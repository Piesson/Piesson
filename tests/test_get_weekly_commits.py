import os
import unittest
from unittest.mock import patch
from tests.conftest import fake_http_response

import get_weekly_commits as gwc
from _graphql_client import ErrorKind


class GetWeeklyCommitsReturnsOptionalInt(unittest.TestCase):
    def setUp(self):
        os.environ["GITHUB_TOKEN"] = "x"
        os.environ["USERNAME"] = "Piesson"

    def tearDown(self):
        os.environ.pop("GITHUB_TOKEN", None)
        os.environ.pop("USERNAME", None)

    def test_returns_int_on_success(self):
        body = {"data": {"user": {"contributionsCollection": {"totalCommitContributions": 23}}}}
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, body)):
            self.assertEqual(gwc.get_weekly_commits(), 23)

    def test_returns_none_on_rate_limit(self):
        body = {"errors": [{"type": "RATE_LIMIT", "message": "..."}]}
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, body)):
            self.assertIsNone(gwc.get_weekly_commits())

    def test_returns_none_on_missing_token(self):
        os.environ.pop("GITHUB_TOKEN", None)
        os.environ.pop("SUMMARY_CARDS_TOKEN", None)
        self.assertIsNone(gwc.get_weekly_commits())

    def test_returns_none_on_network_error(self):
        import requests
        with patch("_graphql_client.requests.post",
                   side_effect=requests.ConnectionError("boom")):
            self.assertIsNone(gwc.get_weekly_commits())

    def test_zero_commits_is_int_zero_not_none(self):
        body = {"data": {"user": {"contributionsCollection": {"totalCommitContributions": 0}}}}
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, body)):
            v = gwc.get_weekly_commits()
        self.assertEqual(v, 0)
        self.assertIsNotNone(v)  # CRITICAL: real 0 must NOT collapse to None


class WeekWindowStartsAtMidnight(unittest.TestCase):
    def test_window_truncates_to_monday_midnight_kst(self):
        """Regression: the window used to start at Monday <run's time-of-day>,
        dropping every commit made earlier in the day."""
        from datetime import datetime
        now = datetime(2026, 7, 14, 22, 50, 0, tzinfo=gwc.KST)  # Tue 22:50 KST
        from_iso, to_iso = gwc._week_window_utc(now)
        # Monday 2026-07-13 00:00 KST == Sunday 2026-07-12 15:00 UTC
        self.assertEqual(from_iso, "2026-07-12T15:00:00Z")
        # Sunday 2026-07-19 23:59:59 KST == 2026-07-19 14:59:59 UTC
        self.assertEqual(to_iso, "2026-07-19T14:59:59Z")


class GetCommitsForRange(unittest.TestCase):
    def setUp(self):
        os.environ["GITHUB_TOKEN"] = "x"
        os.environ["USERNAME"] = "Piesson"

    def tearDown(self):
        os.environ.pop("GITHUB_TOKEN", None)
        os.environ.pop("USERNAME", None)

    def test_range_converts_kst_dates_to_utc_window(self):
        body = {"data": {"user": {"contributionsCollection": {"totalCommitContributions": 174}}}}
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, body)) as mock_post:
            v = gwc.get_commits_for_range("2026-07-06", "2026-07-12")
        self.assertEqual(v, 174)
        variables = mock_post.call_args.kwargs.get("json", mock_post.call_args.args[-1])["variables"]
        # 2026-07-06 00:00 KST == 2026-07-05 15:00 UTC
        self.assertEqual(variables["from"], "2026-07-05T15:00:00Z")
        # 2026-07-12 23:59:59 KST == 2026-07-12 14:59:59 UTC
        self.assertEqual(variables["to"], "2026-07-12T14:59:59Z")

    def test_bad_dates_return_none(self):
        self.assertIsNone(gwc.get_commits_for_range("not-a-date", "2026-07-12"))
        self.assertIsNone(gwc.get_commits_for_range("2026-07-06", None))


if __name__ == "__main__":
    unittest.main()
