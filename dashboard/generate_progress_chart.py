#!/usr/bin/env python3
"""
generate_progress_chart.py — Running Totals (2026-09-21 redesign).

Two cumulative line charts — pull requests (machine-counted) and social
posts (hand-filed, now the metric that matters most) — each on its own
scale. Four remaining hand-filed measures print as figures.

Replaces the dual-axis six-line chart and the sparkline cards.
"""

import json
from datetime import datetime
from pathlib import Path

DATA = Path('dashboard/data.json')
OUT = Path('dashboard/progress_sparklines.svg')

PAPER = '#e4e4df'; EDGE = '#cbcbc4'
INK = '#15150f'; INK2 = '#3e3e37'; INK3 = '#575750'
RED = '#a81f16'; RULE = '#a9a9a0'; HAIR = '#c9c9c1'
FILL2 = '#6e6e66'
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "system-ui, -apple-system, sans-serif"

W, H = 1000, 700
L, R = 64, 936
CHART_W = R - L


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


def dotted(x1, x2, y):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{RULE}" stroke-width="1" stroke-dasharray="1.5,3.5"/>\n'


def line_chart(y0, label, cum, total, sub, color, h=120):
    """Cumulative line chart: baseline at y0+h, top at y0."""
    out = []
    out.append(t(L, y0 - 14, label, 21, INK))
    out.append(dotted(L + 280, R - 80, y0 - 20))
    out.append(t(R, y0 - 10, str(total), 56, INK, '700', anchor='end', letter='-0.03em'))
    out.append(t(L, y0 + 10, sub, 13, INK2, family=SANS))

    gy = y0 + h
    out.append(hline(L, R, gy, RULE))
    out.append(hline(L, R, y0 + 8, HAIR))

    n = len(cum)
    mx = max(cum) or 1
    mn = min(cum)
    rng = (mx - mn) or 1
    pts = []
    for i, v in enumerate(cum):
        x = L + i * CHART_W / (n - 1)
        yv = gy - 10 - (v - mn) / rng * (h - 24)
        pts.append((x, yv))
    poly = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    out.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>\n')
    lx, ly = pts[-1]
    out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="{RED}"/>\n')
    out.append(t(L + 2, y0 + 4, str(mx), 11, INK3, family=SANS))

    # axis
    out.append(t(L, gy + 18, 'W27', 12, INK3, family=SANS))
    for frac, lbl in [(0.2, 'W29'), (0.4, 'W31'), (0.6, 'W33'), (0.8, 'W35')]:
        out.append(t(L + CHART_W * frac, gy + 18, lbl, 12, INK3, family=SANS))
    out.append(t(R, gy + 18, 'W38', 12, RED, '600', anchor='end', family=SANS))
    return out


def build():
    d = json.loads(DATA.read_text())
    cw = d['currentWeek']
    hist = list(reversed(d['weeklyHistory']))
    hist11 = hist[-11:] if len(hist) >= 11 else hist

    def week_pr(e):
        return e['metrics'].get('pullRequests', e['metrics'].get('commits', 0))

    def week_soc(e):
        s = e['metrics'].get('socialContent', {})
        return sum(v for v in s.values() if isinstance(v, int))

    pr_now = cw['metrics'].get('pullRequests', cw['metrics'].get('commits', 0))
    soc_now = sum(v for v in cw['metrics'].get('socialContent', {}).values() if isinstance(v, int))

    pr_cum, s = [], 0
    for e in hist11:
        s += week_pr(e); pr_cum.append(s)
    s += pr_now; pr_cum.append(s)

    soc_cum, s = [], 0
    for e in hist11:
        s += week_soc(e); soc_cum.append(s)
    s += soc_now; soc_cum.append(s)

    # hand totals
    m = cw['metrics']
    wo = m.get('workouts', {})
    wo_tot = sum(v for v in wo.values() if isinstance(v, int))
    hand = [
        ('Workouts', wo_tot),
        ('Coffee chats', m.get('ctoMeetings', 0)),
        ('Talks with users', m.get('userSessions', 0)),
        ('Blog posts', m.get('blogPosts', 0)),
    ]

    now = datetime.now().strftime('%-d %b %Y')

    out = []
    out.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n')
    out.append(f'<rect width="{W}" height="{H}" fill="{PAPER}" stroke="{EDGE}" stroke-width="1"/>\n')
    out.append(f'<style>text{{font-variant-numeric:tabular-nums;}}</style>\n')

    out.append(t(L, 40, 'PIESSON · RUNNING TOTALS', 12, INK2, '600', family=SANS, letter='0.14em'))
    out.append(t(R, 40, 'W27 — W38', 12, INK2, '600', anchor='end', family=SANS, letter='0.14em'))
    out.append(hline(L, R, 50, INK, 2))

    # chart 1: PR
    out += line_chart(90, 'Pull requests merged', pr_cum, pr_cum[-1],
                      'Counted from GitHub search, twelve weeks.', INK)

    # chart 2: Social
    out += line_chart(290, 'Social posts', soc_cum, soc_cum[-1],
                      'Filed by hand, twelve weeks.', FILL2)

    # hand rows
    y = 520
    out.append(t(L, y, 'ALSO FILED BY HAND', 12, INK2, '600', family=SANS, letter='0.14em'))
    out.append(hline(L, R, y + 10, INK))
    col_x = [L, L + 430]
    yy = y + 42
    for i, (name, val) in enumerate(hand):
        cx = col_x[i % 2]
        out.append(t(cx, yy, name, 17, INK))
        out.append(dotted(cx + 160, cx + 386, yy - 5))
        out.append(t(cx + 392, yy, str(val), 21, INK, '700', anchor='end'))
        if i % 2 == 1:
            out.append(hline(cx - 430 if cx == col_x[1] else cx, cx + 430, yy + 12))
            yy += 38

    # note
    out.append(t(L, yy + 24, 'The top figure is counted by the machine; the rest are entered by hand each week,',
                 13, INK2, family=SANS))
    out.append(t(L, yy + 42, 'which is the point of entering them: the number is the review, not the report.',
                 13, INK2, family=SANS))

    # colophon
    yc = H - 24
    out.append(hline(L, R, yc - 14, INK))
    out.append(t(L, yc, 'Totals run from week 27 and reset with the quarter.', 13, INK2, family=SANS))
    out.append(t(R, yc, f'as of {now}', 13, INK2, anchor='end', style='italic'))

    out.append('</svg>\n')
    OUT.write_text(''.join(out))
    print(f'wrote {OUT}')


def generate_progress_chart():
    """Backward-compat wrapper."""
    build()


if __name__ == '__main__':
    build()
