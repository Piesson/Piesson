import json
import datetime
from pathlib import Path

def generate_dashboard_svg():
    # Load data
    with open('dashboard/data.json', 'r') as f:
        data = json.load(f)

    current = data['currentWeek']['metrics']

    # SVG template with modern monochrome theme
    svg_content = f'''<svg width="520" height="440" xmlns="http://www.w3.org/2000/svg">
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
    <rect width="520" height="440" fill="url(#bg)" rx="16" stroke="#e2e8f0" stroke-width="1"/>

    <!-- Title -->
    <text x="260" y="40" text-anchor="middle" fill="#0f172a" font-size="22" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
        Weekly Progress Dashboard
    </text>
    <text x="260" y="60" text-anchor="middle" fill="#64748b" font-size="12" font-family="system-ui, -apple-system, sans-serif">
        {data['currentWeek']['startDate']} — {data['currentWeek']['endDate']}
    </text>

    <!-- Metrics Grid -->
    <!-- Row 1: Commits, User Talks, Social Posts -->
    <!-- Commits -->
    <g transform="translate(60, 90)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="35" text-anchor="middle" fill="#0f172a" font-size="28" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {current['commits']}
        </text>
        <text x="60" y="55" text-anchor="middle" fill="#374151" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            🚀 CODE COMMITS
        </text>
        <text x="60" y="75" text-anchor="middle" fill="#6b7280" font-size="9" font-family="system-ui, -apple-system, sans-serif">
            Building the future
        </text>
    </g>

    <!-- User Talks -->
    <g transform="translate(200, 90)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="35" text-anchor="middle" fill="#0f172a" font-size="28" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {current['userSessions']}
        </text>
        <text x="60" y="55" text-anchor="middle" fill="#374151" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            💬 USER TALKS
        </text>
        <text x="60" y="75" text-anchor="middle" fill="#6b7280" font-size="9" font-family="system-ui, -apple-system, sans-serif">
            Real conversations
        </text>
    </g>

    <!-- Social Posts -->
    <g transform="translate(340, 90)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="35" text-anchor="middle" fill="#0f172a" font-size="28" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {current['socialContent']['instagram'] + current['socialContent']['tiktok'] + current['socialContent']['hellotalk']}
        </text>
        <text x="60" y="55" text-anchor="middle" fill="#374151" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            📱 SOCIAL POSTS
        </text>
        <text x="60" y="75" text-anchor="middle" fill="#6b7280" font-size="9" font-family="system-ui, -apple-system, sans-serif">
            IG:{current['socialContent']['instagram']} TT:{current['socialContent']['tiktok']} HT:{current['socialContent']['hellotalk']}
        </text>
    </g>

    <!-- Row 2: Coffee Chats, Workouts, Blog Posts -->
    <!-- Coffee Chats -->
    <g transform="translate(60, 210)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="35" text-anchor="middle" fill="#0f172a" font-size="28" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {current['ctoMeetings']}
        </text>
        <text x="60" y="55" text-anchor="middle" fill="#374151" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            ☕ COFFEE CHATS
        </text>
        <text x="60" y="75" text-anchor="middle" fill="#6b7280" font-size="9" font-family="system-ui, -apple-system, sans-serif">
            Co-founder search
        </text>
    </g>

    <!-- Workouts -->
    <g transform="translate(200, 210)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="35" text-anchor="middle" fill="#0f172a" font-size="28" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {current['workouts']['running'] + current['workouts']['gym']}
        </text>
        <text x="60" y="55" text-anchor="middle" fill="#374151" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            🏃 WORKOUTS
        </text>
        <text x="60" y="75" text-anchor="middle" fill="#6b7280" font-size="9" font-family="system-ui, -apple-system, sans-serif">
            Run:{current['workouts']['running']} Gym:{current['workouts']['gym']}
        </text>
    </g>

    <!-- Blog Posts -->
    <g transform="translate(340, 210)">
        <rect width="120" height="100" fill="url(#cardBg)" rx="12" filter="url(#shadow)" stroke="#e2e8f0" stroke-width="1"/>
        <text x="60" y="35" text-anchor="middle" fill="#0f172a" font-size="28" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {current['blogPosts']}
        </text>
        <text x="60" y="55" text-anchor="middle" fill="#374151" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            📝 BLOG POSTS
        </text>
        <text x="60" y="75" text-anchor="middle" fill="#6b7280" font-size="9" font-family="system-ui, -apple-system, sans-serif">
            AI &amp; Startup content
        </text>
    </g>

    <!-- Progress Bar -->
    <rect x="60" y="340" width="400" height="6" fill="#f1f5f9" rx="3"/>
    <rect x="60" y="340" width="300" height="6" fill="#374151" rx="3"/>

    <!-- Footer -->
    <text x="260" y="370" text-anchor="middle" fill="#6b7280" font-size="10" font-family="system-ui, -apple-system, sans-serif">
        Updated {datetime.datetime.now().strftime('%Y-%m-%d')} • Building in public
    </text>

    <!-- Stats Summary -->
    <text x="60" y="395" fill="#374151" font-size="10" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
        Building my AI language learning startup
    </text>
    <text x="60" y="410" fill="#6b7280" font-size="9" font-family="system-ui, -apple-system, sans-serif">
        Product development • User engagement • Team building • Health
    </text>
</svg>'''

    # Save SVG
    output_path = Path('dashboard/weekly_dashboard.svg')
    output_path.write_text(svg_content)
    print(f"Dashboard generated: {output_path}")

if __name__ == "__main__":
    generate_dashboard_svg()