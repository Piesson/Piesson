"""Tests for the past-year disk cache (_yearly_cache) and graphql_stats integration."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

DASHBOARD = Path(__file__).resolve().parent.parent / "dashboard"
sys.path.insert(0, str(DASHBOARD))


class YearlyCacheBehavior(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.cache_path = self.tmp / ".stats_cache.json"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_missing_file_returns_empty(self):
        from _yearly_cache import load_cache
        c = load_cache(self.cache_path)
        self.assertEqual(c, {"version": 1, "years": {}})

    def test_corrupt_file_returns_empty(self):
        self.cache_path.write_text("not json")
        from _yearly_cache import load_cache
        self.assertEqual(load_cache(self.cache_path),
                         {"version": 1, "years": {}})

    def test_save_then_load_roundtrip(self):
        from _yearly_cache import save_cache, load_cache
        cache = {"version": 1, "years": {"2020": {
            "commits": 100, "code_reviews": 1, "pull_requests": 2, "issues": 3,
            "computed_in_year": 2026,
        }}}
        save_cache(self.cache_path, cache)
        self.assertEqual(load_cache(self.cache_path), cache)

    def test_uses_cache_for_completed_year(self):
        from _yearly_cache import is_cache_authoritative
        entry = {"computed_in_year": 2026}
        self.assertTrue(is_cache_authoritative(year=2025, current_year=2026, entry=entry))

    def test_invalidates_when_computed_in_same_year(self):
        from _yearly_cache import is_cache_authoritative
        entry = {"computed_in_year": 2025}
        self.assertFalse(is_cache_authoritative(year=2025, current_year=2026, entry=entry))

    def test_never_caches_current_year(self):
        from _yearly_cache import is_cache_authoritative
        self.assertFalse(is_cache_authoritative(year=2026, current_year=2026,
                                                entry={"computed_in_year": 2026}))


class GraphqlStatsUsesCache(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.cache_path = self.tmp / ".stats_cache.json"
        # pre-seed cache: 2020-2025 known, only 2026 needs API
        cache = {
            "version": 1,
            "years": {
                str(y): {
                    "commits": 10, "code_reviews": 2, "pull_requests": 1, "issues": 3,
                    "computed_in_year": 2026,
                } for y in range(2020, 2026)
            },
        }
        self.cache_path.write_text(json.dumps(cache))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_only_current_year_queried(self):
        from unittest.mock import patch
        from tests.conftest import fake_http_response
        body = {"data": {"user": {
            "y2026": {
                "totalCommitContributions": 99,
                "totalPullRequestContributions": 9,
                "totalPullRequestReviewContributions": 8,
                "totalIssueContributions": 7,
            }
        }}}
        for m in ("graphql_stats",):
            sys.modules.pop(m, None)
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, body)) as p:
            import graphql_stats
            with patch.object(graphql_stats, "CACHE_PATH", self.cache_path):
                stats = graphql_stats.get_github_activity_stats_graphql(
                    "Piesson", "tok", current_year=2026)
        self.assertEqual(p.call_count, 1)
        # 6 cached years x 10 + current year 99 = 159
        self.assertEqual(stats["commits"], 159)


if __name__ == "__main__":
    unittest.main()
