import unittest

from tests import conftest  # noqa: F401
from metric_totals import grouped_total


class GroupedTotalTests(unittest.TestCase):
    def test_legacy_detail_keys_are_summed(self):
        self.assertEqual(
            grouped_total({"instagram": 1, "tiktok": 2, "hellotalk": 3}), 6
        )

    def test_explicit_total_is_authoritative(self):
        self.assertEqual(grouped_total({"total": 4, "instagram": 99}), 4)

    def test_scalar_legacy_value_is_supported(self):
        self.assertEqual(grouped_total(5), 5)

    def test_invalid_or_negative_values_do_not_reduce_total(self):
        self.assertEqual(grouped_total({"a": -2, "b": "3", "c": True}), 0)


if __name__ == "__main__":
    unittest.main()
