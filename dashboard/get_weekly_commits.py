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
    # Truncate to Monday 00:00:00 KST. Without the truncation the window
    # started at Monday <current time-of-day>, silently dropping every
    # commit made earlier in the day than the run's wall-clock time.
    monday = (now_kst - timedelta(days=now_kst.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    sunday = monday + timedelta(days=6)
    monday_utc = monday.astimezone(timezone.utc)
    sunday_utc = sunday.replace(hour=23, minute=59, second=59).astimezone(timezone.utc)
    return (
        monday_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        sunday_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def get_weekly_commits() -> Optional[int]:
    from_iso, to_iso = _week_window_utc(datetime.now(KST))
    return _query_commit_contributions(from_iso, to_iso)


def get_commits_for_range(start_date: str, end_date: str) -> Optional[int]:
    """Commit contributions for an explicit KST date range (inclusive).

    Dates are 'YYYY-MM-DD'. Same None-on-failure contract as
    get_weekly_commits(). Used by check_weekly_reset.py to confirm the
    closing week at snapshot time, and by backfill_commits.py to repair
    weeklyHistory entries that were snapshotted as 0.
    """
    try:
        start_kst = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=KST)
        end_kst = datetime.strptime(end_date, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, tzinfo=KST
        )
    except (ValueError, TypeError):
        print(f"[weekly-commits] bad range {start_date}..{end_date}; returning None", file=sys.stderr)
        return None
    from_iso = start_kst.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_iso = end_kst.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return _query_commit_contributions(from_iso, to_iso)


def _query_commit_contributions(from_iso: str, to_iso: str) -> Optional[int]:
    username = os.getenv("GITHUB_USERNAME", os.getenv("USERNAME", "Piesson"))
    token = os.getenv("GITHUB_TOKEN", os.getenv("SUMMARY_CARDS_TOKEN", ""))
    if not token:
        print("[weekly-commits] no token in env; returning None (NOT 0)", file=sys.stderr)
        return None

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
