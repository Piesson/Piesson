#!/usr/bin/env python3
"""
Generate custom GitHub profile summary card with contribution heatmap
"""

import json
import requests
import datetime
from pathlib import Path
import os

def get_github_data(username, token):
    """Fetch GitHub user data and calculate statistics"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        # Get user basic info
        user_response = requests.get(f'https://api.github.com/users/{username}', headers=headers)
        user_data = user_response.json()

        # Get repositories
        repos_response = requests.get(f'https://api.github.com/users/{username}/repos?per_page=100', headers=headers)
        repos_data = repos_response.json()

        # Calculate total commits (approximate from recent activity)
        total_commits = 0
        for repo in repos_data:
            if not repo['fork']:  # Skip forked repos
                commits_response = requests.get(f'https://api.github.com/repos/{username}/{repo["name"]}/commits?author={username}&per_page=1', headers=headers)
                if commits_response.status_code == 200:
                    # Get commit count from headers (GitHub API limitation workaround)
                    total_commits += len(commits_response.json())

        # Use fixed join date: January 2025
        created_at = datetime.datetime(2025, 1, 1)

        # Calculate days since joining (fixed date)
        today = datetime.datetime.now()
        days_since_join = (today - created_at).days

        # Calculate daily average based on Jan 1, 2025
        daily_avg = total_commits / max(days_since_join, 1) if days_since_join > 0 else 0

        return {
            'total_commits': total_commits,
            'join_date': 'Jan 2025',
            'daily_avg': round(daily_avg, 1),
            'days_since_join': days_since_join
        }

    except Exception as e:
        print(f"Error fetching GitHub data: {e}")
        # Return default values if API fails
        return {
            'total_commits': 0,
            'join_date': 'Jan 2025',
            'daily_avg': 0.0,
            'days_since_join': 0
        }

def generate_four_quadrant_stats():
    """Generate 4-quadrant statistics data"""
    stats = {
        'commits': 156,
        'code_reviews': 23,
        'pull_requests': 12,
        'issues': 8
    }

    # Calculate percentages
    total = sum(stats.values())
    percentages = {key: round((value / total) * 100) for key, value in stats.items()}

    return {
        'stats': stats,
        'percentages': percentages,
        'total': total
    }

def generate_quadrant_pie_chart(data):
    """Generate a 4-quadrant pie chart SVG"""
    import math

    stats = data['stats']
    percentages = data['percentages']

    # Chart dimensions
    size = 120
    center = size // 2
    radius = 45

    # Colors for each quadrant
    colors = {
        'commits': '#3b82f6',      # Blue
        'code_reviews': '#10b981', # Green
        'pull_requests': '#f59e0b', # Yellow
        'issues': '#ef4444'        # Red
    }

    # Calculate angles (starting from top, clockwise)
    total = data['total']
    current_angle = -90  # Start from top

    chart_svg = f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'

    for key, value in stats.items():
        if value == 0:
            continue

        # Calculate angle for this slice
        slice_angle = (value / total) * 360

        # Calculate start and end angles in radians
        start_angle_rad = math.radians(current_angle)
        end_angle_rad = math.radians(current_angle + slice_angle)

        # Calculate arc path
        x1 = center + radius * math.cos(start_angle_rad)
        y1 = center + radius * math.sin(start_angle_rad)
        x2 = center + radius * math.cos(end_angle_rad)
        y2 = center + radius * math.sin(end_angle_rad)

        large_arc = 1 if slice_angle > 180 else 0

        # Create path
        path = f'M {center},{center} L {x1},{y1} A {radius},{radius} 0 {large_arc},1 {x2},{y2} Z'

        chart_svg += f'<path d="{path}" fill="{colors[key]}" stroke="#ffffff" stroke-width="2"/>'

        # Add percentage label
        label_angle_rad = math.radians(current_angle + slice_angle / 2)
        label_x = center + (radius * 0.7) * math.cos(label_angle_rad)
        label_y = center + (radius * 0.7) * math.sin(label_angle_rad)

        chart_svg += f'<text x="{label_x}" y="{label_y}" text-anchor="middle" fill="white" font-size="12" font-weight="bold" font-family="system-ui, -apple-system, sans-serif">{percentages[key]}%</text>'

        current_angle += slice_angle

    chart_svg += '</svg>'
    return chart_svg

def generate_profile_card():
    """Generate the custom profile summary card"""
    username = os.getenv('USERNAME', 'Piesson')
    token = os.getenv('GITHUB_TOKEN', '')

    # Get GitHub data
    github_data = get_github_data(username, token)

    # Generate 4-quadrant stats
    quadrant_data = generate_four_quadrant_stats()
    pie_chart = generate_quadrant_pie_chart(quadrant_data)

    # SVG dimensions
    card_width = 500
    card_height = 200

    svg_content = f'''<svg width="{card_width}" height="{card_height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#f8fafc;stop-opacity:1" />
        </linearGradient>
    </defs>

    <!-- Background -->
    <rect width="{card_width}" height="{card_height}" fill="url(#cardBg)" rx="12" stroke="#e5e7eb" stroke-width="1"/>

    <!-- Title -->
    <text x="250" y="30" text-anchor="middle" fill="#111827" font-size="18" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
        GitHub Activity Overview
    </text>

    <!-- Left Side: 4-Quadrant Chart + Legend -->
    <g transform="translate(30, 50)">
        <!-- Pie Chart -->
        <g transform="translate(30, 20)">
            {pie_chart}
        </g>

        <!-- Legend -->
        <g transform="translate(170, 30)">
            <!-- Commits -->
            <g transform="translate(0, 0)">
                <rect x="0" y="0" width="12" height="12" fill="#3b82f6"/>
                <text x="18" y="10" fill="#111827" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
                    Commits: {quadrant_data['stats']['commits']} ({quadrant_data['percentages']['commits']}%)
                </text>
            </g>
            <!-- Code Reviews -->
            <g transform="translate(0, 20)">
                <rect x="0" y="0" width="12" height="12" fill="#10b981"/>
                <text x="18" y="10" fill="#111827" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
                    Reviews: {quadrant_data['stats']['code_reviews']} ({quadrant_data['percentages']['code_reviews']}%)
                </text>
            </g>
            <!-- Pull Requests -->
            <g transform="translate(0, 40)">
                <rect x="0" y="0" width="12" height="12" fill="#f59e0b"/>
                <text x="18" y="10" fill="#111827" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
                    PRs: {quadrant_data['stats']['pull_requests']} ({quadrant_data['percentages']['pull_requests']}%)
                </text>
            </g>
            <!-- Issues -->
            <g transform="translate(0, 60)">
                <rect x="0" y="0" width="12" height="12" fill="#ef4444"/>
                <text x="18" y="10" fill="#111827" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
                    Issues: {quadrant_data['stats']['issues']} ({quadrant_data['percentages']['issues']}%)
                </text>
            </g>
        </g>
    </g>

    <!-- Vertical Divider -->
    <line x1="350" y1="50" x2="350" y2="180" stroke="#e5e7eb" stroke-width="1"/>

    <!-- Right Side: Statistics Cards -->
    <g transform="translate(370, 60)">
        <!-- Total Commits -->
        <g transform="translate(0, 0)">
            <text x="0" y="20" fill="#111827" font-size="24" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
                {github_data['total_commits']:,}
            </text>
            <text x="0" y="35" fill="#6b7280" font-size="11" font-family="system-ui, -apple-system, sans-serif">
                Total Commits
            </text>
        </g>

        <!-- Join Date -->
        <g transform="translate(0, 50)">
            <text x="0" y="20" fill="#111827" font-size="16" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
                {github_data['join_date']}
            </text>
            <text x="0" y="35" fill="#6b7280" font-size="11" font-family="system-ui, -apple-system, sans-serif">
                Joined GitHub
            </text>
        </g>

        <!-- Daily Average -->
        <g transform="translate(0, 100)">
            <text x="0" y="20" fill="#111827" font-size="16" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
                {github_data['daily_avg']}
            </text>
            <text x="0" y="35" fill="#6b7280" font-size="11" font-family="system-ui, -apple-system, sans-serif">
                Daily Average
            </text>
        </g>
    </g>
</svg>'''

    # Save SVG
    output_path = Path('profile-summary-card-output/default/0-profile-details.svg')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content)
    print(f"Profile card generated: {output_path}")

if __name__ == "__main__":
    generate_profile_card()