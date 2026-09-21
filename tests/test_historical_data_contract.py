import json
import unittest
from pathlib import Path

from tests import conftest  # noqa: F401
from metric_totals import grouped_total


class HistoricalDataContractTests(unittest.TestCase):
    def test_retained_social_baseline_is_not_reconstructed_from_stale_svgs(self):
        data_path = Path(__file__).parents[1] / "dashboard" / "data.json"
        data = json.loads(data_path.read_text(encoding="utf-8"))
        by_week = {entry["week"]: entry for entry in data["weeklyHistory"]}
        # The source snapshot is still in W38 until the first production reset.
        if data["currentWeek"].get("startDate") == "2026-09-14":
            by_week["2026-W38"] = data["currentWeek"]

        expected = {"2026-W27": 11}
        expected.update({f"2026-W{week:02d}": 10 for week in range(28, 39)})
        # weeklyHistory is intentionally rolling. Enforce the baseline only while
        # protected weeks remain, then report an explicit skip instead of a false pass.
        if not set(expected) & set(by_week):
            self.skipTest("baseline weeks fully rolled out; retire this migration guard")
        for week_id, expected_total in expected.items():
            entry = by_week.get(week_id)
            if entry is None:
                continue
            with self.subTest(week=week_id):
                social = entry["metrics"]["socialContent"]
                self.assertEqual(grouped_total(social), expected_total)


if __name__ == "__main__":
    unittest.main()
