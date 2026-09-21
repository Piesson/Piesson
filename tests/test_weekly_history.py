import copy
import unittest

from tests import conftest  # noqa: F401
from check_weekly_reset import reset_current_week_metrics, save_to_history
from generate_weekly_history import generate_history_svg


ENTRY = {
    "week": "2026-W39",
    "startDate": "2026-09-21",
    "endDate": "2026-09-27",
    "metrics": {
        "pullRequests": 3,
        "socialContent": {"total": 0},
        "userSessions": 0,
        "ctoMeetings": 0,
        "workouts": {"total": 0},
        "blogPosts": 0,
    },
}


class WeeklyHistoryTests(unittest.TestCase):
    def test_total_schema_uses_source_marker_without_name_error(self):
        managed = copy.deepcopy(ENTRY)
        managed["manualMetricsSource"] = "daily-notes"
        self.assertIn("Filed from daily notes", generate_history_svg(managed))
        self.assertIn("Legacy aggregate", generate_history_svg(copy.deepcopy(ENTRY)))

    def test_reset_archives_then_clears_source_marker(self):
        current = copy.deepcopy(ENTRY)
        current.pop("week")
        current["manualMetricsSource"] = "daily-notes"
        data = {"currentWeek": current, "weeklyHistory": []}
        current_info = {"monday": "2026-09-28", "sunday": "2026-10-04"}

        self.assertTrue(save_to_history(data, current_info))
        self.assertEqual(data["weeklyHistory"][0]["manualMetricsSource"], "daily-notes")

        reset_current_week_metrics(data)
        self.assertNotIn("manualMetricsSource", data["currentWeek"])


if __name__ == "__main__":
    unittest.main()
