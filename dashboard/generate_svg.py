import json
import datetime
from pathlib import Path

def generate_dashboard_svg():
    # Load data
    with open('dashboard/data.json', 'r') as f:
        data = json.load(f)

    current = data['currentWeek']['metrics']

    # SVG template with modern dark theme
    svg_content = f'''<svg width="950" height="520" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#16213e;stop-opacity:1" />
        </linearGradient>
        <filter id="shadow">
            <feDropShadow dx="0" dy="4" stdDeviation="3" flood-opacity="0.3"/>
        </filter>
    </defs>

    <!-- Background -->
    <rect width="950" height="520" fill="url(#bg)" rx="10"/>

    <!-- Title -->
    <text x="475" y="40" text-anchor="middle" fill="#fff" font-size="28" font-weight="bold" font-family="system-ui, -apple-system, sans-serif">
        📊 My Weekly Startup Journey
    </text>
    <text x="475" y="65" text-anchor="middle" fill="#94a3b8" font-size="14" font-family="system-ui, -apple-system, sans-serif">
        Building dreams one week at a time • {data['currentWeek']['startDate']} → {data['currentWeek']['endDate']}
    </text>

    <!-- Subtitle descriptions -->
    <text x="475" y="85" text-anchor="middle" fill="#64748b" font-size="12" font-family="system-ui, -apple-system, sans-serif">
        Here's what I accomplished this week while building my AI language learning app
    </text>

    <!-- Metrics Cards Row 1 -->
    <!-- Commits -->
    <g transform="translate(50, 110)">
        <rect width="140" height="120" fill="#0f3460" rx="8" filter="url(#shadow)"/>
        <text x="70" y="35" text-anchor="middle" fill="#60a5fa" font-size="32" font-weight="bold" font-family="system-ui, -apple-system, sans-serif">
            {current['commits']}
        </text>
        <text x="70" y="55" text-anchor="middle" fill="#94a3b8" font-size="12" font-family="system-ui, -apple-system, sans-serif">
            💻 Code Commits
        </text>
        <text x="70" y="75" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Lines of code written.
        </text>
        <text x="70" y="88" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Building the future!
        </text>
        <text x="70" y="105" text-anchor="middle" fill="#4ade80" font-size="14" font-family="system-ui, -apple-system, sans-serif">
            ↑ +10.5%
        </text>
    </g>

    <!-- Social Content -->
    <g transform="translate(210, 110)">
        <rect width="140" height="120" fill="#0f3460" rx="8" filter="url(#shadow)"/>
        <text x="70" y="35" text-anchor="middle" fill="#f472b6" font-size="32" font-weight="bold" font-family="system-ui, -apple-system, sans-serif">
            {current['socialContent']['instagram'] + current['socialContent']['tiktok'] + current['socialContent']['hellotalk']}
        </text>
        <text x="70" y="55" text-anchor="middle" fill="#94a3b8" font-size="12" font-family="system-ui, -apple-system, sans-serif">
            📱 Social Posts
        </text>
        <text x="70" y="75" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Sharing my story.
        </text>
        <text x="70" y="88" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            IG:{current['socialContent']['instagram']} TT:{current['socialContent']['tiktok']} HT:{current['socialContent']['hellotalk']}
        </text>
        <text x="70" y="105" text-anchor="middle" fill="#4ade80" font-size="14" font-family="system-ui, -apple-system, sans-serif">
            ↑ +25%
        </text>
    </g>

    <!-- User Sessions -->
    <g transform="translate(370, 110)">
        <rect width="140" height="120" fill="#0f3460" rx="8" filter="url(#shadow)"/>
        <text x="70" y="35" text-anchor="middle" fill="#fbbf24" font-size="32" font-weight="bold" font-family="system-ui, -apple-system, sans-serif">
            {current['userSessions']}
        </text>
        <text x="70" y="55" text-anchor="middle" fill="#94a3b8" font-size="12" font-family="system-ui, -apple-system, sans-serif">
            👥 User Talks
        </text>
        <text x="70" y="75" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Chats, calls, meetings.
        </text>
        <text x="70" y="88" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Real conversations!
        </text>
        <text x="70" y="105" text-anchor="middle" fill="#4ade80" font-size="14" font-family="system-ui, -apple-system, sans-serif">
            ↑ +10.4%
        </text>
    </g>

    <!-- CTO Meetings -->
    <g transform="translate(530, 110)">
        <rect width="140" height="120" fill="#0f3460" rx="8" filter="url(#shadow)"/>
        <text x="70" y="35" text-anchor="middle" fill="#c084fc" font-size="32" font-weight="bold" font-family="system-ui, -apple-system, sans-serif">
            {current['ctoMeetings']}
        </text>
        <text x="70" y="55" text-anchor="middle" fill="#94a3b8" font-size="12" font-family="system-ui, -apple-system, sans-serif">
            🤝 CTO Meetings
        </text>
        <text x="70" y="75" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Looking for my
        </text>
        <text x="70" y="88" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            technical co-founder.
        </text>
        <text x="70" y="105" text-anchor="middle" fill="#4ade80" font-size="14" font-family="system-ui, -apple-system, sans-serif">
            ↑ +33%
        </text>
    </g>

    <!-- Workouts -->
    <g transform="translate(690, 110)">
        <rect width="140" height="120" fill="#0f3460" rx="8" filter="url(#shadow)"/>
        <text x="70" y="35" text-anchor="middle" fill="#fb7185" font-size="32" font-weight="bold" font-family="system-ui, -apple-system, sans-serif">
            {current['workouts']['running'] + current['workouts']['gym']}
        </text>
        <text x="70" y="55" text-anchor="middle" fill="#94a3b8" font-size="12" font-family="system-ui, -apple-system, sans-serif">
            🏃‍♂️ Workouts
        </text>
        <text x="70" y="75" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Staying healthy.
        </text>
        <text x="70" y="88" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Run: {current['workouts']['running']} | Gym: {current['workouts']['gym']}
        </text>
        <text x="70" y="105" text-anchor="middle" fill="#4ade80" font-size="14" font-family="system-ui, -apple-system, sans-serif">
            ↑ +25%
        </text>
    </g>

    <!-- Blog Posts Row 2 -->
    <g transform="translate(390, 260)">
        <rect width="220" height="120" fill="#0f3460" rx="8" filter="url(#shadow)"/>
        <text x="110" y="35" text-anchor="middle" fill="#34d399" font-size="32" font-weight="bold" font-family="system-ui, -apple-system, sans-serif">
            {current['blogPosts']}
        </text>
        <text x="110" y="55" text-anchor="middle" fill="#94a3b8" font-size="12" font-family="system-ui, -apple-system, sans-serif">
            ✍️ AI & Startup Posts
        </text>
        <text x="110" y="75" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Writing about my journey. Sharing what I learn.</text>
        <text x="110" y="88" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Helping others build their dreams too.
        </text>
        <text x="110" y="105" text-anchor="middle" fill="#4ade80" font-size="14" font-family="system-ui, -apple-system, sans-serif">
            ↑ +100%
        </text>
    </g>

    <!-- Footer -->
    <text x="475" y="420" text-anchor="middle" fill="#475569" font-size="11" font-family="system-ui, -apple-system, sans-serif">
        Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} UTC
    </text>

    <!-- Motivational quote -->
    <text x="475" y="445" text-anchor="middle" fill="#64748b" font-size="12" font-family="system-ui, -apple-system, sans-serif" font-style="italic">
        "Every commit, every post, every conversation brings me closer to my dream."
    </text>

    <!-- Weekly streak indicator -->
    <text x="475" y="470" text-anchor="middle" fill="#fbbf24" font-size="11" font-family="system-ui, -apple-system, sans-serif">
        💪 Weekly consistency streak: Building habits that build the future
    </text>
</svg>'''

    # Save SVG
    output_path = Path('dashboard/weekly_dashboard.svg')
    output_path.write_text(svg_content)
    print(f"Dashboard generated: {output_path}")

if __name__ == "__main__":
    generate_dashboard_svg()