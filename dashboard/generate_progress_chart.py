#!/usr/bin/env python3
"""
Generate progress charts for Piesson GitHub profile README.

Part A: QuickChart.io dual Y-axis URL (combined chart)
Part B: Self-generated SVG sparklines (individual metric detail)
"""

import json
import math
from pathlib import Path
from urllib.parse import quote


def load_weekly_data():
    """Load and process weekly history data into cumulative series."""
    data_file = Path('dashboard/data.json')

    if not data_file.exists():
        print("data.json not found")
        return None

    with open(data_file, 'r') as f:
        data = json.load(f)

    history = data.get('weeklyHistory', [])

    if not history:
        print("No weekly history found")
        return None

    history_sorted = sorted(history, key=lambda x: x['week'])

    weeks = []
    commits = []
    user_talks = []
    social_posts = []
    coffee_chats = []
    workouts = []
    blog_posts = []

    cumulative_commits = 0
    cumulative_talks = 0
    cumulative_social = 0
    cumulative_chats = 0
    cumulative_workouts = 0
    cumulative_posts = 0

    for entry in history_sorted:
        week_id = entry['week']
        week_num = week_id.split('-W')[1]
        weeks.append(f"W{week_num}")

        metrics = entry['metrics']

        social = metrics.get('socialContent', {})
        if isinstance(social, dict):
            total_social = social.get('instagram', 0) + social.get('tiktok', 0) + social.get('hellotalk', 0)
        else:
            total_social = social

        workouts_data = metrics.get('workouts', {})
        if isinstance(workouts_data, dict):
            total_workouts = workouts_data.get('running', 0) + workouts_data.get('gym', 0)
        else:
            total_workouts = workouts_data

        cumulative_commits += metrics.get('commits', 0)
        cumulative_talks += metrics.get('userSessions', 0)
        cumulative_social += total_social
        cumulative_chats += metrics.get('ctoMeetings', 0)
        cumulative_workouts += total_workouts
        cumulative_posts += metrics.get('blogPosts', 0)

        commits.append(cumulative_commits)
        user_talks.append(cumulative_talks)
        social_posts.append(cumulative_social)
        coffee_chats.append(cumulative_chats)
        workouts.append(cumulative_workouts)
        blog_posts.append(cumulative_posts)

    return {
        'weeks': weeks,
        'commits': commits,
        'user_talks': user_talks,
        'social_posts': social_posts,
        'coffee_chats': coffee_chats,
        'workouts': workouts,
        'blog_posts': blog_posts
    }


# ---------------------------------------------------------------------------
# Part A: QuickChart.io dual Y-axis combined chart
# ---------------------------------------------------------------------------

def generate_chart_url(data):
    """Generate QuickChart.io URL with dual Y-axis.

    Left axis (y1): Code Commits (large scale)
    Right axis (y2): Other 5 metrics (smaller scale)
    """
    if not data:
        return None

    config = {
        "type": "line",
        "data": {
            "labels": data['weeks'],
            "datasets": [
                {
                    "label": "Code Commits",
                    "data": data['commits'],
                    "borderColor": "#FF6384",
                    "backgroundColor": "rgba(255,99,132,0.08)",
                    "fill": False,
                    "yAxisID": "y1",
                    "borderWidth": 2.5,
                    "pointRadius": 3,
                    "tension": 0.3
                },
                {
                    "label": "User Talks",
                    "data": data['user_talks'],
                    "borderColor": "#36A2EB",
                    "backgroundColor": "rgba(54,162,235,0.08)",
                    "fill": False,
                    "yAxisID": "y2",
                    "borderWidth": 2.5,
                    "pointRadius": 3,
                    "tension": 0.3
                },
                {
                    "label": "Social Posts",
                    "data": data['social_posts'],
                    "borderColor": "#E6B800",
                    "backgroundColor": "rgba(230,184,0,0.08)",
                    "fill": False,
                    "yAxisID": "y2",
                    "borderWidth": 2.5,
                    "pointRadius": 3,
                    "tension": 0.3
                },
                {
                    "label": "Coffee Chats",
                    "data": data['coffee_chats'],
                    "borderColor": "#4BC0C0",
                    "backgroundColor": "rgba(75,192,192,0.08)",
                    "fill": False,
                    "yAxisID": "y2",
                    "borderWidth": 2.5,
                    "pointRadius": 3,
                    "tension": 0.3
                },
                {
                    "label": "Workouts",
                    "data": data['workouts'],
                    "borderColor": "#9966FF",
                    "backgroundColor": "rgba(153,102,255,0.08)",
                    "fill": False,
                    "yAxisID": "y2",
                    "borderWidth": 2.5,
                    "pointRadius": 3,
                    "tension": 0.3
                },
                {
                    "label": "Blog Posts",
                    "data": data['blog_posts'],
                    "borderColor": "#FF9F40",
                    "backgroundColor": "rgba(255,159,64,0.08)",
                    "fill": False,
                    "yAxisID": "y2",
                    "borderWidth": 2.5,
                    "pointRadius": 3,
                    "tension": 0.3
                }
            ]
        },
        "options": {
            "responsive": False,
            "title": {
                "display": True,
                "text": "Progress Tracker",
                "fontSize": 16
            },
            "legend": {
                "position": "right",
                "labels": {"fontSize": 11, "padding": 12}
            },
            "scales": {
                "yAxes": [
                    {
                        "id": "y1",
                        "position": "left",
                        "scaleLabel": {
                            "display": True,
                            "labelString": "Commits",
                            "fontStyle": "bold"
                        },
                        "ticks": {"beginAtZero": True}
                    },
                    {
                        "id": "y2",
                        "position": "right",
                        "scaleLabel": {
                            "display": True,
                            "labelString": "Other Metrics",
                            "fontStyle": "bold"
                        },
                        "gridLines": {"drawOnChartArea": False},
                        "ticks": {"beginAtZero": True}
                    }
                ]
            },
            "plugins": {
                "datalabels": {
                    "display": "auto",
                    "anchor": "end",
                    "align": "top",
                    "font": {"size": 9},
                    "formatter": "Math.round"
                }
            }
        }
    }

    config_json = json.dumps(config, separators=(',', ':'))
    url = f"https://quickchart.io/chart?c={quote(config_json)}&w=900&h=450&bkg=white"
    return url


# ---------------------------------------------------------------------------
# Part B: Self-generated SVG sparklines
# ---------------------------------------------------------------------------

# Metric definitions: (name, emoji, data_key, color)
METRICS = [
    ('Code Commits', '\U0001f680', 'commits', '#FF6384'),
    ('User Talks', '\U0001f4ac', 'user_talks', '#36A2EB'),
    ('Social Posts', '\U0001f4f1', 'social_posts', '#E6B800'),
    ('Coffee Chats', '\u2615', 'coffee_chats', '#4BC0C0'),
    ('Workouts', '\U0001f3c3', 'workouts', '#9966FF'),
    ('Blog Posts', '\U0001f4dd', 'blog_posts', '#FF9F40'),
]

# SVG layout constants
SVG_WIDTH = 800
SVG_HEIGHT = 440
CARD_W = 236
CARD_H = 192
PADDING = 30
GAP = 16
CHART_X = 30
CHART_Y = 36
CHART_W = CARD_W - 40   # 196
CHART_H = CARD_H - 72   # 120

# Card positions: 3x2 grid
CARD_POSITIONS = [
    (PADDING, 20),
    (PADDING + CARD_W + GAP, 20),
    (PADDING + 2 * (CARD_W + GAP), 20),
    (PADDING, 20 + CARD_H + GAP),
    (PADDING + CARD_W + GAP, 20 + CARD_H + GAP),
    (PADDING + 2 * (CARD_W + GAP), 20 + CARD_H + GAP),
]


def _scale_points(values, chart_width, chart_height):
    """Scale data values to SVG coordinates within chart area.

    Returns (points_list, max_value_used_for_scaling).
    """
    n = len(values)
    if n == 0:
        return [], 1

    raw_max = max(values)
    max_val = raw_max * 1.1 if raw_max > 0 else 1

    points = []
    for i, val in enumerate(values):
        x = (i / max(n - 1, 1)) * chart_width
        y = chart_height - (val / max_val) * chart_height
        points.append((round(x, 1), round(y, 1)))
    return points, max_val


def _render_sparkline_card(name, emoji, values, weeks, color, card_w, card_h):
    """Render one mini sparkline card as SVG group content."""
    final_val = values[-1] if values else 0
    points, max_val = _scale_points(values, CHART_W, CHART_H)

    # Polyline points string
    polyline_pts = ' '.join(f'{CHART_X + x},{CHART_Y + y}' for x, y in points)

    # Polygon for area fill (close along bottom edge)
    polygon_pts = polyline_pts
    if points:
        polygon_pts += f' {CHART_X + points[-1][0]},{CHART_Y + CHART_H}'
        polygon_pts += f' {CHART_X + points[0][0]},{CHART_Y + CHART_H}'

    # Y-axis tick values: 0, mid, max
    raw_max = max(values) if values and max(values) > 0 else 0
    if raw_max > 0:
        mid_val = raw_max // 2
        y_ticks = [
            (0, CHART_Y + CHART_H),
            (mid_val, CHART_Y + CHART_H - (mid_val / max_val) * CHART_H),
            (raw_max, CHART_Y + CHART_H - (raw_max / max_val) * CHART_H),
        ]
    else:
        y_ticks = [(0, CHART_Y + CHART_H)]

    # Grid lines (3 horizontal dashed)
    grid_ys = [CHART_Y, CHART_Y + CHART_H / 2, CHART_Y + CHART_H]

    # Last data point dot
    last_dot = ''
    if points:
        lx, ly = points[-1]
        last_dot = f'<circle cx="{CHART_X + lx}" cy="{CHART_Y + ly}" r="3.5" fill="{color}" />'

    # X-axis labels: first and last week
    first_week = weeks[0] if weeks else ''
    last_week = weeks[-1] if len(weeks) > 1 else ''

    svg = f'''
    <rect width="{card_w}" height="{card_h}" fill="url(#cardBg)" rx="12"
          filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>

    <!-- Title -->
    <text x="12" y="22" fill="#1f2937" font-size="11" font-weight="700"
          font-family="system-ui, -apple-system, sans-serif">
        {emoji} {name}
    </text>

    <!-- Final value badge -->
    <text x="{card_w - 12}" y="22" fill="{color}" font-size="12" font-weight="700"
          font-family="system-ui, -apple-system, sans-serif" text-anchor="end">
        {final_val:,}
    </text>

    <!-- Grid lines -->'''

    for gy in grid_ys:
        svg += f'''
    <line x1="{CHART_X}" y1="{round(gy, 1)}" x2="{CHART_X + CHART_W}" y2="{round(gy, 1)}"
          stroke="#e2e8f0" stroke-width="0.5" stroke-dasharray="4,3" />'''

    svg += f'''

    <!-- Y-axis ticks -->'''
    for val, y_pos in y_ticks:
        svg += f'''
    <text x="{CHART_X - 4}" y="{round(y_pos + 3, 1)}" fill="#9ca3af" font-size="8"
          font-family="Monaco, monospace" text-anchor="end">{val}</text>'''

    svg += f'''

    <!-- Area fill -->
    <polygon points="{polygon_pts}" fill="{color}" opacity="0.08" />

    <!-- Sparkline -->
    <polyline points="{polyline_pts}" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />

    <!-- Last point dot -->
    {last_dot}

    <!-- X-axis labels -->
    <text x="{CHART_X}" y="{CHART_Y + CHART_H + 14}" fill="#9ca3af" font-size="8"
          font-family="system-ui, -apple-system, sans-serif">{first_week}</text>
    <text x="{CHART_X + CHART_W}" y="{CHART_Y + CHART_H + 14}" fill="#9ca3af" font-size="8"
          font-family="system-ui, -apple-system, sans-serif" text-anchor="end">{last_week}</text>
    '''

    return svg


def generate_sparklines_svg(data):
    """Generate a self-contained SVG with 6 mini sparkline charts in a 3x2 grid."""
    if not data:
        return None

    cards_svg = ''
    for i, (name, emoji, data_key, color) in enumerate(METRICS):
        x, y = CARD_POSITIONS[i]
        card_content = _render_sparkline_card(
            name, emoji, data[data_key], data['weeks'], color, CARD_W, CARD_H
        )
        cards_svg += f'  <g transform="translate({x},{y})">{card_content}</g>\n'

    svg = f'''<svg width="{SVG_WIDTH}" height="{SVG_HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#f8fafc;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#f1f5f9;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="0" dy="2" stdDeviation="8" flood-color="#000000" flood-opacity="0.1"/>
    </filter>
  </defs>

  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="url(#bg)" rx="16"
        stroke="#e2e8f0" stroke-width="1"/>

{cards_svg}</svg>'''

    return svg


def save_sparklines_svg(data):
    """Generate and save the sparklines SVG to disk."""
    svg_content = generate_sparklines_svg(data)
    if svg_content is None:
        return None
    output_path = Path('dashboard/progress_sparklines.svg')
    output_path.write_text(svg_content)
    return str(output_path)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating progress charts...\n")

    data = load_weekly_data()

    if data:
        combined_url = generate_chart_url(data)
        print("Combined Chart URL (QuickChart.io dual Y-axis):")
        print(combined_url)
        print(f"\nURL length: {len(combined_url)} chars")
        print()

        svg_path = save_sparklines_svg(data)
        print(f"Sparklines SVG saved: {svg_path}")
        print("\nDone!")
    else:
        print("Failed to generate charts")
        exit(1)
