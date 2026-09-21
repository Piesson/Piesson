import os
import unittest
from unittest.mock import patch

from tests.conftest import fake_http_response
from get_weekly_pull_requests import get_pull_requests_for_range, utc_range


class PullRequestWeekWindowTests(unittest.TestCase):
    def test_kst_week_converts_to_exact_utc_window(self):
        self.assertEqual(
            utc_range("2026-09-14", "2026-09-20"),
            ("2026-09-13T15:00:00Z", "2026-09-20T14:59:59Z"),
        )

    def test_bad_range_returns_none(self):
        self.assertIsNone(utc_range("not-a-date", "2026-09-20"))
        self.assertIsNone(utc_range("2026-09-20", "2026-09-14"))


class PullRequestCountTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "test-token", "USERNAME": "Piesson"},
            clear=False,
        )
        self.env.start()

    def tearDown(self):
        self.env.stop()

    @patch("get_weekly_pull_requests.requests.get")
    def test_search_query_and_count(self, get):
        get.return_value = fake_http_response(200, {"total_count": 77, "items": []})
        result = get_pull_requests_for_range("2026-09-14", "2026-09-20")
        self.assertEqual(result, 77)
        query = get.call_args.kwargs["params"]["q"]
        self.assertIn("author:Piesson is:pr is:merged", query)
        self.assertIn(
            "merged:2026-09-13T15:00:00Z..2026-09-20T14:59:59Z", query
        )

    @patch("get_weekly_pull_requests.requests.get")
    def test_api_failure_returns_none(self, get):
        get.return_value = fake_http_response(403, {"message": "rate limit"})
        self.assertIsNone(
            get_pull_requests_for_range("2026-09-14", "2026-09-20")
        )

    def test_missing_token_returns_none(self):
        with patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "", "SUMMARY_CARDS_TOKEN": "", "GH_TOKEN": ""},
        ):
            self.assertIsNone(
                get_pull_requests_for_range("2026-09-14", "2026-09-20")
            )


if __name__ == "__main__":
    unittest.main()
