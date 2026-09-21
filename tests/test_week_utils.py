import unittest
from datetime import date, datetime

from tests import conftest  # noqa: F401
from week_utils import iso_week_id


class IsoWeekIdTests(unittest.TestCase):
    def test_regular_week(self):
        self.assertEqual(iso_week_id(date(2026, 9, 21)), "2026-W39")

    def test_calendar_year_boundary_uses_iso_year(self):
        self.assertEqual(iso_week_id(date(2029, 12, 31)), "2030-W01")
        self.assertEqual(iso_week_id(datetime(2029, 12, 31)), "2030-W01")


if __name__ == "__main__":
    unittest.main()
