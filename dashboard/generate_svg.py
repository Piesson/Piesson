import json
import datetime
import os
from pathlib import Path
from get_weekly_commits import get_weekly_commits

# KST = UTC + 9 hours
KST = datetime.timezone(datetime.timedelta(hours=9))

def generate_dashboard_svg():
    # Load data
    with open('dashboard/data.json', 'r') as f:
        data = json.load(f)

    # Auto-update commits from GitHub GraphQL API (all repos)
    current_commits = get_weekly_commits()
    data['currentWeek']['metrics']['commits'] = current_commits

    # Save updated data back
    with open('dashboard/data.json', 'w') as f:
        json.dump(data, f, indent=2)

    current = data['currentWeek']['metrics']

    # Calculate current week dates (Monday to Sunday) in KST
    today = datetime.datetime.now(KST)
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)

    # Format dates in US format (MM/DD/YYYY)
    week_start = monday.strftime('%m/%d/%Y')
    week_end = sunday.strftime('%m/%d/%Y')

    svg_content = f'''<svg width="520" height="330" xmlns="http://www.w3.org/2000/svg">
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

    <!-- Background -->
    <rect width="520" height="330" fill="url(#bg)" rx="16" stroke="#e2e8f0" stroke-width="1"/>

    <!-- Title -->
    <text x="260" y="30" text-anchor="middle" fill="#0f172a" font-size="22" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
        Moved the needle this week? 📈
    </text>
    <text x="260" y="50" text-anchor="middle" fill="#64748b" font-size="12" font-family="system-ui, -apple-system, sans-serif">
        {week_start} — {week_end}
    </text>
    <text x="260" y="68" text-anchor="middle" fill="#9ca3af" font-size="9" font-family="system-ui, -apple-system, sans-serif">
        updated at {today.strftime('%m/%d/%y')}
    </text>

    <!-- Metrics Grid -->
    <!-- Row 1: Commits, User Talks, Social Posts -->
    <!-- Commits -->
    <g transform="translate(60, 85)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {current['commits']}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            🚀 CODE COMMITS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            Daily goal: 20 commits
        </text>
    </g>

    <!-- User Talks -->
    <g transform="translate(200, 85)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {current['userSessions']}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            💬 USER TALKS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            Daily goal: 1 talk
        </text>
    </g>

    <!-- Social Posts -->
    <g transform="translate(340, 85)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {current['socialContent']['instagram'] + current['socialContent']['tiktok'] + current['socialContent']['hellotalk']}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            📱 SOCIAL POSTS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            IG:{current['socialContent']['instagram']} TT:{current['socialContent']['tiktok']} HT:{current['socialContent']['hellotalk']}
        </text>
    </g>

    <!-- Row 2: Coffee Chats, Workouts, Blog Posts -->
    <!-- Coffee Chats -->
    <g transform="translate(60, 200)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {current['ctoMeetings']}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            ☕ COFFEE CHATS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            Weekly goal: 2 chats
        </text>
    </g>

    <!-- Workouts -->
    <g transform="translate(200, 200)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {current['workouts']['running'] + current['workouts']['gym']}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            🏃 WORKOUTS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            Run:{current['workouts']['running']} Gym:{current['workouts']['gym']}
        </text>
    </g>

    <!-- Blog Posts -->
    <g transform="translate(340, 200)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {current['blogPosts']}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            📝 BLOG POSTS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            AI &amp; Startup content
        </text>
    </g>

</svg>'''

    # Save SVG
    output_path = Path('dashboard/weekly_dashboard.svg')
    output_path.write_text(svg_content)
    print(f"Dashboard generated: {output_path}")

    # Update README with timestamp
    update_readme_dashboard_timestamp(today)

def update_readme_dashboard_timestamp(today):
    """Update README.md Grinding metics section with timestamp"""
    import re
    readme_path = Path('README.md')

    if not readme_path.exists():
        return

    with open(readme_path, 'r') as f:
        content = f.read()

    current_date = today.strftime('%m/%d/%y')
    timestamp_line = f"<sub>updated at {current_date}</sub>"

    # Pattern: # Grinding metics followed by optional timestamp, then <p align="center">
    pattern = r'(# Grinding metics\n\n)(?:<sub>updated at \d{2}/\d{2}/\d{2}</sub>\n\n)?(<p align="center">)'
    replacement = f'\\1{timestamp_line}\n\n\\2'

    content = re.sub(pattern, replacement, content)

    with open(readme_path, 'w') as f:
        f.write(content)

    print(f"✅ Updated Grinding metics timestamp: {current_date}")

if __name__ == "__main__":
    generate_dashboard_svg()