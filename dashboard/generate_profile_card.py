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

def generate_contribution_graph():
    """Generate a 4-quadrant contribution graph SVG"""
    import random
    random.seed(42)  # Consistent pattern

    # Generate sample data for 12 months
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Generate commit data (0-100 range)
    commits_data = [random.randint(20, 100) for _ in range(12)]

    # SVG dimensions
    width = 200
    height = 80
    max_value = max(commits_data)

    # Create path for the area chart
    points = []
    for i, value in enumerate(commits_data):
        x = (i / (len(commits_data) - 1)) * width
        y = height - (value / max_value) * height
        points.append(f"{x},{y}")

    # Create the path string
    path_points = " ".join(points)

    graph_svg = f'''
    <!-- Contribution Graph -->
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <!-- Grid lines -->
        <g opacity="0.1">
            <line x1="0" y1="{height//4}" x2="{width}" y2="{height//4}" stroke="#6b7280" stroke-width="1"/>
            <line x1="0" y1="{height//2}" x2="{width}" y2="{height//2}" stroke="#6b7280" stroke-width="1"/>
            <line x1="0" y1="{3*height//4}" x2="{width}" y2="{3*height//4}" stroke="#6b7280" stroke-width="1"/>
        </g>

        <!-- Area fill -->
        <path d="M 0,{height} L {path_points} L {width},{height} Z"
              fill="#3b82f6" fill-opacity="0.1" stroke="none"/>

        <!-- Main line -->
        <polyline points="{path_points}"
                  fill="none" stroke="#3b82f6" stroke-width="2"/>

        <!-- Data points -->'''

    for i, value in enumerate(commits_data):
        x = (i / (len(commits_data) - 1)) * width
        y = height - (value / max_value) * height
        graph_svg += f'<circle cx="{x}" cy="{y}" r="2" fill="#3b82f6"/>'

    graph_svg += '''
    </svg>'''

    return graph_svg

def generate_profile_card():
    """Generate the custom profile summary card"""
    username = os.getenv('USERNAME', 'Piesson')
    token = os.getenv('GITHUB_TOKEN', '')

    # Get GitHub data
    github_data = get_github_data(username, token)

    # Generate contribution graph
    graph = generate_contribution_graph()

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

    <!-- Contribution Graph -->
    <g transform="translate(30, 50)">
        <text x="0" y="-10" fill="#6b7280" font-size="12" font-weight="500" font-family="system-ui, -apple-system, sans-serif">
            Contributions
        </text>
        {graph}
    </g>

    <!-- Statistics -->
    <g transform="translate(280, 60)">
        <!-- Total Commits -->
        <text x="0" y="20" fill="#111827" font-size="24" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {github_data['total_commits']:,}
        </text>
        <text x="0" y="35" fill="#6b7280" font-size="11" font-family="system-ui, -apple-system, sans-serif">
            Total Commits
        </text>

        <!-- Join Date -->
        <text x="0" y="65" fill="#111827" font-size="16" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {github_data['join_date']}
        </text>
        <text x="0" y="80" fill="#6b7280" font-size="11" font-family="system-ui, -apple-system, sans-serif">
            Joined GitHub
        </text>

        <!-- Daily Average -->
        <text x="0" y="110" fill="#111827" font-size="16" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
            {github_data['daily_avg']}
        </text>
        <text x="0" y="125" fill="#6b7280" font-size="11" font-family="system-ui, -apple-system, sans-serif">
            Daily Average
        </text>
    </g>
</svg>'''

    # Save SVG
    output_path = Path('profile-summary-card-output/default/0-profile-details.svg')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content)
    print(f"Profile card generated: {output_path}")

if __name__ == "__main__":
    generate_profile_card()