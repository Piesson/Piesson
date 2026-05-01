#!/usr/bin/env python3
"""Get weekly commit count for current KST week from GitHub GraphQL API.

Returns:
    int  - actual commit count (including 0 if user really had 0 commits)
    None - API call failed for any reason. Callers MUST treat None as
           "unknown - keep showing previous value", never as zero.
"""

from __future__ import annotations
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional

from _graphql_client import post_graphql, ErrorKind

KST = timezone(timedelta(hours=9))
GRAPHQL_URL = "https://api.github.com/graphql"


def _week_window_utc(now_kst: datetime):
    monday = now_kst - timedelta(days=now_kst.weekday())
    sunday = monday + timedelta(days=6)
    monday_utc = monday.astimezone(timezone.utc)
    sunday_utc = sunday.replace(hour=23, minute=59, second=59).astimezone(timezone.utc)
    return (
        monday_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        sunday_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def get_weekly_commits() -> Optional[int]:
    username = os.getenv("GITHUB_USERNAME", os.getenv("USERNAME", "Piesson"))
    token = os.getenv("GITHUB_TOKEN", os.getenv("SUMMARY_CARDS_TOKEN", ""))
    if not token:
        print("[weekly-commits] no token in env; returning None (NOT 0)", file=sys.stderr)
        return None

    from_iso, to_iso = _week_window_utc(datetime.now(KST))
    print(f"[weekly-commits] querying {from_iso} -> {to_iso}", file=sys.stderr)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $username) {
            contributionsCollection(from: $from, to: $to) {
                totalCommitContributions
            }
        }
    }
    """
    variables = {"username": username, "from": from_iso, "to": to_iso}
    body = {"query": query, "variables": variables}

    data, err = post_graphql(GRAPHQL_URL, headers, body)
    if err is not None:
        print(f"[weekly-commits] API failed ({err.value}); returning None (NOT 0)", file=sys.stderr)
        return None

    try:
        n = int(data["data"]["user"]["contributionsCollection"]["totalCommitContributions"])
    except (KeyError, TypeError, ValueError):
        print("[weekly-commits] unexpected response shape; returning None", file=sys.stderr)
        return None

    print(f"[weekly-commits] got {n}", file=sys.stderr)
    return n


if __name__ == "__main__":
    v = get_weekly_commits()
    if v is None:
        print("None")
        sys.exit(2)
    print(v)
