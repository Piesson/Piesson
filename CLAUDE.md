# CLAUDE.md

Guidance for agents working on the Piesson GitHub profile dashboard.

## Critical rules

1. Work in the Vault monorepo under `apps/piesson/`; do not edit the public mirror directly.
2. Code delivery is automatic after a Vault `main` push (`mirror-piesson.yml`).
3. Upstream-generated files are authoritative and must be preserved during mirror arbitration:
   - `README.md`
   - `dashboard/data.json`
   - `dashboard/weekly_dashboard.svg`
   - `dashboard/progress_sparklines.svg`
   - `dashboard/history/`
   - `.stats_cache.json`
   - `profile-summary-card-output/`
4. Never expose token totals on the public dashboard. Collection remains private data in `data.json`.
5. Verify dashboard changes with tests and a screenshot of the deployed public GitHub profile.

## Current systems

### 1. GitHub profile card

- Workflow: `.github/workflows/profile-summary-cards.yml`
- Generator: `dashboard/generate_profile_card.py`
- Stats: `dashboard/graphql_stats.py`, `dashboard/_graphql_client.py`
- Output: `profile-summary-card-output/default/0-profile-details.svg`
- Schedule: every six hours plus manual dispatch

### 2. Weekly dashboard

- Workflow: `.github/workflows/update_dashboard.yml`
- Current panel: `dashboard/generate_svg.py`
- Running totals panel: `dashboard/generate_progress_chart.py`
- History: `dashboard/generate_weekly_history.py`
- README writers: `dashboard/update_readme_history.py`, `dashboard/update_readme_charts.py`
- Cache-busting: `dashboard/update_readme_asset_versions.py`
- Weekly reset: Monday 07:00 KST via `dashboard/check_weekly_reset.py`

`dashboard/data.json` stores the current week and up to twelve completed weeks.
Pull requests are machine-counted by `dashboard/get_weekly_pull_requests.py`
using an exact Monday–Sunday KST window. API failure preserves the last good
value. Five grouped metrics are hand-filed:

1. social posts
2. talks with users
3. coffee chats
4. workouts
5. blog posts

### 3. Daily-note input

Slack input and reminders were retired in September 2026. The source of truth for
hand-filed metrics is now the private Vault's `200-Daily/` notes.

The global `/today` skill writes this exact block into today's note for the
just-finished previous KST day:

```markdown
# 어제의 점검
<!-- piesson-review-date: 2026-09-20 -->
- 소셜 포스트: 2
- 유저 대화: 1
- 커피챗: 0
- 운동: 1
- 글: 0
```

Rules:

- Blank values are zero.
- A missing day contributes zero once that week has at least one review block.
- Reviews before the 2026-09-21 migration cutoff are ignored, preserving W38 and older Slack-filed history.
- Managed weeks are recomputed from all retained notes, never incremented blindly.
- Editing an old note repairs that ISO week's totals on the next sync.
- Malformed or conflicting duplicate blocks fail closed.

Parser: `dashboard/sync_daily_metrics.py`

At 00:05 KST, `scripts/update-weekly-tokens.sh` uses the isolated cron worktree to:

1. merge the latest Vault `main`;
2. pull upstream-generated Piesson state;
3. recompute retained weeks from `200-Daily/`;
4. refresh private token totals;
5. commit only `dashboard/data.json`;
6. deliver it to `Piesson/Piesson`.

A token-provider outage does not block a valid daily-metric correction, but the
wrapper still exits non-zero so health monitoring reports the token failure.

## Metric schema

New daily-note-managed entries carry provenance at the week-entry level, while
grouped metric values use an explicit total:

```json
{
  "manualMetricsSource": "daily-notes",
  "metrics": {
    "socialContent": {"total": 3},
    "userSessions": 1,
    "ctoMeetings": 0,
    "workouts": {"total": 1},
    "blogPosts": 0
  }
}
```

Older retained weeks may still use platform/activity splits. All readers must use
`dashboard/metric_totals.py::grouped_total` so both shapes remain valid. If a
mapping contains `total`, it is authoritative and detail keys must not be added.

## Auto-generated files

Do not hand-edit:

- `dashboard/weekly_dashboard.svg`
- `dashboard/progress_sparklines.svg`
- `dashboard/history/*.svg`
- `profile-summary-card-output/**/*.svg`
- generated README history, timestamps, or image-version query strings

Change the generator, regenerate, and test instead.

## Tests

From `apps/piesson/`:

```bash
python3 -m unittest discover -s tests
bash scripts/test-update-weekly-tokens.sh
python3 dashboard/generate_svg.py
python3 dashboard/generate_progress_chart.py
```

Relevant suites:

- `tests/test_sync_daily_metrics.py` — blank=0, idempotence, edits, backfill, conflicts
- `tests/test_metric_totals.py` — grouped legacy/new schema compatibility
- `tests/test_weekly_pull_requests.py` and `tests/test_week_utils.py` — KST/ISO boundaries
- `tests/test_update_readme_history.py` and `tests/test_weekly_history.py` — publication/archive execution paths
- `tests/test_historical_data_contract.py` — retained migration baseline
- `tests/test_dashboard_layout.py` — bar/divider/text collision guards
- `tests/test_readme_asset_versions.py` — content-hash cache busting
- `scripts/test-update-weekly-tokens.sh` — isolated worktree and upstream delivery

For workflow changes, also run `actionlint` when available.

## Manual operations

```bash
# Regenerate the public dashboard upstream
gh workflow run update_dashboard.yml --repo Piesson/Piesson

# Regenerate profile cards upstream
gh workflow run profile-summary-cards.yml --repo Piesson/Piesson

# Run the local nightly wrapper once
 launchctl kickstart -k gui/$UID/com.piesson.weekly-tokens
```

The GitHub workflow only archives/resets weeks and regenerates assets. It does not
have access to private Obsidian notes; daily-note synchronization therefore runs
locally before `data.json` is delivered upstream.

## Retired Slack surface

Do not recreate the deleted Slack path. The following no longer exist:

- `slack_response.yml`
- `cloudflare-worker.js`
- `slack_update.py`
- `generate_slack_message.py`
- `check_daily_update.py`
- `generate_weekly_summary.py`
- `SLACK_WEBHOOK_URL`
