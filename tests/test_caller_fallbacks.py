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


class GenerateSlackMessageFallback(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "dashboard").mkdir()
        (self.tmp / "dashboard" / "data.json").write_text(json.dumps(SAMPLE_DATA))
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp)

    def test_uses_data_json_commits_when_api_none(self):
        for m in ("generate_slack_message", "get_weekly_commits"):
            sys.modules.pop(m, None)
        with patch("get_weekly_commits.get_weekly_commits", return_value=None):
            import generate_slack_message as gsm
            m = gsm.load_current_metrics()
        self.assertEqual(m["commits"], 23)
        self.assertTrue(m.get("commits_is_cached"), "must mark commits as cached fallback")

    def test_fresh_value_when_api_succeeds(self):
        for m in ("generate_slack_message", "get_weekly_commits"):
            sys.modules.pop(m, None)
        with patch("get_weekly_commits.get_weekly_commits", return_value=99):
            import generate_slack_message as gsm
            m = gsm.load_current_metrics()
        self.assertEqual(m["commits"], 99)
        self.assertFalse(m.get("commits_is_cached"))


class SlackUpdateConfirmationUsesDataJson(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "dashboard").mkdir()
        (self.tmp / "dashboard" / "data.json").write_text(json.dumps(SAMPLE_DATA))
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp)

    def test_confirmation_reads_commits_from_data_json_no_api_call(self):
        for m in ("slack_update", "get_weekly_commits"):
            sys.modules.pop(m, None)
        # If anyone calls get_weekly_commits, this test fails loudly
        from unittest.mock import MagicMock
        spy = MagicMock(side_effect=AssertionError("must NOT call API in confirmation"))
        with patch("get_weekly_commits.get_weekly_commits", spy), \
             patch("slack_update.requests.post") as post:
            post.return_value.status_code = 200
            import slack_update
            os.environ["SLACK_WEBHOOK_URL"] = "https://example.invalid/x"
            result = slack_update.update_data({
                "instagram": 0, "tiktok": 0, "hellotalk": 0,
                "usertalks": 0, "coffeechats": 0, "blogposts": 0,
                "running": 0, "gym": 0,
            })
            slack_update.send_confirmation_message(os.environ["SLACK_WEBHOOK_URL"], result)
            os.environ.pop("SLACK_WEBHOOK_URL", None)
        # Inspect the slack body
        sent_body = post.call_args.kwargs["json"]["text"]
        self.assertIn("Code Commits: 23", sent_body)
        spy.assert_not_called()


class SlackResponseFlowDoesOneApiCall(unittest.TestCase):
    """Simulates: slack_update.py -> generate_svg.py.
    Asserts get_weekly_commits is invoked at most ONCE across both."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "dashboard").mkdir()
        (self.tmp / "dashboard" / "data.json").write_text(json.dumps(SAMPLE_DATA))
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp)

    def test_one_call_total(self):
        for m in ("slack_update", "generate_svg", "get_weekly_commits"):
            sys.modules.pop(m, None)

        from unittest.mock import MagicMock
        spy = MagicMock(return_value=42)

        with patch("get_weekly_commits.get_weekly_commits", spy), \
             patch("slack_update.requests.post"):
            os.environ["SLACK_WEBHOOK_URL"] = "https://example.invalid/x"
            import slack_update
            metrics = {"instagram": 0, "tiktok": 0, "hellotalk": 0,
                       "usertalks": 0, "coffeechats": 0, "blogposts": 0,
                       "running": 0, "gym": 0}
            r = slack_update.update_data(metrics)
            slack_update.send_confirmation_message(os.environ["SLACK_WEBHOOK_URL"], r)

            import generate_svg
            generate_svg.generate_dashboard_svg()
            os.environ.pop("SLACK_WEBHOOK_URL", None)

        self.assertEqual(spy.call_count, 1,
                         f"expected exactly 1 GraphQL call across the full flow, got {spy.call_count}")


class SlackMessageShowsCachedSuffix(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "dashboard").mkdir()
        (self.tmp / "dashboard" / "data.json").write_text(json.dumps(SAMPLE_DATA))
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp)

    def test_shows_cached_suffix_on_api_failure(self):
        import sys
        for m in ("generate_slack_message", "get_weekly_commits"):
            sys.modules.pop(m, None)
        with patch("get_weekly_commits.get_weekly_commits", return_value=None):
            import generate_slack_message as gsm
            payload = json.loads(gsm.generate_slack_message("morning"))
        self.assertIn("23", payload["text"])
        self.assertIn("(cached — API unavailable)", payload["text"])

    def test_no_suffix_on_api_success(self):
        import sys
        for m in ("generate_slack_message", "get_weekly_commits"):
            sys.modules.pop(m, None)
        with patch("get_weekly_commits.get_weekly_commits", return_value=99):
            import generate_slack_message as gsm
            payload = json.loads(gsm.generate_slack_message("morning"))
        self.assertIn("99", payload["text"])
        self.assertNotIn("cached", payload["text"])


if __name__ == "__main__":
    unittest.main()
