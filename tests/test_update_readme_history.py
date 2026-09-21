import json
import os
import tempfile
import unittest
from pathlib import Path

from tests import conftest  # noqa: F401
import update_readme_history


class UpdateReadmeHistoryEndToEndTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "dashboard").mkdir()
        (self.root / "README.md").write_text(
            "# Profile\n\n# Tech Stack\n\ncontent\n", encoding="utf-8"
        )
        data = {
            "currentWeek": {
                "startDate": "2026-09-21",
                "endDate": "2026-09-27",
                "metrics": {
                    "pullRequests": 12,
                    "socialContent": {"total": 2},
                    "userSessions": 1,
                    "ctoMeetings": 0,
                    "workouts": {"total": 1},
                    "blogPosts": 0,
                },
            },
            "weeklyHistory": [
                {
                    "week": "2026-W38",
                    "startDate": "2026-09-14",
                    "endDate": "2026-09-20",
                    "metrics": {
                        "pullRequests": 77,
                        "socialContent": {"instagram": 0, "tiktok": 10},
                        "userSessions": 1,
                        "ctoMeetings": 1,
                        "workouts": {"running": 1, "gym": 1},
                        "blogPosts": 1,
                    },
                }
            ],
        }
        (self.root / "dashboard" / "data.json").write_text(
            json.dumps(data), encoding="utf-8"
        )
        self.old_cwd = Path.cwd()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp.cleanup()

    def test_updates_history_without_legacy_quickchart_variables(self):
        self.assertTrue(update_readme_history.update_readme_with_history())
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("# Weekly History", readme)
        self.assertIn("Week 39 (live)", readme)
        self.assertIn("| 12 | 2 | 1 | 0 | 1 | 0 |", readme)
        self.assertIn("Week 38", readme)
        self.assertNotIn("image-charts.com", readme)

    def test_managed_week_displays_honest_zeroes_instead_of_missing_dashes(self):
        current = {
            "startDate": "2026-09-21",
            "endDate": "2026-09-27",
            "manualMetricsSource": "daily-notes",
            "metrics": {"pullRequests": 3},
        }
        table = update_readme_history.generate_history_table([], current_week=current)
        self.assertIn("| 3 | 0 | 0 | 0 | 0 | 0 |", table)


if __name__ == "__main__":
    unittest.main()
