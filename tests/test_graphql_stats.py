"""Tests for graphql_stats: aliased single-request yearly contributions."""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tests.conftest import fake_http_response


class GraphqlStatsAliasedQuery(unittest.TestCase):
    def setUp(self):
        # Isolate from the committed dashboard/.stats_cache.json so T7 mock data
        # doesn't pollute it. CACHE_PATH is patched to a tempdir per-test.
        self.tmp = Path(tempfile.mkdtemp())
        self.cache_path = self.tmp / ".stats_cache.json"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_single_request_with_yearly_aliases(self):
        # The endpoint should be called exactly ONCE,
        # and the response should contain aliased keys y2020..y2026.
        body = {"data": {"user": {
            f"y{y}": {
                "totalCommitContributions": 10,
                "totalPullRequestContributions": 1,
                "totalPullRequestReviewContributions": 2,
                "totalIssueContributions": 3,
            } for y in range(2020, 2027)
        }}}
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, body)) as p:
            import graphql_stats
            with patch.object(graphql_stats, "CACHE_PATH", self.cache_path):
                stats = graphql_stats.get_github_activity_stats_graphql(
                    "Piesson", "tok", current_year=2026)
        self.assertEqual(p.call_count, 1, "must use a single aliased GraphQL request")
        # 7 years x 10 commits each
        self.assertEqual(stats["commits"], 70)
        self.assertEqual(stats["pull_requests"], 7)
        self.assertEqual(stats["code_reviews"], 14)
        self.assertEqual(stats["issues"], 21)

    def test_returns_none_on_api_failure(self):
        body = {"errors": [{"type": "RATE_LIMIT", "message": "..."}]}
        # RATE_LIMIT does not retry, so no need to patch time.sleep
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, body)):
            import graphql_stats
            with patch.object(graphql_stats, "CACHE_PATH", self.cache_path):
                self.assertIsNone(graphql_stats.get_github_activity_stats_graphql(
                    "Piesson", "tok", current_year=2026))


if __name__ == "__main__":
    unittest.main()
