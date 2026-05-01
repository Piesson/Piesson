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


if __name__ == "__main__":
    unittest.main()
