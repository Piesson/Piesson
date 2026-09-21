import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from tests import conftest  # noqa: F401
import generate_progress_chart
import generate_svg


SVG_NS = "{http://www.w3.org/2000/svg}"


def sample_data():
    history = []
    for week in range(27, 38):
        history.append({
            "week": f"2026-W{week}",
            "startDate": f"2026-07-{week - 20:02d}",
            "endDate": f"2026-07-{week - 14:02d}",
            "metrics": {
                "pullRequests": week - 26,
                "socialContent": {"instagram": 1, "tiktok": 0, "hellotalk": 0},
                "userSessions": 2,
                "ctoMeetings": 1,
                "blogPosts": 1,
                "workouts": {"running": 1, "gym": 2},
            },
        })
    # Generators reverse stored history, so keep newest first like data.json.
    history.reverse()
    return {
        "lastUpdated": "2026-09-20",
        "currentWeek": {
            "startDate": "2026-09-14",
            "endDate": "2026-09-20",
            "metrics": {
                "pullRequests": 12,
                "commits": 1,
                "socialContent": {"total": 1},
                "userSessions": 2,
                "ctoMeetings": 1,
                "blogPosts": 1,
                "workouts": {"total": 3},
            },
        },
        "weeklyHistory": history,
    }


class DashboardLayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.data = self.root / "data.json"
        self.data.write_text(json.dumps(sample_data()))

    def tearDown(self):
        self.tmp.cleanup()

    def test_weekly_bars_start_below_series_labels_and_section_rule(self):
        out = self.root / "weekly.svg"
        with patch.object(generate_svg, "DATA", self.data), \
             patch.object(generate_svg, "OUT", out), \
             patch("get_weekly_commits.get_weekly_commits", return_value=None), \
             patch("get_weekly_pull_requests.get_weekly_pull_requests", return_value=None):
            generate_svg.generate_dashboard_svg()

        root = ET.parse(out).getroot()
        texts = [e for e in root.findall(f"{SVG_NS}text")]
        labels = {
            e.text: float(e.attrib["y"])
            for e in texts
            if e.text in {"TWELVE WEEKS", "Pull requests merged", "Social posts"}
            and float(e.attrib["y"]) > 400
        }
        bars = [
            e for e in root.findall(f"{SVG_NS}rect")
            if "x" in e.attrib and "y" in e.attrib
        ]
        self.assertEqual(len(bars), 24)

        first, second = bars[:12], bars[12:]
        self.assertGreaterEqual(
            min(float(e.attrib["y"]) for e in first),
            labels["Pull requests merged"] + 12,
        )
        self.assertGreaterEqual(
            min(float(e.attrib["y"]) for e in second),
            labels["Social posts"] + 12,
        )
        self.assertGreater(
            min(float(e.attrib["y"]) for e in bars),
            labels["TWELVE WEEKS"] + 14,
        )

    def test_hand_filed_figures_are_twelve_week_totals(self):
        out = self.root / "totals.svg"
        with patch.object(generate_progress_chart, "DATA", self.data), \
             patch.object(generate_progress_chart, "OUT", out):
            generate_progress_chart.generate_progress_chart()

        root = ET.parse(out).getroot()
        texts = root.findall(f"{SVG_NS}text")
        by_y = {}
        for element in texts:
            by_y.setdefault(element.attrib["y"], []).append(element.text)

        expected = {
            "Workouts": "36",
            "Coffee chats": "12",
            "Talks with users": "24",
            "Blog posts": "12",
        }
        for label, total in expected.items():
            row = next(values for values in by_y.values() if label in values)
            self.assertIn(total, row, f"{label} should show its 12-week total")

        svg = out.read_text()
        self.assertIn("ALSO FILED BY HAND · TWELVE-WEEK TOTALS", svg)
        self.assertNotIn("The top figure is counted", svg)
        self.assertNotIn("The number is the review", svg)


if __name__ == "__main__":
    unittest.main()
