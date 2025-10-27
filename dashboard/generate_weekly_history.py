#!/usr/bin/env python3
"""
Generate individual SVG cards for each week in history
Creates: dashboard/history/weekly_history_2025-W43.svg
"""

import json
from pathlib import Path
from datetime import datetime

def generate_history_svg(week_entry):
    """Generate SVG for a single week's history"""
    week_id = week_entry['week']
    metrics = week_entry['metrics']

    # Parse dates for display
    try:
        start_date = datetime.strptime(week_entry['startDate'], '%Y-%m-%d')
        end_date = datetime.strptime(week_entry['endDate'], '%Y-%m-%d')
        week_display = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    except:
        # Fallback for old format
        week_display = f"{week_entry['startDate']} - {week_entry['endDate']}"

    # Extract metrics with proper structure
    social = metrics.get('socialContent', {})
    if isinstance(social, dict):
        instagram = social.get('instagram', 0)
        tiktok = social.get('tiktok', 0)
        hellotalk = social.get('hellotalk', 0)
        total_social = instagram + tiktok + hellotalk
    else:
        # Old format: socialContent was a number
        total_social = social
        instagram = total_social // 3
        tiktok = total_social // 3
        hellotalk = total_social - (instagram + tiktok)

    workouts = metrics.get('workouts', {})
    if isinstance(workouts, dict):
        running = workouts.get('running', 0)
        gym = workouts.get('gym', 0)
        total_workouts = running + gym
    else:
        # Old format: workouts was a number
        total_workouts = workouts
        running = total_workouts // 2
        gym = total_workouts - running

    # Commits (from old format, might not exist)
    commits = metrics.get('commits', 0)

    # Other metrics
    user_sessions = metrics.get('userSessions', 0)
    cto_meetings = metrics.get('ctoMeetings', 0)
    blog_posts = metrics.get('blogPosts', 0)

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
    <text x="260" y="28" text-anchor="middle" fill="#0f172a" font-size="20" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
        Week {week_id.split('-W')[1]} Archive
    </text>
    <text x="260" y="50" text-anchor="middle" fill="#64748b" font-size="12" font-family="system-ui, -apple-system, sans-serif">
        {week_display}
    </text>

    <!-- Metrics Grid -->
    <!-- Row 1: Commits, User Talks, Social Posts -->
    <!-- Commits -->
    <g transform="translate(60, 75)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {commits}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            🚀 CODE COMMITS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            Daily goal: 20 commits
        </text>
    </g>

    <!-- User Talks -->
    <g transform="translate(200, 75)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {user_sessions}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            💬 USER TALKS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            Daily goal: 1 talk
        </text>
    </g>

    <!-- Social Posts -->
    <g transform="translate(340, 75)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {total_social}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            📱 SOCIAL POSTS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            IG:{instagram} TT:{tiktok} HT:{hellotalk}
        </text>
    </g>

    <!-- Row 2: Coffee Chats, Workouts, Blog Posts -->
    <!-- Coffee Chats -->
    <g transform="translate(60, 190)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {cto_meetings}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            ☕ COFFEE CHATS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            Weekly goal: 2 chats
        </text>
    </g>

    <!-- Workouts -->
    <g transform="translate(200, 190)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {total_workouts}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            🏃 WORKOUTS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            Run:{running} Gym:{gym}
        </text>
    </g>

    <!-- Blog Posts -->
    <g transform="translate(340, 190)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="40" text-anchor="middle" fill="#000000" font-size="36" font-weight="800" font-family="system-ui, -apple-system, sans-serif">
            {blog_posts}
        </text>
        <text x="60" y="60" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            📝 BLOG POSTS
        </text>
        <text x="60" y="78" text-anchor="middle" fill="#9ca3af" font-size="8" font-weight="400" font-family="system-ui, -apple-system, sans-serif">
            AI &amp; Startup content
        </text>
    </g>

</svg>'''

    return svg_content

def generate_all_history_svgs():
    """Generate SVGs for all weeks in history"""
    data_file = Path('dashboard/data.json')

    if not data_file.exists():
        print("❌ data.json not found")
        return

    # Load data
    with open(data_file, 'r') as f:
        data = json.load(f)

    weekly_history = data.get('weeklyHistory', [])

    if not weekly_history:
        print("No weekly history to generate")
        return

    # Create history directory
    history_dir = Path('dashboard/history')
    history_dir.mkdir(exist_ok=True)

    print(f"📚 Generating history SVGs for {len(weekly_history)} weeks...")

    generated_count = 0
    skipped_count = 0

    for entry in weekly_history:
        week_id = entry['week']
        output_file = history_dir / f"weekly_history_{week_id}.svg"

        # Check if file already exists (skip regeneration)
        if output_file.exists():
            print(f"  ⏭️  Skipped {week_id} (already exists)")
            skipped_count += 1
            continue

        # Generate SVG
        svg_content = generate_history_svg(entry)

        # Save to file
        with open(output_file, 'w') as f:
            f.write(svg_content)

        print(f"  ✅ Generated {week_id}")
        generated_count += 1

    print(f"\n✅ Completed: {generated_count} generated, {skipped_count} skipped")

if __name__ == "__main__":
    generate_all_history_svgs()
