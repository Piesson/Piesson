"""Disk cache for yearly GitHub contribution totals.

A year's totals are 'authoritative' once they've been computed in a
*later* calendar year — at that point the year is final and will never
change. Current year is never authoritative; it must be queried fresh.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

CACHE_VERSION = 1


def load_cache(path: Path) -> Dict[str, Any]:
    try:
        raw = path.read_text()
        data = json.loads(raw)
        if not isinstance(data, dict) or data.get("version") != CACHE_VERSION:
            return {"version": CACHE_VERSION, "years": {}}
        if not isinstance(data.get("years"), dict):
            data["years"] = {}
        return data
    except (FileNotFoundError, ValueError):
        return {"version": CACHE_VERSION, "years": {}}


def save_cache(path: Path, cache: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2, sort_keys=True))


def is_cache_authoritative(*, year: int, current_year: int, entry: Dict[str, Any]) -> bool:
    """Year is final iff it was computed AFTER it ended."""
    if year >= current_year:
        return False
    return int(entry.get("computed_in_year", 0)) > year
