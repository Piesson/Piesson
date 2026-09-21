#!/usr/bin/env python3
"""
generate_svg.py — Weekly Galley (2026-09-21 redesign).

Design: proof-shop galley. Cool proof stock, Caslon-register serif (Georgia),
Archivo-register sans (system-ui), dotted leaders, hairline rules.
The lead figure (PR merged) is the week's subject; five hand-filed rows
sit in two columns below; twelve weeks of two series (PR + social) close.

SVG-in-<img> constraint: no web fonts. Georgia/system stacks only.
"""

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))
DATA = Path('dashboard/data.json')
OUT = Path('dashboard/weekly_dashboard.svg')

# tokens (mirror .impeccable/mocks/a-galley.html)
PAPER = '#e4e4df'; EDGE = '#cbcbc4'
INK = '#15150f'; INK2 = '#3e3e37'; INK3 = '#575750'
RED = '#a81f16'; RULE = '#a9a9a0'; HAIR = '#c9c9c1'
FILL2 = '#6e6e66'
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "system-ui, -apple-system, sans-serif"

W, H = 1000, 780
L, R = 64, 936


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def t(x, y, s, size=13, fill=INK, weight='400', anchor='start',
       family=SERIF, style='', letter=''):
    a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
    ls = f' letter-spacing="{letter}"' if letter else ''
    st = f' font-style="{style}"' if style else ''
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}"{a}{st}{ls}>{esc(s)}</text>\n')


def leaders(x1, x2, y):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{RULE}" stroke-width="1" stroke-dasharray="1.5,3.5"/>\n'


def hline(x1, x2, y, color=HAIR, w=1):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="{w}"/>\n'


def load():
    return json.loads(DATA.read_text())


def goal_for(key):
    goals = {'pullRequests': 60, 'userSessions': 7, 'social': 7,
             'workouts': 7, 'coffee': 2, 'blog': 1}
    return goals.get(key, 7)


def generate_dashboard_svg():
    """Backward-compat wrapper — tests and workflows call this name."""
    build()


def build():
    d = load()
    # Auto-refresh commits from GitHub (regression guard: None = keep previous,
    # never write 0 — 2026-05 incident contract, tests/test_caller_fallbacks.py)
    import get_weekly_commits as _gwc
    fresh = _gwc.get_weekly_commits()
    if fresh is not None:
        d['currentWeek']['metrics']['commits'] = fresh
        json.dump(d, open(DATA, 'w'), indent=2, ensure_ascii=False)

    cw = d['currentWeek']
    m = cw['metrics']
    hist = list(reversed(d['weeklyHistory']))  # oldest first

    # ---- data ----
    pr_now = m.get('pullRequests')  # no commits fallback — the label says PRs
    social = m.get('socialContent', {})
    social_now = sum(v for v in social.values() if isinstance(v, int))
    workouts = m.get('workouts', {})
    wo_now = sum(v for v in workouts.values() if isinstance(v, int))

    # weekly PR + social series (12 weeks incl current)
    def week_pr(entry):
        return entry['metrics'].get('pullRequests', 0)

    def week_soc(entry):
        s = entry['metrics'].get('socialContent', {})
        return sum(v for v in s.values() if isinstance(v, int))

    hist11 = hist[-11:] if len(hist) >= 11 else hist
    pr_series = [week_pr(e) for e in hist11] + [pr_now]
    soc_series = [week_soc(e) for e in hist11] + [social_now]
    weeks = []
    for e in hist11:
        dt = datetime.fromisoformat(e['startDate'])
        weeks.append(f"W{dt.isocalendar()[1]}")
    dt = datetime.fromisoformat(cw['startDate'])
    weeks.append(f"W{dt.isocalendar()[1]}")

    # period label
    s = datetime.fromisoformat(cw['startDate'])
    e = datetime.fromisoformat(cw['endDate'])
    period = f"{s.strftime('%B %-d')} – {e.strftime('%-d, %Y')}"
    now = datetime.now(KST).strftime('%-d %b %Y')

    # ---- svg ----
    out = []
    out.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n')
    out.append(f'<rect width="{W}" height="{H}" rx="0" fill="{PAPER}" stroke="{EDGE}" stroke-width="1"/>\n')
    out.append(f'<style>text{{font-variant-numeric:tabular-nums;}}</style>\n')

    # runhead
    out.append(t(L, 40, 'PIESSON · WEEKLY GALLEY', 12, INK2, '600', family=SANS, letter='0.14em'))
    out.append(t(R, 40, weeks[-1], 12, INK2, '600', anchor='end', family=SANS, letter='0.14em'))
    out.append(hline(L, R, 50, INK, 2))
    out.append(t(W / 2, 76, period, 16, INK2, style='italic'))

    # lead
    out.append(t(L, 136, 'Pull requests merged', 24, INK))
    out.append(leaders(L + 300, R - 110, 130))
    out.append(t(R, 136, str(pr_now) if pr_now is not None else '\u2014', 62, INK, '700', anchor='end', letter='-0.03em'))
    pct = round(pr_now / goal_for('pullRequests') * 100) if pr_now else 0
    pr_label = f'Counted from GitHub search \u00b7 goal {goal_for("pullRequests")} \u00b7 {pct}% of target' if pr_now is not None else 'Counted from GitHub search'
    out.append(t(L, 158, f'Counted from GitHub search · goal {goal_for("pullRequests")} · {pct}% of target',
                 13, INK2, family=SANS))
    out.append(hline(L, R, 176, INK))

    # hand-filed rows (2 columns x 3)
    hand = [
        ('Talks with users', m.get('userSessions', 0), 7),
        ('Social posts', social_now, 7),
        ('Workouts', wo_now, 7),
        ('Coffee chats', m.get('ctoMeetings', 0), 2),
        ('Blog posts', m.get('blogPosts', 0), 1),
    ]
    col_x = [L, L + 430]
    y = 210
    for i, (name, val, goal) in enumerate(hand):
        cx = col_x[i % 2]
        out.append(t(cx, y, name, 17, INK))
        out.append(leaders(cx + 160, col_x[i % 2] + 390, y - 5))
        out.append(t(cx + 396, y, str(val), 20, INK, '700', anchor='end'))
        out.append(t(cx + 404, y, f'/ {goal}', 13, INK3, family=SANS))
        # every slug gets its hairline, both columns, symmetric
        out.append(hline(cx, cx + 430, y + 12))
        if i % 2 == 1:
            y += 42
    if len(hand) % 2 == 1:
        y += 42

    # twelve weeks — two series
    ybase = y + 50
    out.append(t(L, ybase, 'TWELVE WEEKS', 12, INK2, '600', family=SANS, letter='0.14em'))
    out.append(hline(L, R, ybase + 10, INK))

    def bar_series(y0, label, vals, peak, color, val_size=19):
        out.append(t(L, y0, label, 12.5, INK2, '600', family=SANS))
        out.append(t(R, y0, f'peak {peak}', 12, INK3, family=SANS, anchor='end'))
        gy = y0 + 14
        out.append(hline(L, R, gy, RULE))
        n = len(vals)
        slot = (R - L) / n
        max_h = 64
        for i, v in enumerate(vals):
            cx = L + slot * i + slot / 2
            h = round(v / peak * max_h) if (v and peak) else 0
            if h > 0:
                bw = min(slot * 0.6, 42)
                bx = cx - bw / 2
                c = RED if i == n - 1 else color
                out.append(f'<rect x="{bx:.1f}" y="{gy - h}" width="{bw:.1f}" height="{h}" fill="{c}"/>\n')
            out.append(t(cx, gy + 18, str(v), val_size, INK if i < n - 1 else RED,
                         '400' if i < n - 1 else '700', anchor='middle'))
            out.append(t(cx, gy + 34, weeks[i], 11.5, INK3 if i < n - 1 else RED,
                         '400' if i < n - 1 else '600', anchor='middle', family=SANS, letter='0.06em'))

    pr_peak = max(pr_series) or 1
    soc_peak = max(soc_series) or 1
    bar_series(ybase + 30, 'Pull requests merged', pr_series, pr_peak, INK)
    bar_series(ybase + 30 + 108, 'Social posts', soc_series, soc_peak, FILL2, 15)

    # colophon
    yc = H - 40
    out.append(hline(L, R, yc - 16, INK))
    out.append(t(L, yc, 'Figures are counted, never estimated.', 13, INK2, family=SANS))
    out.append(t(R, yc, f'as of {now}', 13, INK2, anchor='end', style='italic'))

    out.append('</svg>\n')
    OUT.write_text(''.join(out))
    print(f'wrote {OUT}')


if __name__ == '__main__':
    build()
