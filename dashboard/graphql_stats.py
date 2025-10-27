#!/usr/bin/env python3
"""
GitHub GraphQL API integration for accurate contribution statistics
"""

import requests
import datetime

def get_github_activity_stats_graphql(username, token):
    """Fetch GitHub activity statistics using GraphQL API for accurate totals including private repos"""
    if not token:
        return None

    # GraphQL endpoint
    graphql_url = "https://api.github.com/graphql"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Get current year for contributions
    current_year = datetime.datetime.now().year
    from_date = f"{current_year}-01-01T00:00:00Z"
    to_date = f"{current_year}-12-31T23:59:59Z"

    # GraphQL query for total contributions
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $username) {
            contributionsCollection(from: $from, to: $to) {
                totalCommitContributions
                totalPullRequestContributions
                totalPullRequestReviewContributions
                totalIssueContributions
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
        response = requests.post(graphql_url, headers=headers, json={"query": query, "variables": variables})
        if response.status_code != 200:
            print(f"GraphQL API failed: {response.status_code}")
            return None

        data = response.json()
        if 'errors' in data:
            print(f"GraphQL errors: {data['errors']}")
            return None

        contributions = data['data']['user']['contributionsCollection']

        stats = {
            'commits': contributions['totalCommitContributions'],
            'code_reviews': contributions['totalPullRequestReviewContributions'],
            'pull_requests': contributions['totalPullRequestContributions'],
            'issues': contributions['totalIssueContributions']
        }

        print(f"GraphQL API - Commits: {stats['commits']}, Reviews: {stats['code_reviews']}, PRs: {stats['pull_requests']}, Issues: {stats['issues']}")
        return stats

    except Exception as e:
        print(f"GraphQL API error: {e}")
        return None
