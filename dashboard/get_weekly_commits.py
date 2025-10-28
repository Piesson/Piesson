#!/usr/bin/env python3
"""
Get weekly commit count from GitHub GraphQL API
Counts all commits across all repositories (including private) for current week
"""

import os
import requests
from datetime import datetime, timedelta, timezone

# KST = UTC + 9 hours
KST = timezone(timedelta(hours=9))

def get_weekly_commits_graphql(username, token):
    """
    Get commit count for current week using GitHub GraphQL API
    This includes ALL repositories (private + public)
    """
    import sys
    if not token:
        print("Warning: No GITHUB_TOKEN provided, cannot fetch weekly commits", file=sys.stderr)
        return 0

    # Calculate current week's Monday and Sunday in KST
    today = datetime.now(KST)
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    # Convert to UTC for GitHub API (GitHub uses UTC timestamps)
    monday_utc = monday.astimezone(timezone.utc)
    sunday_utc = sunday.replace(hour=23, minute=59, second=59).astimezone(timezone.utc)

    # Format as ISO 8601 strings
    from_date = monday_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    to_date = sunday_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"Fetching commits for week: {monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')} (KST)", file=sys.stderr)
    print(f"GitHub API query: {from_date} to {to_date} (UTC)", file=sys.stderr)

    # GraphQL endpoint
    graphql_url = "https://api.github.com/graphql"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # GraphQL query for current week's contributions
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $username) {
            contributionsCollection(from: $from, to: $to) {
                totalCommitContributions
            }
        }
    }
    """

    variables = {
        "username": username,
        "from": from_date,
        "to": to_date
    }

    try:
        response = requests.post(
            graphql_url,
            headers=headers,
            json={"query": query, "variables": variables}
        )

        if response.status_code != 200:
            print(f"GraphQL API failed: {response.status_code}", file=sys.stderr)
            print(f"Response: {response.text}", file=sys.stderr)
            return 0

        data = response.json()

        if 'errors' in data:
            print(f"GraphQL errors: {data['errors']}", file=sys.stderr)
            return 0

        commits = data['data']['user']['contributionsCollection']['totalCommitContributions']
        print(f"✅ Weekly commits (all repos): {commits}", file=sys.stderr)
        return commits

    except Exception as e:
        print(f"Error fetching weekly commits: {e}", file=sys.stderr)
        return 0

def get_weekly_commits():
    """
    Main function to get weekly commits
    Uses environment variables for username and token
    """
    username = os.getenv('GITHUB_USERNAME', os.getenv('USERNAME', 'Piesson'))
    token = os.getenv('GITHUB_TOKEN', os.getenv('SUMMARY_CARDS_TOKEN', ''))

    if not token:
        import sys
        print("⚠️ No GitHub token found. Set GITHUB_TOKEN or SUMMARY_CARDS_TOKEN environment variable.", file=sys.stderr)
        print("Falling back to 0 commits", file=sys.stderr)
        return 0

    return get_weekly_commits_graphql(username, token)

if __name__ == "__main__":
    commits = get_weekly_commits()
    print(f"\nWeekly commits: {commits}")
