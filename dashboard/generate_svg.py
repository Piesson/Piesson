import json
import datetime
import os
from pathlib import Path
from get_weekly_commits import get_weekly_commits

# KST = UTC + 9 hours
KST = datetime.timezone(datetime.timedelta(hours=9))

def get_trend_indicator(current, last_week_value):
    """Calculate trend arrow and percentage change"""
    if last_week_value is None or last_week_value == 0:
        return "", ""

    diff = current - last_week_value
    pct = int((diff / last_week_value) * 100)

    if diff > 0:
        arrow = "▲"
        color = "#10b981"  # green
        sign = "+"
    elif diff < 0:
        arrow = "▼"
        color = "#ef4444"  # red
        sign = ""
    else:
        return "", ""

    return arrow, f"{sign}{pct}%", color

def get_progress_bar(current, goal):
    """Generate progress bar and percentage"""
    if goal == 0:
        return "", "N/A"

    percentage = min(int((current / goal) * 100), 100)
    filled = int(percentage / 10)
    empty = 10 - filled

    bar = "█" * filled + "░" * empty
    return bar, f"{percentage}%"

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
    goals = data.get('goals', {})

    # Get last week's data for trend calculation
    history = data.get('weeklyHistory', [])
    last_week = history[0]['metrics'] if history else None

    # Calculate current week dates (Monday to Sunday) in KST
    today = datetime.datetime.now(KST)
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)

    # Format dates in US format (MM/DD/YYYY)
    week_start = monday.strftime('%m/%d/%Y')
    week_end = sunday.strftime('%m/%d/%Y')

    # Calculate totals
    total_social = current['socialContent']['instagram'] + current['socialContent']['tiktok'] + current['socialContent']['hellotalk']
    total_workouts = current['workouts']['running'] + current['workouts']['gym']

    # Calculate trends and progress
    if last_week:
        commits_trend = get_trend_indicator(current['commits'], last_week['commits'])
        talks_trend = get_trend_indicator(current['userSessions'], last_week['userSessions'])
        social_trend = get_trend_indicator(total_social, last_week['socialContent']['instagram'] + last_week['socialContent']['tiktok'] + last_week['socialContent']['hellotalk'])
        coffee_trend = get_trend_indicator(current['ctoMeetings'], last_week['ctoMeetings'])
        workouts_trend = get_trend_indicator(total_workouts, last_week['workouts']['running'] + last_week['workouts']['gym'])
        blog_trend = get_trend_indicator(current['blogPosts'], last_week['blogPosts'])
    else:
        commits_trend = talks_trend = social_trend = coffee_trend = workouts_trend = blog_trend = ("", "", "#9ca3af")

    # Calculate progress bars
    commits_progress = get_progress_bar(current['commits'], goals.get('weeklyCommits', 140))
    talks_progress = get_progress_bar(current['userSessions'], goals.get('weeklyUserTalks', 7))
    social_progress = get_progress_bar(total_social, goals.get('weeklySocial', 7))
    coffee_progress = get_progress_bar(current['ctoMeetings'], goals.get('weeklyCoffee', 2))
    workouts_progress = get_progress_bar(total_workouts, goals.get('weeklyWorkouts', 7))
    blog_progress = get_progress_bar(current['blogPosts'], goals.get('weeklyBlog', 1))

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
    <text x="260" y="35" text-anchor="middle" fill="#0f172a" font-size="22" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
        Moved the needle this week? 📈
    </text>
    <text x="260" y="60" text-anchor="middle" fill="#64748b" font-size="12" font-family="system-ui, -apple-system, sans-serif">
        {week_start} — {week_end}
    </text>

    <!-- Metrics Grid -->
    <!-- Row 1: Commits, User Talks, Social Posts -->
    <!-- Commits -->
    <g transform="translate(60, 85)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="32" text-anchor="middle" fill="#000000" font-size="32" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {current['commits']}
        </text>
        <text x="60" y="48" text-anchor="middle" fill="{commits_trend[2] if len(commits_trend) > 2 else '#9ca3af'}" font-size="9" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {commits_trend[0] + ' ' + commits_trend[1] if len(commits_trend) > 1 and commits_trend[0] else ''}
        </text>
        <text x="60" y="62" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            🚀 CODE COMMITS
        </text>
        <text x="60" y="76" text-anchor="middle" fill="#9ca3af" font-size="7" font-weight="400" font-family="Monaco, monospace">
            {commits_progress[0]}
        </text>
        <text x="60" y="88" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {commits_progress[1]} of goal
        </text>
    </g>

    <!-- User Talks -->
    <g transform="translate(200, 85)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="32" text-anchor="middle" fill="#000000" font-size="32" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {current['userSessions']}
        </text>
        <text x="60" y="48" text-anchor="middle" fill="{talks_trend[2] if len(talks_trend) > 2 else '#9ca3af'}" font-size="9" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {talks_trend[0] + ' ' + talks_trend[1] if len(talks_trend) > 1 and talks_trend[0] else ''}
        </text>
        <text x="60" y="62" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            💬 USER TALKS
        </text>
        <text x="60" y="76" text-anchor="middle" fill="#9ca3af" font-size="7" font-weight="400" font-family="Monaco, monospace">
            {talks_progress[0]}
        </text>
        <text x="60" y="88" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {talks_progress[1]} of goal
        </text>
    </g>

    <!-- Social Posts -->
    <g transform="translate(340, 85)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="32" text-anchor="middle" fill="#000000" font-size="32" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {total_social}
        </text>
        <text x="60" y="48" text-anchor="middle" fill="{social_trend[2] if len(social_trend) > 2 else '#9ca3af'}" font-size="9" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {social_trend[0] + ' ' + social_trend[1] if len(social_trend) > 1 and social_trend[0] else ''}
        </text>
        <text x="60" y="62" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            📱 SOCIAL POSTS
        </text>
        <text x="60" y="76" text-anchor="middle" fill="#9ca3af" font-size="7" font-weight="400" font-family="Monaco, monospace">
            {social_progress[0]}
        </text>
        <text x="60" y="88" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {social_progress[1]} of goal
        </text>
    </g>

    <!-- Row 2: Coffee Chats, Workouts, Blog Posts -->
    <!-- Coffee Chats -->
    <g transform="translate(60, 200)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="32" text-anchor="middle" fill="#000000" font-size="32" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {current['ctoMeetings']}
        </text>
        <text x="60" y="48" text-anchor="middle" fill="{coffee_trend[2] if len(coffee_trend) > 2 else '#9ca3af'}" font-size="9" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {coffee_trend[0] + ' ' + coffee_trend[1] if len(coffee_trend) > 1 and coffee_trend[0] else ''}
        </text>
        <text x="60" y="62" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            ☕ COFFEE CHATS
        </text>
        <text x="60" y="76" text-anchor="middle" fill="#9ca3af" font-size="7" font-weight="400" font-family="Monaco, monospace">
            {coffee_progress[0]}
        </text>
        <text x="60" y="88" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {coffee_progress[1]} of goal
        </text>
    </g>

    <!-- Workouts -->
    <g transform="translate(200, 200)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="32" text-anchor="middle" fill="#000000" font-size="32" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {total_workouts}
        </text>
        <text x="60" y="48" text-anchor="middle" fill="{workouts_trend[2] if len(workouts_trend) > 2 else '#9ca3af'}" font-size="9" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {workouts_trend[0] + ' ' + workouts_trend[1] if len(workouts_trend) > 1 and workouts_trend[0] else ''}
        </text>
        <text x="60" y="62" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            🏃 WORKOUTS
        </text>
        <text x="60" y="76" text-anchor="middle" fill="#9ca3af" font-size="7" font-weight="400" font-family="Monaco, monospace">
            {workouts_progress[0]}
        </text>
        <text x="60" y="88" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {workouts_progress[1]} of goal
        </text>
    </g>

    <!-- Blog Posts -->
    <g transform="translate(340, 200)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="32" text-anchor="middle" fill="#000000" font-size="32" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {current['blogPosts']}
        </text>
        <text x="60" y="48" text-anchor="middle" fill="{blog_trend[2] if len(blog_trend) > 2 else '#9ca3af'}" font-size="9" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {blog_trend[0] + ' ' + blog_trend[1] if len(blog_trend) > 1 and blog_trend[0] else ''}
        </text>
        <text x="60" y="62" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            📝 BLOG POSTS
        </text>
        <text x="60" y="76" text-anchor="middle" fill="#9ca3af" font-size="7" font-weight="400" font-family="Monaco, monospace">
            {blog_progress[0]}
        </text>
        <text x="60" y="88" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {blog_progress[1]} of goal
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
    """Update README.md Grinding enough? section with timestamp"""
    import re
    readme_path = Path('README.md')

    if not readme_path.exists():
        return

    with open(readme_path, 'r') as f:
        content = f.read()

    current_date = today.strftime('%m/%d/%y')
    timestamp_line = f'<div align="right"><sub>updated at {current_date}</sub></div>'

    # Pattern: # Grinding enough?, <p> with image, then optional timestamp
    pattern = r'(# Grinding enough\?\n\n<p align="center">\n  <img src="[^"]+" alt="Weekly Dashboard">\n</p>)\n*(?:<div align="right"><sub>updated at \d{2}/\d{2}/\d{2}</sub></div>)?'
    replacement = f'\\1\n\n{timestamp_line}'

    content = re.sub(pattern, replacement, content)

    with open(readme_path, 'w') as f:
        f.write(content)

    print(f"✅ Updated Grinding enough? timestamp: {current_date}")

if __name__ == "__main__":
    generate_dashboard_svg()