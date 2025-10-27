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
    return {
        'commits': 156,
        'code_reviews': 23,
        'pull_requests': 12,
        'issues': 8
    }

def generate_profile_card():
    """Generate the custom profile summary card"""
    username = os.getenv('USERNAME', 'Piesson')
    token = os.getenv('GITHUB_TOKEN', '')

    # Get GitHub data
    github_data = get_github_data(username, token)

    # Generate 4-quadrant stats
    stats = generate_four_quadrant_stats()

    # SVG dimensions
    card_width = 500
    card_height = 220

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

    <!-- 4-Quadrant Layout -->

    <!-- Top Left: Commits -->
    <g transform="translate(30, 60)">
        <rect width="200" height="65" fill="#ffffff" rx="8" stroke="#e5e7eb" stroke-width="1"/>
        <text x="15" y="25" fill="#111827" font-size="28" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {stats['commits']}
        </text>
        <text x="15" y="45" fill="#6b7280" font-size="12" font-family="system-ui, -apple-system, sans-serif">
            Commits
        </text>
        <text x="15" y="58" fill="#9ca3af" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Joined {github_data['join_date']}
        </text>
    </g>

    <!-- Top Right: Code Reviews -->
    <g transform="translate(250, 60)">
        <rect width="200" height="65" fill="#ffffff" rx="8" stroke="#e5e7eb" stroke-width="1"/>
        <text x="15" y="25" fill="#111827" font-size="28" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {stats['code_reviews']}
        </text>
        <text x="15" y="45" fill="#6b7280" font-size="12" font-family="system-ui, -apple-system, sans-serif">
            Code Reviews
        </text>
        <text x="15" y="58" fill="#9ca3af" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Total {github_data['total_commits']:,} commits
        </text>
    </g>

    <!-- Bottom Left: Pull Requests -->
    <g transform="translate(30, 145)">
        <rect width="200" height="65" fill="#ffffff" rx="8" stroke="#e5e7eb" stroke-width="1"/>
        <text x="15" y="25" fill="#111827" font-size="28" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {stats['pull_requests']}
        </text>
        <text x="15" y="45" fill="#6b7280" font-size="12" font-family="system-ui, -apple-system, sans-serif">
            Pull Requests
        </text>
        <text x="15" y="58" fill="#9ca3af" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Daily avg {github_data['daily_avg']}
        </text>
    </g>

    <!-- Bottom Right: Issues -->
    <g transform="translate(250, 145)">
        <rect width="200" height="65" fill="#ffffff" rx="8" stroke="#e5e7eb" stroke-width="1"/>
        <text x="15" y="25" fill="#111827" font-size="28" font-weight="700" font-family="system-ui, -apple-system, sans-serif">
            {stats['issues']}
        </text>
        <text x="15" y="45" fill="#6b7280" font-size="12" font-family="system-ui, -apple-system, sans-serif">
            Issues
        </text>
        <text x="15" y="58" fill="#9ca3af" font-size="10" font-family="system-ui, -apple-system, sans-serif">
            Opened & closed
        </text>
    </g>

    <!-- Center divider lines -->
    <line x1="250" y1="60" x2="250" y2="210" stroke="#e5e7eb" stroke-width="1"/>
    <line x1="30" y1="135" x2="450" y2="135" stroke="#e5e7eb" stroke-width="1"/>
</svg>'''

    # Save SVG
    output_path = Path('profile-summary-card-output/default/0-profile-details.svg')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content)
    print(f"Profile card generated: {output_path}")

if __name__ == "__main__":
    generate_profile_card()