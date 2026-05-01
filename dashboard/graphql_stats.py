#!/usr/bin/env python3
"""GitHub GraphQL API integration for accurate yearly contribution stats.

This module is called by generate_profile_card.py. Past-year stats are
cached on disk by _yearly_cache (Task 8); this module just builds the
single aliased GraphQL query and parses the response.
"""

from __future__ import annotations
import datetime as _dt
import sys
from pathlib import Path
from typing import Optional

from _graphql_client import post_graphql
from _yearly_cache import load_cache, save_cache, is_cache_authoritative

GRAPHQL_URL = "https://api.github.com/graphql"
CACHE_PATH = Path(__file__).resolve().parent / ".stats_cache.json"


def _build_query(years):
    """Build a single GraphQL query with one aliased contributionsCollection per year.

    Returns (query_string, variables_dict).
    """
    aliases = []
    variables = {"username": None}
    for y in years:
        from_var, to_var = f"from{y}", f"to{y}"
        aliases.append(
            f"      y{y}: contributionsCollection(from: ${from_var}, to: ${to_var}) {{\n"
            f"        totalCommitContributions\n"
            f"        totalPullRequestContributions\n"
            f"        totalPullRequestReviewContributions\n"
            f"        totalIssueContributions\n"
            f"      }}"
        )
        variables[from_var] = f"{y}-01-01T00:00:00Z"
        variables[to_var] = f"{y}-12-31T23:59:59Z"

    var_decls = ", ".join(["$username: String!"] +
                          [f"${f'from{y}'}: DateTime!, ${f'to{y}'}: DateTime!"
                           for y in years])
    query = (
        f"query({var_decls}) {{\n"
        f"  user(login: $username) {{\n"
        + "\n".join(aliases) + "\n"
        f"  }}\n"
        f"}}\n"
    )
    return query, variables


def get_github_activity_stats_graphql(
    username: str,
    token: str,
    *,
    current_year: Optional[int] = None,
):
    """Sum yearly contributions from 2020 onward, querying only uncached years.

    Returns dict {commits, code_reviews, pull_requests, issues} on success,
    None on any API failure. (No silent zero.)
    """
    if not token:
        print("[graphql_stats] no token; returning None", file=sys.stderr)
        return None

    if current_year is None:
        current_year = _dt.datetime.now().year
    # Fixed floor at 2020 — see T7 rationale (rolling-window phantom-drop bug + caching).
    all_years = list(range(2020, current_year + 1))

    cache = load_cache(CACHE_PATH)
    cached_years = []
    fetch_years = []
    for y in all_years:
        entry = cache["years"].get(str(y))
        if entry and is_cache_authoritative(year=y, current_year=current_year, entry=entry):
            cached_years.append((y, entry))
        else:
            fetch_years.append(y)

    totals = {"commits": 0, "code_reviews": 0, "pull_requests": 0, "issues": 0}
    for _, entry in cached_years:
        totals["commits"]       += int(entry.get("commits", 0))
        totals["code_reviews"]  += int(entry.get("code_reviews", 0))
        totals["pull_requests"] += int(entry.get("pull_requests", 0))
        totals["issues"]        += int(entry.get("issues", 0))

    if not fetch_years:
        print("[graphql_stats] all years served from cache; 0 API calls", file=sys.stderr)
        return totals

    query, variables = _build_query(fetch_years)
    variables["username"] = username

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data, err = post_graphql(GRAPHQL_URL, headers, {"query": query, "variables": variables})
    if err is not None:
        print(f"[graphql_stats] API failed ({err.value}); returning None", file=sys.stderr)
        return None

    user = (data or {}).get("data", {}).get("user", {})
    if not user:
        print("[graphql_stats] empty user payload; returning None", file=sys.stderr)
        return None

    for y in fetch_years:
        bucket = user.get(f"y{y}")
        if not bucket:
            print(f"[graphql_stats] missing y{y}; returning None", file=sys.stderr)
            return None
        c = int(bucket.get("totalCommitContributions", 0))
        r = int(bucket.get("totalPullRequestReviewContributions", 0))
        p = int(bucket.get("totalPullRequestContributions", 0))
        i = int(bucket.get("totalIssueContributions", 0))
        totals["commits"]       += c
        totals["code_reviews"]  += r
        totals["pull_requests"] += p
        totals["issues"]        += i
        # only past years go into cache; current year is intentionally skipped
        if y < current_year:
            cache["years"][str(y)] = {
                "commits": c, "code_reviews": r, "pull_requests": p, "issues": i,
                "computed_in_year": current_year,
            }

    save_cache(CACHE_PATH, cache)
    return totals
