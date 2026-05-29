"""Unit tests for weekly_history backfill in get_weekly_tokens.py.

Verifies that stale entries (snapshotted before week's natural close at
Mon 00:00 KST after endDate) get re-queried via ccusage; complete entries
are left untouched (idempotent); and safety preserves non-zero values when
re-query returns zero (defensive against transient ccusage failures).
"""

import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

# conftest side-effect: inserts dashboard/ into sys.path so we can import
# get_weekly_tokens directly. Other tests use the same pattern.
from tests import conftest  # noqa: F401

import get_weekly_tokens as gwt

KST = timezone(timedelta(hours=9))


def make_entry(week, start, end, tokens=None, **metric_overrides):
    """Build a weeklyHistory entry. tokens=None → no tokens block."""
    metrics = {
        "commits": 0,
        "socialContent": {"instagram": 0, "tiktok": 0, "hellotalk": 0},
        "userSessions": 0,
        "ctoMeetings": 0,
        "blogPosts": 0,
        "workouts": {"running": 0, "gym": 0},
    }
    metrics.update(metric_overrides)
    if tokens is not None:
        metrics["tokens"] = tokens
    return {"week": week, "startDate": start, "endDate": end, "metrics": metrics}


class TestStaleDetection(unittest.TestCase):
    """Entries are stale when updatedAt < endDate + 1 day @ 00:00 KST."""

    def test_no_tokens_block_is_stale(self):
        entry = make_entry("2026-W17", "2026-04-20", "2026-04-26")  # no tokens
        self.assertTrue(gwt.is_history_entry_stale(entry))

    def test_no_updatedAt_is_stale(self):
        entry = make_entry(
            "2026-W17", "2026-04-20", "2026-04-26",
            tokens={"claude": 100, "codex": 0, "total": 100},
        )
        self.assertTrue(gwt.is_history_entry_stale(entry))

    def test_updatedAt_mid_week_is_stale(self):
        """W19 real-world bug: updatedAt = 2026-05-06 00:05, endDate = 5/10.
        Boundary = 2026-05-11 00:00 KST. 5/6 < 5/11 → STALE."""
        entry = make_entry(
            "2026-W19", "2026-05-04", "2026-05-10",
            tokens={
                "claude": 804497540, "codex": 22658397, "total": 827155937,
                "updatedAt": "2026-05-06T00:05:20+09:00",
            },
        )
        self.assertTrue(gwt.is_history_entry_stale(entry))

    def test_updatedAt_after_boundary_is_complete(self):
        entry = make_entry(
            "2026-W17", "2026-04-20", "2026-04-26",
            tokens={
                "claude": 100, "codex": 0, "total": 100,
                # Mon 4/27 12:00 KST = after boundary (4/27 00:00 KST)
                "updatedAt": "2026-04-27T12:00:00+09:00",
            },
        )
        self.assertFalse(gwt.is_history_entry_stale(entry))

    def test_updatedAt_sunday_2359_is_stale(self):
        """Edge case: wrapper ran Sun 23:59 of the week.
        updatedAt < Mon 00:00 boundary → flagged stale (will re-query).
        Practically idempotent — re-query returns ~same value."""
        entry = make_entry(
            "2026-W19", "2026-05-04", "2026-05-10",
            tokens={
                "claude": 1098000000, "codex": 36000000, "total": 1134000000,
                "updatedAt": "2026-05-10T23:59:00+09:00",
            },
        )
        self.assertTrue(gwt.is_history_entry_stale(entry))

    def test_mm_dd_yyyy_date_format(self):
        """Legacy entries have MM/DD/YYYY in start/endDate."""
        entry = make_entry(
            "2025-W43", "10/20/2025", "10/26/2025",
            tokens={
                "claude": 100, "codex": 0, "total": 100,
                "updatedAt": "2025-10-27T12:00:00+09:00",  # after Mon 10/27 00:00
            },
        )
        self.assertFalse(gwt.is_history_entry_stale(entry))

    def test_unparseable_date_skipped(self):
        entry = make_entry("?", "not-a-date", "also-not", tokens={"claude": 100})
        # Can't parse → don't risk re-querying (return False = skip)
        self.assertFalse(gwt.is_history_entry_stale(entry))


class TestBackfill(unittest.TestCase):
    """The actual re-query loop. Mock fetch_claude / fetch_codex."""

    def _mk_data(self, entries):
        return {"weeklyHistory": entries}

    def test_no_entries_no_calls(self):
        with patch.object(gwt, "fetch_claude") as mc, \
             patch.object(gwt, "fetch_codex") as mx:
            data = self._mk_data([])
            self.assertEqual(gwt.backfill_weekly_history(data), 0)
            mc.assert_not_called()
            mx.assert_not_called()

    def test_complete_entries_skipped(self):
        """Idempotency: complete entries don't trigger ccusage."""
        with patch.object(gwt, "fetch_claude") as mc, \
             patch.object(gwt, "fetch_codex") as mx:
            data = self._mk_data([
                make_entry(
                    "2026-W17", "2026-04-20", "2026-04-26",
                    tokens={
                        "claude": 100, "codex": 0, "total": 100,
                        "updatedAt": "2026-04-28T12:00:00+09:00",
                    },
                ),
            ])
            n = gwt.backfill_weekly_history(data)
            self.assertEqual(n, 0)
            mc.assert_not_called()
            mx.assert_not_called()

    def test_stale_entry_gets_updated(self):
        """The W19 real-world scenario: stale entry re-queried + updated."""
        with patch.object(gwt, "fetch_claude", return_value=(1_098_135_370, True)) as mc, \
             patch.object(gwt, "fetch_codex", return_value=(36_474_284, True)) as mx:
            data = self._mk_data([
                make_entry(
                    "2026-W19", "2026-05-04", "2026-05-10",
                    tokens={
                        "claude": 804497540, "codex": 22658397, "total": 827155937,
                        "updatedAt": "2026-05-06T00:05:20+09:00",
                    },
                ),
            ])
            n = gwt.backfill_weekly_history(data)
            self.assertEqual(n, 1)
            mc.assert_called_once_with("2026-05-04", "2026-05-10")
            mx.assert_called_once_with("2026-05-04", "2026-05-10")
            new_tokens = data["weeklyHistory"][0]["metrics"]["tokens"]
            self.assertEqual(new_tokens["claude"], 1_098_135_370)
            self.assertEqual(new_tokens["codex"], 36_474_284)
            self.assertEqual(new_tokens["total"], 1_134_609_654)
            # updatedAt is rewritten to "now"
            self.assertTrue(new_tokens["updatedAt"].startswith("20"))

    def test_zero_query_preserves_nonzero(self):
        """Defensive: if ccusage returns 0 for an entry that had non-zero,
        KEEP the existing value. Could be transient ccusage breakage."""
        with patch.object(gwt, "fetch_claude", return_value=(0, True)), \
             patch.object(gwt, "fetch_codex", return_value=(0, True)):
            data = self._mk_data([
                make_entry(
                    "2026-W19", "2026-05-04", "2026-05-10",
                    tokens={
                        "claude": 800000000, "codex": 22000000, "total": 822000000,
                        "updatedAt": "2026-05-06T00:05:20+09:00",
                    },
                ),
            ])
            n = gwt.backfill_weekly_history(data)
            self.assertEqual(n, 0)  # not counted as backfilled
            tokens = data["weeklyHistory"][0]["metrics"]["tokens"]
            self.assertEqual(tokens["claude"], 800000000)  # preserved
            self.assertEqual(tokens["codex"], 22000000)

    def test_zero_query_ok_for_zero_entry(self):
        """Edge: if existing was 0 (e.g., Mac off that week) and re-query
        returns 0, accept the 0 (it's real)."""
        with patch.object(gwt, "fetch_claude", return_value=(0, True)), \
             patch.object(gwt, "fetch_codex", return_value=(0, True)):
            data = self._mk_data([
                make_entry(
                    "2026-W15", "2026-04-06", "2026-04-12",
                    tokens=None,  # no tokens block at all
                ),
            ])
            n = gwt.backfill_weekly_history(data)
            self.assertEqual(n, 1)
            tokens = data["weeklyHistory"][0]["metrics"]["tokens"]
            self.assertEqual(tokens["claude"], 0)
            self.assertEqual(tokens["codex"], 0)
            self.assertEqual(tokens["total"], 0)

    def test_partial_failure_uses_existing(self):
        """If claude succeeds but codex fails, keep codex's previous value."""
        with patch.object(gwt, "fetch_claude", return_value=(1_000_000_000, True)), \
             patch.object(gwt, "fetch_codex", return_value=(0, False)):
            data = self._mk_data([
                make_entry(
                    "2026-W19", "2026-05-04", "2026-05-10",
                    tokens={
                        "claude": 800_000_000, "codex": 22_000_000, "total": 822_000_000,
                        "updatedAt": "2026-05-06T00:05:20+09:00",
                    },
                ),
            ])
            n = gwt.backfill_weekly_history(data)
            self.assertEqual(n, 1)
            tokens = data["weeklyHistory"][0]["metrics"]["tokens"]
            self.assertEqual(tokens["claude"], 1_000_000_000)  # updated
            self.assertEqual(tokens["codex"], 22_000_000)      # preserved

    def test_both_sources_fail_skips_entry(self):
        """If both ccusage CLIs fail (e.g., offline), don't touch the entry."""
        with patch.object(gwt, "fetch_claude", return_value=(0, False)), \
             patch.object(gwt, "fetch_codex", return_value=(0, False)):
            data = self._mk_data([
                make_entry(
                    "2026-W19", "2026-05-04", "2026-05-10",
                    tokens={
                        "claude": 800_000_000, "codex": 22_000_000, "total": 822_000_000,
                        "updatedAt": "2026-05-06T00:05:20+09:00",
                    },
                ),
            ])
            n = gwt.backfill_weekly_history(data)
            self.assertEqual(n, 0)
            tokens = data["weeklyHistory"][0]["metrics"]["tokens"]
            self.assertEqual(tokens["claude"], 800_000_000)  # preserved

    def test_multiple_entries_mixed(self):
        """One stale, one complete → 1 call set, 1 skip."""
        with patch.object(gwt, "fetch_claude", return_value=(500, True)) as mc, \
             patch.object(gwt, "fetch_codex", return_value=(100, True)) as mx:
            data = self._mk_data([
                # Stale (W19)
                make_entry(
                    "2026-W19", "2026-05-04", "2026-05-10",
                    tokens={
                        "claude": 100, "codex": 0, "total": 100,
                        "updatedAt": "2026-05-06T00:05:20+09:00",
                    },
                ),
                # Complete (W18)
                make_entry(
                    "2026-W18", "2026-04-27", "2026-05-03",
                    tokens={
                        "claude": 200, "codex": 0, "total": 200,
                        "updatedAt": "2026-05-05T00:00:00+09:00",
                    },
                ),
            ])
            n = gwt.backfill_weekly_history(data)
            self.assertEqual(n, 1)
            # Only called for the stale entry
            self.assertEqual(mc.call_count, 1)
            self.assertEqual(mx.call_count, 1)
            mc.assert_called_with("2026-05-04", "2026-05-10")

    def test_mm_dd_yyyy_dates_normalized_for_ccusage(self):
        """Legacy MM/DD/YYYY entries get normalized before ccusage call."""
        with patch.object(gwt, "fetch_claude", return_value=(100, True)) as mc, \
             patch.object(gwt, "fetch_codex", return_value=(0, True)):
            data = self._mk_data([
                make_entry(
                    "2025-W43", "10/20/2025", "10/26/2025",
                    tokens=None,  # stale
                ),
            ])
            gwt.backfill_weekly_history(data)
            mc.assert_called_once_with("2025-10-20", "2025-10-26")


if __name__ == "__main__":
    unittest.main()
