import copy
import tempfile
import unittest
from pathlib import Path

from tests import conftest  # noqa: F401
from sync_daily_metrics import collect_notes, parse_note, sync_data


BASE_DATA = {
    "lastUpdated": "2026-09-20",
    "currentWeek": {
        "startDate": "2026-09-21",
        "endDate": "2026-09-27",
        "metrics": {
            "pullRequests": 8,
            "socialContent": {"instagram": 9, "tiktok": 9, "hellotalk": 9},
            "userSessions": 9,
            "ctoMeetings": 9,
            "workouts": {"running": 9, "gym": 9},
            "blogPosts": 9,
            "tokens": {"total": 123},
        },
    },
    "weeklyHistory": [
        {
            "week": "2026-W38",
            "startDate": "2026-09-14",
            "endDate": "2026-09-20",
            "metrics": {
                "pullRequests": 77,
                "socialContent": {"instagram": 0, "tiktok": 10, "hellotalk": 0},
                "userSessions": 1,
                "ctoMeetings": 1,
                "workouts": {"running": 1, "gym": 1},
                "blogPosts": 1,
            },
        }
    ],
}


def note(day, social="", talks="", coffee="", workouts="", blog=""):
    return f"""---
type: note
created: 2026-09-21
tags: [daily]
---
# 어제의 점검
<!-- piesson-review-date: {day} -->
- 소셜 포스트: {social}
- 유저 대화: {talks}
- 커피챗: {coffee}
- 운동: {workouts}
- 글: {blog}
"""


class DailyMetricSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.daily = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_blank_values_are_zero(self):
        path = self.daily / "daily.md"
        path.write_text(note("2026-09-21"), encoding="utf-8")
        parsed = parse_note(path)[0]
        self.assertEqual(parsed.values(), (0, 0, 0, 0, 0))

    def test_current_week_is_recomputed_not_incremented(self):
        (self.daily / "monday.md").write_text(
            note("2026-09-21", 2, 1, 0, 1, 0), encoding="utf-8"
        )
        (self.daily / "tuesday.md").write_text(
            note("2026-09-22", 3, 0, 1, 1, 1), encoding="utf-8"
        )
        records = collect_notes(self.daily)
        data = copy.deepcopy(BASE_DATA)

        changed, summaries = sync_data(data, records)
        metrics = data["currentWeek"]["metrics"]
        self.assertTrue(changed)
        self.assertTrue(summaries[0].startswith("2026-W39: 2 day(s)"))
        self.assertEqual(metrics["socialContent"], {"total": 5})
        self.assertEqual(metrics["userSessions"], 1)
        self.assertEqual(metrics["ctoMeetings"], 1)
        self.assertEqual(metrics["workouts"], {"total": 2})
        self.assertEqual(metrics["blogPosts"], 1)
        self.assertEqual(metrics["pullRequests"], 8)
        self.assertEqual(metrics["tokens"], {"total": 123})
        self.assertEqual(data["currentWeek"]["manualMetricsSource"], "daily-notes")

        changed_again, _ = sync_data(data, records)
        self.assertFalse(changed_again)
        self.assertEqual(metrics["socialContent"], {"total": 5})

    def test_pre_migration_boundary_week_is_preserved(self):
        (self.daily / "sunday.md").write_text(
            note("2026-09-20", social=4, workouts=1), encoding="utf-8"
        )
        data = copy.deepcopy(BASE_DATA)
        before = copy.deepcopy(data["weeklyHistory"][0])
        changed, summaries = sync_data(data, collect_notes(self.daily))

        self.assertFalse(changed)
        self.assertEqual(summaries, [])
        self.assertEqual(data["weeklyHistory"][0], before)

    def test_managed_history_week_can_be_backfilled(self):
        (self.daily / "monday.md").write_text(
            note("2026-09-21", social=4, workouts=1), encoding="utf-8"
        )
        data = copy.deepcopy(BASE_DATA)
        managed_history = copy.deepcopy(data["currentWeek"])
        managed_history["week"] = "2026-W39"
        data["weeklyHistory"].insert(0, managed_history)
        data["currentWeek"] = {
            "startDate": "2026-09-28",
            "endDate": "2026-10-04",
            "metrics": {"pullRequests": 0},
        }

        changed, _ = sync_data(data, collect_notes(self.daily))
        history = data["weeklyHistory"][0]["metrics"]
        self.assertTrue(changed)
        self.assertEqual(history["socialContent"], {"total": 4})
        self.assertEqual(history["userSessions"], 0)
        self.assertEqual(history["workouts"], {"total": 1})
        self.assertEqual(history["pullRequests"], 8)

    def test_week_without_any_review_block_is_preserved(self):
        (self.daily / "old.md").write_text(
            note("2026-01-01", social=99), encoding="utf-8"
        )
        data = copy.deepcopy(BASE_DATA)
        before = copy.deepcopy(data)
        changed, summaries = sync_data(data, collect_notes(self.daily))
        self.assertFalse(changed)
        self.assertEqual(summaries, [])
        self.assertEqual(data, before)

    def test_editing_a_note_recalculates_the_total(self):
        path = self.daily / "monday.md"
        path.write_text(note("2026-09-21", social=2), encoding="utf-8")
        data = copy.deepcopy(BASE_DATA)
        sync_data(data, collect_notes(self.daily))
        self.assertEqual(
            data["currentWeek"]["metrics"]["socialContent"], {"total": 2}
        )

        path.write_text(note("2026-09-21", social=7), encoding="utf-8")
        changed, _ = sync_data(data, collect_notes(self.daily))
        self.assertTrue(changed)
        self.assertEqual(
            data["currentWeek"]["metrics"]["socialContent"], {"total": 7}
        )

    def test_conflicting_duplicate_dates_fail_closed(self):
        (self.daily / "a.md").write_text(
            note("2026-09-21", social=1), encoding="utf-8"
        )
        (self.daily / "b.md").write_text(
            note("2026-09-21", social=2), encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "conflicting reviews"):
            collect_notes(self.daily)

    def test_malformed_review_block_fails_closed(self):
        path = self.daily / "bad.md"
        path.write_text(
            note("2026-09-21", social=1).replace("- 운동: ", "- 운동함: "),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "malformed"):
            parse_note(path)


if __name__ == "__main__":
    unittest.main()
