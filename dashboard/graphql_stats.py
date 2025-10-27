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

    # Get all-time contributions (GitHub account creation to now)
    # Note: GraphQL API only supports 1 year range, so we need multiple queries
    # For now, we'll aggregate last few years to get a more complete picture
    current_year = datetime.datetime.now().year

    # We'll fetch contributions from multiple years and sum them
    all_stats = {
        'commits': 0,
        'code_reviews': 0,
        'pull_requests': 0,
        'issues': 0
    }

    # Fetch last 5 years (2020-2025) to cover most contributions
    start_year = max(2020, current_year - 5)

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

    try:
        for year in range(start_year, current_year + 1):
            from_date = f"{year}-01-01T00:00:00Z"
            to_date = f"{year}-12-31T23:59:59Z"

            variables = {
                "username": username,
                "from": from_date,
                "to": to_date
            }

            response = requests.post(graphql_url, headers=headers, json={"query": query, "variables": variables})
            if response.status_code != 200:
                print(f"GraphQL API failed for year {year}: {response.status_code}")
                continue

            data = response.json()
            if 'errors' in data:
                print(f"GraphQL errors for year {year}: {data['errors']}")
                continue

            contributions = data['data']['user']['contributionsCollection']

            # Accumulate stats
            all_stats['commits'] += contributions['totalCommitContributions']
            all_stats['code_reviews'] += contributions['totalPullRequestReviewContributions']
            all_stats['pull_requests'] += contributions['totalPullRequestContributions']
            all_stats['issues'] += contributions['totalIssueContributions']

            print(f"Year {year}: Commits={contributions['totalCommitContributions']}, Reviews={contributions['totalPullRequestReviewContributions']}, PRs={contributions['totalPullRequestContributions']}, Issues={contributions['totalIssueContributions']}")

        print(f"GraphQL API Total - Commits: {all_stats['commits']}, Reviews: {all_stats['code_reviews']}, PRs: {all_stats['pull_requests']}, Issues: {all_stats['issues']}")
        return all_stats

    except Exception as e:
        print(f"GraphQL API error: {e}")
        return None
