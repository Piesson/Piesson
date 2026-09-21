#!/usr/bin/env python3
"""
generate_progress_chart.py — Running Totals (2026-09-21 redesign).

Two cumulative line charts — pull requests (machine-counted) and social
posts (hand-filed, now the metric that matters most) — each on its own
scale. Four remaining hand-filed measures print as twelve-week totals.

Replaces the dual-axis six-line chart and the sparkline cards.
"""

import json
from datetime import datetime
from pathlib import Path

from metric_totals import grouped_total
from week_utils import iso_week_id

DATA = Path('dashboard/data.json')
OUT = Path('dashboard/progress_sparklines.svg')

PAPER = '#e4e4df'; EDGE = '#cbcbc4'
INK = '#15150f'; INK2 = '#3e3e37'; INK3 = '#575750'
RED = '#a81f16'; RULE = '#a9a9a0'; HAIR = '#c9c9c1'
FILL2 = '#6e6e66'
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "system-ui, -apple-system, sans-serif"

W, H = 1000, 730
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


def line_chart(y0, label, cum, total, sub, color, week_labels, h=120):
    """Cumulative line chart: baseline at y0+h, top at y0."""
    out = []
    out.append(t(L, y0 - 14, label, 21, INK))
    out.append(dotted(L + 280, R - 80, y0 - 15))
    out.append(t(R, y0 - 10, str(total), 56, INK, '700', anchor='end', letter='-0.03em'))
    out.append(t(L, y0 + 46, sub, 13, INK2, family=SANS))

    gy = y0 + h
    out.append(hline(L, R, gy, RULE))
    out.append(hline(L, R, y0 + 16, HAIR))

    n = len(cum)
    mx = max(cum) or 1
    mn = min(cum)
    rng = (mx - mn) or 1
    pts = []
    for i, v in enumerate(cum):
        x = L if n == 1 else L + i * CHART_W / (n - 1)
        yv = gy - 10 - (v - mn) / rng * (h - 24)
        pts.append((x, yv))
    poly = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    out.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>\n')
    lx, ly = pts[-1]
    out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="{RED}"/>\n')
    out.append(t(L + 2, y0 + 4, str(mx), 11, INK3, family=SANS))

    # Axis labels follow the rolling data window instead of a fixed launch range.
    tick_indexes = sorted(range(n - 1, -1, -2))
    for index in tick_indexes:
        x = L if n == 1 else L + index * CHART_W / (n - 1)
        is_last = index == n - 1
        out.append(t(
            x, gy + 18, week_labels[index], 12,
            RED if is_last else INK3,
            '600' if is_last else '400',
            anchor='end' if is_last and n > 1 else 'start',
            family=SANS,
        ))
    return out


def build():
    d = json.loads(DATA.read_text())
    cw = d['currentWeek']
    hist = list(reversed(d['weeklyHistory']))
    hist11 = hist[-11:] if len(hist) >= 11 else hist
    hand_weeks = hist11 + [cw]

    def week_label(entry):
        week_id = entry.get('week')
        if not week_id:
            week_id = iso_week_id(datetime.strptime(entry['startDate'], '%Y-%m-%d'))
        return f"W{int(week_id.split('-W')[1])}"

    week_labels = [week_label(entry) for entry in hand_weeks]

    def week_pr(e):
        return e['metrics'].get('pullRequests', e['metrics'].get('commits', 0))

    def week_soc(e):
        return grouped_total(e['metrics'].get('socialContent', {}))

    pr_now = cw['metrics'].get('pullRequests', cw['metrics'].get('commits', 0))
    soc_now = grouped_total(cw['metrics'].get('socialContent', {}))

    pr_cum, s = [], 0
    for e in hist11:
        s += week_pr(e); pr_cum.append(s)
    s += pr_now; pr_cum.append(s)

    soc_cum, s = [], 0
    for e in hist11:
        s += week_soc(e); soc_cum.append(s)
    s += soc_now; soc_cum.append(s)

    # Twelve-week totals for the remaining hand-filed measures.
    def sum_metric(key):
        return sum(e['metrics'].get(key, 0) for e in hand_weeks)

    wo_tot = sum(grouped_total(e['metrics'].get('workouts', {})) for e in hand_weeks)
    hand = [
        ('Workouts', wo_tot),
        ('Coffee chats', sum_metric('ctoMeetings')),
        ('Talks with users', sum_metric('userSessions')),
        ('Blog posts', sum_metric('blogPosts')),
    ]

    now = datetime.now().strftime('%-d %b %Y')

    out = []
    out.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n')
    out.append(f'<rect width="{W}" height="{H}" fill="{PAPER}" stroke="{EDGE}" stroke-width="1"/>\n')
    out.append(f'<style>text{{font-variant-numeric:tabular-nums;}}</style>\n')

    out.append(t(L, 40, 'PIESSON · RUNNING TOTALS', 12, INK2, '600', family=SANS, letter='0.14em'))
    window_label = f"{week_labels[0]} — {week_labels[-1]}"
    out.append(t(R, 40, window_label, 12, INK2, '600', anchor='end', family=SANS, letter='0.14em'))
    out.append(hline(L, R, 54, INK, 2))

    # chart 1: PR
    out += line_chart(120, 'Pull requests merged', pr_cum, pr_cum[-1],
                      'Counted from GitHub search, twelve weeks.', INK, week_labels)

    # chart 2: Social
    out += line_chart(310, 'Social posts', soc_cum, soc_cum[-1],
                      'Filed by hand, twelve weeks.', FILL2, week_labels)

    # hand rows
    y = 548
    out.append(t(L, y, 'ALSO FILED BY HAND · TWELVE-WEEK TOTALS', 12, INK2, '600', family=SANS, letter='0.14em'))
    out.append(hline(L, R, y + 14, INK))
    col_x = [L, L + 430]
    yy = y + 42
    for i, (name, val) in enumerate(hand):
        cx = col_x[i % 2]
        out.append(t(cx, yy, name, 17, INK))
        out.append(dotted(cx + 160, cx + 386, yy - 5))
        out.append(t(cx + 392, yy, str(val), 21, INK, '700', anchor='end'))
        if i % 2 == 1:
            out.append(hline(cx - 430 if cx == col_x[1] else cx, cx + 430, yy + 16))
            yy += 44

    # colophon
    yc = H - 14
    out.append(hline(L, R, yc - 28, INK))
    out.append(t(L, yc, f'Totals cover {window_label}, the latest twelve weeks.', 13, INK2, family=SANS))
    out.append(t(R, yc, f'as of {now}', 13, INK2, anchor='end', style='italic'))

    out.append('</svg>\n')
    OUT.write_text(''.join(out))
    print(f'wrote {OUT}')


def generate_progress_chart():
    """Backward-compat wrapper."""
    build()


if __name__ == '__main__':
    build()
