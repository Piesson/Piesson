#!/usr/bin/env python3
"""Recompute hand-filed dashboard metrics from Obsidian daily notes.

The /today skill writes one review block for the just-finished KST day:

    # 어제의 점검
    <!-- piesson-review-date: 2026-09-20 -->
    - 소셜 포스트: 2
    - 유저 대화: 1
    - 커피챗: 0
    - 운동: 1
    - 글: 0

Blank values are deliberately zero. Reviews before the 2026-09-21 migration
cutoff are ignored, preserving Slack-filed history. For managed weeks, the first
block makes notes authoritative and absent days contribute zero. Editing a past
managed note and rerunning this script repairs that week's totals without
incrementing twice.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from week_utils import iso_week_id

KST = timezone(timedelta(hours=9))
# Daily-note ownership begins on this Monday. Earlier Slack-filed weeks remain
# immutable even if a same-day rerun of /today creates a Sunday review block.
MIGRATION_START = date(2026, 9, 21)
HEADER = "# 어제의 점검"
FIELDS = (
    ("social", "소셜 포스트"),
    ("talks", "유저 대화"),
    ("coffee", "커피챗"),
    ("workouts", "운동"),
    ("blog", "글"),
)

_BLOCK_RE = re.compile(
    r"^# 어제의 점검[ \t]*\n"
    r"<!-- piesson-review-date: (?P<date>\d{4}-\d{2}-\d{2}) -->[ \t]*\n"
    + "".join(
        rf"- {re.escape(label)}:[ \t]*(?P<{key}>\d*)[ \t]*\n"
        for key, label in FIELDS[:-1]
    )
    + rf"- {re.escape(FIELDS[-1][1])}:[ \t]*(?P<{FIELDS[-1][0]}>\d*)[ \t]*(?:\n|$)",
    re.MULTILINE,
)


@dataclass(frozen=True)
class DailyMetrics:
    review_date: date
    social: int
    talks: int
    coffee: int
    workouts: int
    blog: int

    def values(self) -> tuple[int, int, int, int, int]:
        return self.social, self.talks, self.coffee, self.workouts, self.blog


def parse_note(path: Path) -> list[DailyMetrics]:
    text = path.read_text(encoding="utf-8")
    header_count = sum(1 for line in text.splitlines() if line.strip() == HEADER)
    matches = list(_BLOCK_RE.finditer(text))
    if header_count != len(matches):
        raise ValueError(
            f"{path}: malformed {HEADER!r} block; keep the date comment and five labels unchanged"
        )

    parsed = []
    for match in matches:
        try:
            review_date = date.fromisoformat(match.group("date"))
        except ValueError as exc:
            raise ValueError(f"{path}: invalid review date {match.group('date')!r}") from exc
        values = {key: int(match.group(key) or 0) for key, _ in FIELDS}
        parsed.append(DailyMetrics(review_date=review_date, **values))
    return parsed


def collect_notes(daily_dir: Path) -> dict[date, DailyMetrics]:
    records: dict[date, DailyMetrics] = {}
    sources: dict[date, Path] = {}
    if not daily_dir.exists():
        raise FileNotFoundError(f"daily-note directory not found: {daily_dir}")

    for path in sorted(daily_dir.glob("*.md")):
        for record in parse_note(path):
            previous = records.get(record.review_date)
            if previous and previous.values() != record.values():
                raise ValueError(
                    f"conflicting reviews for {record.review_date}: {sources[record.review_date]} and {path}"
                )
            records[record.review_date] = record
            sources[record.review_date] = path
    return records


def current_week_id(current_week: dict) -> str | None:
    raw = current_week.get("startDate")
    if not raw:
        return None
    return iso_week_id(date.fromisoformat(raw))


def aggregate(records: list[DailyMetrics]) -> dict[str, int]:
    return {
        "social": sum(item.social for item in records),
        "talks": sum(item.talks for item in records),
        "coffee": sum(item.coffee for item in records),
        "workouts": sum(item.workouts for item in records),
        "blog": sum(item.blog for item in records),
    }


def apply_metrics(metrics: dict, totals: dict[str, int]) -> bool:
    wanted = {
        "socialContent": {"total": totals["social"]},
        "userSessions": totals["talks"],
        "ctoMeetings": totals["coffee"],
        "workouts": {"total": totals["workouts"]},
        "blogPosts": totals["blog"],
    }
    changed = any(metrics.get(key) != value for key, value in wanted.items())
    metrics.update(wanted)
    return changed


def sync_data(data: dict, records: dict[date, DailyMetrics]) -> tuple[bool, list[str]]:
    by_week: dict[str, list[DailyMetrics]] = {}
    for record in records.values():
        if record.review_date < MIGRATION_START:
            continue
        by_week.setdefault(iso_week_id(record.review_date), []).append(record)

    targets: dict[str, dict] = {}
    current = data.get("currentWeek", {})
    current_id = current_week_id(current)
    if current_id:
        targets[current_id] = current
    for entry in data.get("weeklyHistory", []):
        if entry.get("week"):
            targets[entry["week"]] = entry

    changed = False
    summaries = []
    for target_week, target in targets.items():
        week_records = by_week.get(target_week)
        if not week_records:
            continue
        totals = aggregate(week_records)
        changed |= apply_metrics(target.setdefault("metrics", {}), totals)
        if target.get("manualMetricsSource") != "daily-notes":
            target["manualMetricsSource"] = "daily-notes"
            changed = True
        summaries.append(
            f"{target_week}: {len(week_records)} day(s), "
            f"social={totals['social']} talks={totals['talks']} coffee={totals['coffee']} "
            f"workouts={totals['workouts']} blog={totals['blog']}"
        )

    if changed:
        data["lastUpdated"] = datetime.now(KST).date().isoformat()
    return changed, summaries


def sync_file(daily_dir: Path, data_path: Path) -> tuple[bool, list[str]]:
    records = collect_notes(daily_dir)
    data = json.loads(data_path.read_text(encoding="utf-8"))
    changed, summaries = sync_data(data, records)
    if changed:
        data_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return changed, summaries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily-dir", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=Path("dashboard/data.json"))
    args = parser.parse_args()

    try:
        changed, summaries = sync_file(args.daily_dir, args.data)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"daily metric sync failed: {exc}", file=sys.stderr)
        return 1

    for summary in summaries:
        print(summary)
    if not summaries:
        print("No daily-note review blocks match retained dashboard weeks")
    print("Daily metrics updated" if changed else "Daily metrics already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
