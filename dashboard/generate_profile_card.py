#!/usr/bin/env python3
"""
Generate custom GitHub profile summary card with contribution heatmap
"""

import json
import requests
import datetime
from pathlib import Path
import os
from graphql_stats import get_github_activity_stats_graphql

def get_github_data_from_stats(activity_stats):
    """Create github_data dict from already-fetched activity stats"""
    total_commits = activity_stats.get('commits', 0)

    # Use actual join date: August 2024
    created_at = datetime.datetime(2024, 8, 1)

    # Calculate days since joining
    today = datetime.datetime.now()
    days_since_join = (today - created_at).days

    # Calculate daily average based on actual join date
    daily_avg = total_commits / max(days_since_join, 1) if days_since_join > 0 else 0

    return {
        'total_commits': total_commits,
        'join_date': 'Aug 2024',
        'daily_avg': round(daily_avg, 1),
        'days_since_join': days_since_join
    }

def get_github_data(username, token):
    """Fetch GitHub user data and calculate statistics"""
    # Try to get commit count from GraphQL first (includes private repos)
    graphql_result = get_github_activity_stats_graphql(username, token)
    total_commits = graphql_result['commits'] if graphql_result else 0

    # If GraphQL failed or no token, fallback to public repo count
    if total_commits == 0:
        print("GraphQL failed for total commits, using public repo approximation...")
        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            headers['Authorization'] = f'token {token}'

        try:
            repos_response = requests.get(f'https://api.github.com/users/{username}/repos?per_page=100', headers=headers)
            if repos_response.status_code == 200:
                repos_data = repos_response.json()
                for repo in repos_data:
                    if not repo['fork']:
                        commits_response = requests.get(f'https://api.github.com/repos/{username}/{repo["name"]}/commits?author={username}&per_page=1', headers=headers)
                        if commits_response.status_code == 200:
                            total_commits += len(commits_response.json())
        except Exception as e:
            print(f"Error fetching public repos: {e}")

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

def get_github_activity_stats(username, token):
    """Fetch GitHub activity statistics from API - Try GraphQL first, then REST API"""
    # Try GraphQL first for accurate totals (includes private repos)
    graphql_result = get_github_activity_stats_graphql(username, token)
    if graphql_result:
        return graphql_result

    # Fallback to REST API
    print("Using REST API fallback...")
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }

    # Add authorization header only if token is provided
    if token:
        headers['Authorization'] = f'token {token}'

    try:
        # Get user repositories
        repos_response = requests.get(f'https://api.github.com/users/{username}/repos?per_page=100', headers=headers)
        if repos_response.status_code != 200:
            print(f"Failed to get repos for activity: {repos_response.status_code}")
            raise Exception(f"GitHub API error: {repos_response.status_code}")
        repos = repos_response.json()

        # Count commits across all repos
        total_commits = 0
        for repo in repos:
            if not repo.get('fork', True):  # Skip forked repos
                # Get commits count (limited by API, but gives us a sample)
                commits_response = requests.get(f'https://api.github.com/repos/{username}/{repo["name"]}/commits?author={username}&per_page=100', headers=headers)
                if commits_response.status_code == 200:
                    total_commits += len(commits_response.json())

        # Get pull requests (created by user)
        prs_response = requests.get(f'https://api.github.com/search/issues?q=author:{username}+type:pr', headers=headers)
        pull_requests = prs_response.json().get('total_count', 0) if prs_response.status_code == 200 else 0

        # Get issues (created by user)
        issues_response = requests.get(f'https://api.github.com/search/issues?q=author:{username}+type:issue', headers=headers)
        issues = issues_response.json().get('total_count', 0) if issues_response.status_code == 200 else 0

        # Code reviews (approximate from PR comments - GitHub API limitation)
        # This is an approximation since GitHub doesn't have a direct code review count API
        code_reviews = max(1, total_commits // 10)  # Rough estimate: 1 review per 10 commits

        stats = {
            'commits': total_commits,
            'code_reviews': code_reviews,
            'pull_requests': pull_requests,
            'issues': issues
        }

        return stats

    except Exception as e:
        print(f"Error fetching GitHub activity: {e}")
        # Return default values if API fails
        return {
            'commits': 156,
            'code_reviews': 23,
            'pull_requests': 12,
            'issues': 8
        }

def generate_four_quadrant_stats_from_data(stats):
    """Generate 4-quadrant statistics data from already-fetched stats"""
    # Only set minimum if ALL values are 0 (to avoid empty pie chart)
    if all(value == 0 for value in stats.values()):
        for key in stats:
            stats[key] = 1  # Minimum 1 for pie chart visibility when no data

    # Calculate percentages
    total = sum(stats.values())
    percentages = {key: round((value / total) * 100) for key, value in stats.items()}

    return {
        'stats': stats,
        'percentages': percentages,
        'total': total
    }

def generate_four_quadrant_stats(username, token):
    """Generate 4-quadrant statistics data from GitHub API (legacy)"""
    stats = get_github_activity_stats(username, token)
    return generate_four_quadrant_stats_from_data(stats)

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

    # Get activity stats ONCE (used by both pie chart and total commits)
    activity_stats = get_github_activity_stats(username, token)

    # Generate 4-quadrant stats from the same data
    quadrant_data = generate_four_quadrant_stats_from_data(activity_stats)
    pie_chart = generate_quadrant_pie_chart(quadrant_data)

    # Get GitHub data using the same commit count
    github_data = get_github_data_from_stats(activity_stats)

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
    <g transform="translate(20, 50)">
        <!-- Pie Chart -->
        <g transform="translate(50, 30)">
            {pie_chart}
        </g>

        <!-- Legend -->
        <g transform="translate(180, 40)">
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
                Daily commit avg.
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