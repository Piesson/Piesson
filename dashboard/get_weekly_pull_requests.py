#!/usr/bin/env python3
"""Count pull requests merged by the profile owner in a KST week.

The return contract matches get_weekly_commits: API/auth/network failure returns
None so callers preserve the last known value instead of writing a false zero.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import requests

KST = timezone(timedelta(hours=9))
SEARCH_URL = "https://api.github.com/search/issues"


def utc_range(start_date: str, end_date: str) -> tuple[str, str] | None:
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except (TypeError, ValueError):
        return None
    if end < start:
        return None

    start_kst = datetime.combine(start, time.min, tzinfo=KST)
    end_kst = datetime.combine(end + timedelta(days=1), time.min, tzinfo=KST) - timedelta(seconds=1)
    return (
        start_kst.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        end_kst.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def get_pull_requests_for_range(start_date: str, end_date: str) -> int | None:
    window = utc_range(start_date, end_date)
    if window is None:
        print(f"[weekly-prs] bad range {start_date}..{end_date}; returning None", file=sys.stderr)
        return None

    token = (
        os.environ.get("GITHUB_TOKEN")
        or os.environ.get("SUMMARY_CARDS_TOKEN")
        or os.environ.get("GH_TOKEN")
    )
    if not token:
        print("[weekly-prs] no token in env; returning None", file=sys.stderr)
        return None

    username = os.environ.get("USERNAME", "Piesson")
    start_utc, end_utc = window
    query = (
        f"author:{username} is:pr is:merged "
        f"merged:{start_utc}..{end_utc}"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        response = requests.get(
            SEARCH_URL,
            headers=headers,
            params={"q": query, "per_page": 1},
            timeout=30,
        )
        if response.status_code != 200:
            print(
                f"[weekly-prs] API HTTP {response.status_code}; returning None",
                file=sys.stderr,
            )
            return None
        payload = response.json()
        count = payload.get("total_count")
        if not isinstance(count, int):
            print("[weekly-prs] malformed API response; returning None", file=sys.stderr)
            return None
        print(f"[weekly-prs] got {count} for {start_utc}..{end_utc}")
        return count
    except (requests.RequestException, ValueError) as exc:
        print(f"[weekly-prs] API failed ({exc}); returning None", file=sys.stderr)
        return None


def get_weekly_pull_requests(data_path: Path = Path("dashboard/data.json")) -> int | None:
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
        current = data["currentWeek"]
        return get_pull_requests_for_range(current["startDate"], current["endDate"])
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[weekly-prs] data read failed ({exc}); returning None", file=sys.stderr)
        return None


if __name__ == "__main__":
    value = get_weekly_pull_requests()
    if value is None:
        raise SystemExit(1)
    print(value)
