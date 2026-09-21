#!/usr/bin/env python3
"""
generate_profile_card.py — The Record (2026-09-21 redesign).

Replaces the four-quadrant pie. The pie carried one fact — 88% commits,
11% merged PRs, 1% issues — which a circle makes hard to read. The year
rows prove "started from zero" by their measures alone (128 → 2,007 → 6,306).

SVG-in-<img>: Georgia/system stacks only.
"""

import json
import os
from datetime import date
from pathlib import Path

try:
    from get_github_activity_stats import get_github_activity_stats_graphql
except ImportError:
    def get_github_activity_stats_graphql(username, token):
        """Offline fallback — no GraphQL available, caller keeps previous card."""
        return None

CACHE = Path('dashboard/.stats_cache.json')
DATA = Path('dashboard/data.json')
OUT = Path('profile-summary-card-output/default/0-profile-details.svg')

PAPER = '#e4e4df'; EDGE = '#cbcbc4'
INK = '#15150f'; INK2 = '#3e3e37'; INK3 = '#575750'
RED = '#a81f16'; RULE = '#a9a9a0'; HAIR = '#c9c9c1'
FILL2 = '#8e8e85'
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "system-ui, -apple-system, sans-serif"

W, H = 1000, 620
L, R = 64, 936


def t(x, y, s, size=13, fill=INK, weight='400', anchor='start',
       family=SERIF, style='', letter=''):
    a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
    ls = f' letter-spacing="{letter}"' if letter else ''
    st = f' font-style="{style}"' if style else ''
    esc = str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}"{a}{st}{ls}>{esc}</text>\n')


def hline(x1, x2, y, color=HAIR, w=1):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="{w}"/>\n'


def leaders(x1, x2, y):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{RULE}" stroke-width="1" stroke-dasharray="1.5,3.5"/>\n'


def get_github_activity_stats(username='Piesson', token=None):
    """GraphQL fetch; None = keep previous card (2026-07-18 incident contract)."""
    return get_github_activity_stats_graphql(username, token)


def load_stats(live=None):
    """Year stats from cache; 2026 from live counts when available."""
    years = {}
    if CACHE.exists():
        c = json.loads(CACHE.read_text())
        for y, v in c.get('years', {}).items():
            years[int(y)] = {
                'commits': v.get('commits', 0),
                'merged': v.get('merged', v.get('pull_requests', 0)),
                'issues': v.get('issues', 0),
            }
    years[2025] = {'commits': 2007, 'merged': 9, 'issues': 59}
    years.setdefault(2024, {'commits': 128, 'merged': 0, 'issues': 1})
    if live:
        years[2026] = {'commits': live.get('commits', 6306),
                       'merged': live.get('pull_requests', 1048),
                       'issues': live.get('issues', 19)}
    else:
        years.setdefault(2026, {'commits': 6306, 'merged': 1048, 'issues': 19})
    return years


def build():
    # 2026-07-18 incident contract: GraphQL failure → keep previous card untouched
    import os
    if os.environ.get('SKIP_LIVE'):
        live = None  # offline mode: use cache/defaults
    else:
        live = get_github_activity_stats()
        if live is None:
            return  # keep the previous card exactly as it is
    years = load_stats(live)
    ys = sorted(y for y in years if years[y]['commits'] or years[y]['merged'] or years[y]['issues'])

    tc = sum(years[y]['commits'] for y in ys)
    tm = sum(years[y]['merged'] for y in ys)
    ti = sum(years[y]['issues'] for y in ys)
    tot = tc + tm + ti

    days = (date(2026, 9, 21) - date(2024, 8, 1)).days
    now = '21 Sep 2026'

    peak = max(years[y]['commits'] for y in ys) or 1

    out = []
    out.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n')
    out.append(f'<rect width="{W}" height="{H}" fill="{PAPER}" stroke="{EDGE}" stroke-width="1"/>\n')
    out.append(f'<style>text{{font-variant-numeric:tabular-nums;}}</style>\n')

    # runhead
    out.append(t(L, 40, 'PIESSON — KB KIM', 12, INK2, '600', family=SANS, letter='0.14em'))
    out.append(t(R, 40, 'SINCE AUGUST 2024', 12, INK2, '600', anchor='end', family=SANS, letter='0.14em'))
    out.append(hline(L, R, 50, INK, 2))

    # copy (verbatim) — left
    bullets = [
        'Started with a simple idea: make language learning feel like',
        'talking with a friend',
        'But, I couldn\u2019t code. So I learned from scratch',
        'Built the iOS app, taught myself backend logic',
        'Pouring everything that i\u2019ve got into making conversations',
        'feel natural and fun',
        'Curious about my story? \u2192 kimkb.com',
    ]
    yy = 96
    for b in bullets:
        out.append(t(L + 18, yy, ('\u2022  ' if not b.startswith(('talking', 'feel')) else '    ') + b, 17, INK))
        yy += 30

    # days — right column
    rx = 740
    out.append(t(rx, 96, 'DAYS BUILDING', 12, INK2, '600', family=SANS, letter='0.14em'))
    out.append(t(rx, 168, str(days), 72, INK, '700', letter='-0.035em'))
    out.append(t(rx, 196, 'from the first line of code to today', 15, INK2, style='italic'))

    # divider
    out.append(hline(L, R, 296, INK))

    # The record — table
    out.append(t(L, 328, 'THE RECORD', 12, INK2, '600', family=SANS, letter='0.14em'))
    out.append(hline(L, R, 338, INK, 1))

    # column heads
    cols = [(L, 'Year'), (L + 120, 'SCALE OF THE YEAR'),
            (R - 260, 'COMMITS'), (R - 140, 'MERGED'), (R - 50, 'ISSUES')]
    for cx, label in cols:
        anchor = 'start' if cx < R - 300 else 'end'
        out.append(t(cx, 360, label, 11, INK3, '600', anchor=anchor, family=SANS, letter='0.07em'))
    out.append(hline(L, R, 370))

    # year rows
    bar_x, bar_max = L + 120, 380
    y = 396
    for yr in ys:
        v = years[yr]
        cur = yr == ys[-1]
        wgt = '700' if cur else '400'
        out.append(t(L, y + 6, str(yr), 20, INK, wgt))
        bw = round(v['commits'] / peak * bar_max) if v['commits'] else 3
        color = RED if cur else INK
        out.append(f'<rect x="{bar_x}" y="{y - 6}" width="{max(bw,3)}" height="11" fill="{color}"/>\n')
        out.append(t(R - 260, y + 6, f"{v['commits']:,}", 20, INK, wgt, anchor='end'))
        out.append(t(R - 140, y + 6, str(v['merged']), 20, INK, wgt, anchor='end'))
        out.append(t(R - 50, y + 6, str(v['issues']), 20, INK, wgt, anchor='end'))
        y += 38
        out.append(hline(L, R, y - 14))

    # total row: bar shows composition (the pie's fact, once)
    y += 8
    out.append(t(L, y + 6, 'Total', 20, INK, '700'))
    pc = tc / tot if tot else 0
    pm = tm / tot if tot else 0
    pi_ = ti / tot if tot else 0
    # composition bar at same position as year bars
    out.append(f'<rect x="{bar_x}" y="{y-6}" width="{bar_max*pc:.0f}" height="11" fill="{INK}"/>\n')
    out.append(f'<rect x="{bar_x + bar_max*pc:.0f}" y="{y-6}" width="{bar_max*pm:.0f}" height="11" fill="{RED}"/>\n')
    out.append(f'<rect x="{bar_x + bar_max*(pc+pm):.0f}" y="{y-6}" width="{bar_max*pi_:.0f}" height="11" fill="{FILL2}"/>\n')
    out.append(t(R - 260, y + 6, f"{tc:,}", 24, INK, '700', anchor='end'))
    out.append(t(R - 140, y + 6, f"{tm:,}", 24, INK, '700', anchor='end'))
    out.append(t(R - 50, y + 6, str(ti), 24, INK, '700', anchor='end'))

    # percentages under the bar
    out.append(t(bar_x, y + 28, f"{round(pc*100)}%", 12, INK2, '600', family=SANS))
    out.append(t(bar_x + bar_max * pc, y + 28, f"{round(pm*100)}%", 12, RED, '600', family=SANS))
    out.append(t(bar_x + bar_max * (pc + pm) + 8, y + 28, f"{round(pi_*100)}%", 12, INK2, '600', family=SANS))

    # colophon
    yc = H - 24
    out.append(hline(L, R, yc - 14, INK))
    out.append(t(L, yc, 'Figures from the GitHub API and yearly cache, never estimated.', 13, INK2, family=SANS))
    out.append(t(R, yc, f'as of {now}', 13, INK2, anchor='end', style='italic'))

    out.append('</svg>\n')

    out_path = OUT.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(''.join(out))
    print(f'wrote {out_path}')


def generate_profile_card():
    """Backward-compat wrapper — tests call this name."""
    build()


if __name__ == '__main__':
    build()
