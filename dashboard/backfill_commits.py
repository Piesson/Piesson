#!/usr/bin/env python3
"""Re-confirm weeklyHistory commit counts from the GitHub GraphQL API.

Why: weeklyHistory snapshots whatever commits value data.json happened to
hold at Monday-reset time. During the 2026-06 outage no push ran all week,
so W24-W28 were snapshotted as 0 even though the weeks had real commits.

Run this inside GitHub Actions (backfill_commits.yml) where
SUMMARY_CARDS_TOKEN is available — commit contributions on private repos
are only itemized for a fully-scoped PAT; a lesser token sees them only as
an opaque restrictedContributionsCount and returns wrong (near-zero)
totals.

Idempotent: re-running rewrites each entry with the API's answer for its
exact date range. On API failure (None) the stored value is preserved,
mirroring generate_svg.py's contract.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from get_weekly_commits import get_commits_for_range

DATA = Path('dashboard/data.json')


def _normalize_date(s):
    """Return 'YYYY-MM-DD' from 'YYYY-MM-DD' or legacy 'MM/DD/YYYY'."""
    for fmt in ('%Y-%m-%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except (ValueError, TypeError):
            continue
    return None


def main():
    if not DATA.exists():
        print(f"[commits-backfill] {DATA} not found", file=sys.stderr)
        return 1

    data = json.loads(DATA.read_text())
    changed = 0
    for entry in data.get('weeklyHistory') or []:
        start = _normalize_date(entry.get('startDate', ''))
        end = _normalize_date(entry.get('endDate', ''))
        week = entry.get('week') or f"{start}..{end}"
        if not start or not end:
            print(f"[commits-backfill] {week}: unparseable dates — skipping")
            continue

        confirmed = get_commits_for_range(start, end)
        old = (entry.get('metrics') or {}).get('commits', 0)
        if confirmed is None:
            print(f"[commits-backfill] {week}: API unavailable — keeping {old}")
            continue
        if confirmed != old:
            entry.setdefault('metrics', {})['commits'] = confirmed
            print(f"[commits-backfill] {week}: {old} -> {confirmed}")
            changed += 1
        else:
            print(f"[commits-backfill] {week}: {old} (unchanged)")

    if changed:
        with open(DATA, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[commits-backfill] updated {changed} weeklyHistory entries")
    else:
        print("[commits-backfill] nothing to update")
    return 0


if __name__ == '__main__':
    sys.exit(main())
