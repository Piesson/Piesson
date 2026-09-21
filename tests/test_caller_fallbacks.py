"""Caller-fallback tests for generate_svg.py.

May 1 2026 incident: GitHub GraphQL secondary rate-limit returned an `errors`
payload, get_weekly_commits silently coerced the failure to 0, and
generate_svg.py wrote that 0 into data.json — turning a transient API blip
into permanent data corruption that got committed to git.

After the T3 refactor get_weekly_commits returns Optional[int] (None on any
failure). This test pins the contract that generate_svg MUST treat None as
"keep the existing value", never as zero.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Triggers conftest's sys.path insert so dashboard/ modules are importable.
from tests import conftest  # noqa: F401


SAMPLE_DATA = {
    "lastUpdated": "2026-04-30",
    "currentWeek": {
        "startDate": "2026-04-27",
        "endDate": "2026-05-03",
        "metrics": {
            "commits": 23,
            "socialContent": {"instagram": 0, "tiktok": 0, "hellotalk": 6},
            "userSessions": 2,
            "ctoMeetings": 2,
            "blogPosts": 0,
            "workouts": {"running": 2, "gym": 2},
        },
    },
    "weeklyHistory": [],
    "goals": {"weeklyCommits": 140},
}


class GenerateSvgPreservesCommitsOnApiFailure(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "dashboard").mkdir()
        (self.tmp / "dashboard" / "data.json").write_text(json.dumps(SAMPLE_DATA))
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp)

    def _reload_modules(self):
        # Force re-import so generate_svg picks up the patched get_weekly_commits.
        for m in ("generate_svg", "get_weekly_commits"):
            sys.modules.pop(m, None)

    def test_keeps_existing_commits_when_api_returns_none(self):
        self._reload_modules()
        with patch("get_weekly_commits.get_weekly_commits", return_value=None):
            import generate_svg  # noqa: F401
            generate_svg.generate_dashboard_svg()
        d = json.loads((self.tmp / "dashboard" / "data.json").read_text())
        self.assertEqual(
            d["currentWeek"]["metrics"]["commits"],
            23,
            "commits MUST stay 23 when API returns None — never overwritten with 0",
        )

    def test_overwrites_with_real_value_when_api_succeeds(self):
        self._reload_modules()
        with patch("get_weekly_commits.get_weekly_commits", return_value=42):
            import generate_svg  # noqa: F401
            generate_svg.generate_dashboard_svg()
        d = json.loads((self.tmp / "dashboard" / "data.json").read_text())
        self.assertEqual(d["currentWeek"]["metrics"]["commits"], 42)


class ProfileCardKeepsPreviousSvgOnGraphqlFailure(unittest.TestCase):
    """2026-07-18 incident: the vn7n24fzkq action exhausted the hourly
    GraphQL quota, the custom card's query 403'd, and a REST-sampling
    fallback silently rendered 253 instead of 6,913. The card must follow
    the same None contract as everything else: API failure → keep the
    previous file untouched."""

    SENTINEL = "<svg><!-- previous good card 6,913 --></svg>"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        card_dir = self.tmp / "profile-summary-card-output" / "default"
        card_dir.mkdir(parents=True)
        self.card = card_dir / "0-profile-details.svg"
        self.card.write_text(self.SENTINEL)
        (self.tmp / "README.md").write_text("# readme\n")
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp)

    def test_graphql_failure_leaves_card_untouched(self):
        import sys
        sys.modules.pop("generate_profile_card", None)
        import generate_profile_card as gpc
        with patch.object(gpc, "get_github_activity_stats_graphql", return_value=None):
            gpc.generate_profile_card()
        self.assertEqual(self.card.read_text(), self.SENTINEL)
        self.assertEqual((self.tmp / "README.md").read_text(), "# readme\n")

    def test_graphql_success_regenerates_card(self):
        import sys
        sys.modules.pop("generate_profile_card", None)
        import generate_profile_card as gpc
        stats = {"commits": 6913, "code_reviews": 30, "pull_requests": 20, "issues": 10}
        with patch.object(gpc, "get_github_activity_stats_graphql", return_value=stats):
            gpc.generate_profile_card()
        self.assertIn("6,913", self.card.read_text())


if __name__ == "__main__":
    unittest.main()
