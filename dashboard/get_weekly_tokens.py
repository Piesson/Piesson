#!/usr/bin/env python3
"""
Fetch weekly Claude Code + Codex CLI token usage, write to data.json.

Reads currentWeek.startDate/endDate from data.json (not now()) so upstream
reset timing is irrelevant: query range always matches the labeled week.

Error contract:
  - Each source (ccusage, @ccusage/codex) runs in an isolated try/except.
  - On network failure the CLI is retried once with --offline.
  - If a single source fails, its previous value is preserved and the other
    source still updates (exit 0).
  - If both sources fail, the existing tokens block is preserved unchanged
    and the script exits 1 so the wrapper can skip the commit.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
DATA = Path('dashboard/data.json')
TIMEOUT_SECS = 120
NETWORK_SIGNALS = (
    'network', 'fetch', 'enotfound', 'etimedout', 'eai_again',
    'econnrefused', 'econnreset',
)


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def extract_days(payload):
    if not isinstance(payload, dict):
        return []
    return payload.get('daily') or payload.get('data') or []


def day_total(entry):
    if not isinstance(entry, dict):
        return 0
    return int(entry.get('totalTokens') or entry.get('total_tokens') or 0)


def run_cli(cmd):
    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=TIMEOUT_SECS
    )
    return proc.stdout, proc.stderr, proc.returncode


def looks_like_network_error(stderr):
    low = (stderr or '').lower()
    return any(sig in low for sig in NETWORK_SIGNALS)


def fetch_source(label, online_cmd, offline_cmd):
    try:
        stdout, stderr, rc = run_cli(online_cmd)
        if rc != 0:
            if looks_like_network_error(stderr):
                log(f"[{label}] network error, retrying --offline: {stderr[:200]}")
                stdout, stderr, rc = run_cli(offline_cmd)
                if rc != 0:
                    log(f"[{label}] offline retry failed rc={rc}: {stderr[:200]}")
                    return 0, False
            else:
                log(f"[{label}] CLI failed rc={rc}: {stderr[:200]}")
                return 0, False
        payload = json.loads(stdout) if stdout.strip() else {}
    except FileNotFoundError:
        log(f"[{label}] CLI not found in PATH")
        return 0, False
    except subprocess.TimeoutExpired as exc:
        log(f"[{label}] timeout after {exc.timeout}s")
        return 0, False
    except json.JSONDecodeError as exc:
        log(f"[{label}] JSON decode failed: {exc}")
        return 0, False

    days = extract_days(payload)
    total = sum(day_total(d) for d in days)
    log(f"[{label}] days={len(days)} total={total:,}")
    return total, True


def fetch_claude(start_iso, end_iso):
    start = start_iso.replace('-', '')
    end = end_iso.replace('-', '')
    return fetch_source(
        'claude',
        online_cmd=[
            'ccusage', 'daily', '--json',
            '--since', start, '--until', end,
            '--timezone', 'Asia/Seoul',
        ],
        offline_cmd=[
            'ccusage', 'daily', '--json', '--offline',
            '--since', start, '--until', end,
            '--timezone', 'Asia/Seoul',
        ],
    )


def fetch_codex(start_iso, end_iso):
    base = ['npx', '-y', '@ccusage/codex@latest', 'daily', '--json']
    date_args = [
        '--since', start_iso, '--until', end_iso,
        '--timezone', 'Asia/Seoul',
    ]
    return fetch_source(
        'codex',
        online_cmd=base + date_args,
        offline_cmd=base + ['--offline'] + date_args,
    )


def fmt_b(n):
    return f"{n / 1_000_000_000:.1f}B"


# ── Weekly history backfill ────────────────────────────────────────────────
# Why this exists:
#   When the Mac is off for ≥1 week, the wrapper never runs, so
#   currentWeek.tokens stays stale at whatever value it had when the user
#   left. When the upstream weekly reset (Monday 7 AM KST) then moves
#   currentWeek into weeklyHistory[0], that stale value becomes permanent —
#   the wrapper only updates currentWeek going forward, never re-touches
#   past weeks. That's exactly the W19 (5/4-5/10) bug we manually backfilled.
#
# Fix: every wrapper run inspects each weeklyHistory entry; if its tokens
# were snapshotted before the week's natural close (Mon 00:00 KST after
# endDate), re-query ccusage for that week's range and update. ccusage
# usage data is append-only and retroactive — querying past dates returns
# the cumulative truth, so this is idempotent for complete entries and
# corrective for stale ones.
def parse_date_str(s):
    """Parse 'YYYY-MM-DD' or 'MM/DD/YYYY' (legacy) into a date object."""
    if not s:
        return None
    for fmt in ('%Y-%m-%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(s, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def _normalize_date(s):
    """Return 'YYYY-MM-DD' regardless of input format, or None."""
    d = parse_date_str(s)
    return d.isoformat() if d else None


def is_history_entry_stale(entry):
    """A weeklyHistory entry is stale when its tokens.updatedAt is before
    the natural close boundary = Monday 00:00 KST after the week's endDate.
    Missing or unparseable updatedAt → stale (likely first run against an
    old entry). Unparseable endDate → False (can't compute boundary, skip)."""
    end_date = parse_date_str(entry.get('endDate', ''))
    if end_date is None:
        return False
    close_boundary = datetime.combine(
        end_date + timedelta(days=1),
        datetime.min.time(),
        tzinfo=KST,
    )
    tokens = (entry.get('metrics') or {}).get('tokens') or {}
    updated_at_str = tokens.get('updatedAt')
    if not updated_at_str:
        return True
    try:
        updated_at = datetime.fromisoformat(updated_at_str)
    except (ValueError, TypeError):
        return True
    return updated_at < close_boundary


def backfill_weekly_history(data):
    """Re-query ccusage for each stale weeklyHistory entry. Returns the
    count of entries successfully backfilled.

    Safety rules:
      - Both ccusage sources fail → skip entry (don't overwrite with 0).
      - Re-query returns 0/0 but existing was non-zero → preserve existing
        (defensive against transient ccusage breakage / data corruption).
      - Partial success (claude OR codex) → use the working source's value,
        keep existing for the failed source.
    """
    history = data.get('weeklyHistory') or []
    backfilled = 0
    for entry in history:
        if not is_history_entry_stale(entry):
            continue
        start_iso = _normalize_date(entry.get('startDate'))
        end_iso = _normalize_date(entry.get('endDate'))
        if not start_iso or not end_iso:
            continue
        week_label = entry.get('week') or f"{start_iso}..{end_iso}"
        log(f"[backfill] {week_label} ({start_iso}..{end_iso})")

        claude_total, claude_ok = fetch_claude(start_iso, end_iso)
        codex_total, codex_ok = fetch_codex(start_iso, end_iso)

        if not claude_ok and not codex_ok:
            log(f"[backfill] {week_label} both sources failed — preserving")
            continue

        existing = (entry.get('metrics') or {}).get('tokens') or {}
        existing_claude = int(existing.get('claude') or 0)
        existing_codex = int(existing.get('codex') or 0)
        new_claude = claude_total if claude_ok else existing_claude
        new_codex = codex_total if codex_ok else existing_codex

        # Defensive: don't overwrite non-zero with 0/0 (likely ccusage glitch).
        if (new_claude == 0 and new_codex == 0
                and (existing_claude > 0 or existing_codex > 0)):
            log(f"[backfill] {week_label} re-query returned 0/0 but existing "
                f"non-zero — preserving")
            continue

        metrics = entry.setdefault('metrics', {})
        metrics['tokens'] = {
            'claude': new_claude,
            'codex': new_codex,
            'total': new_claude + new_codex,
            'updatedAt': datetime.now(KST).isoformat(timespec='seconds'),
        }
        log(f"[backfill] {week_label} updated: "
            f"claude {existing_claude:,}→{new_claude:,}, "
            f"codex {existing_codex:,}→{new_codex:,}")
        backfilled += 1
    return backfilled


def main():
    if not DATA.exists():
        log(f"[fatal] {DATA} not found (cwd={Path.cwd()})")
        return 1

    data = json.loads(DATA.read_text())
    start = data['currentWeek']['startDate']
    end = data['currentWeek']['endDate']
    log(f"[range] {start}..{end}")

    claude_total, claude_ok = fetch_claude(start, end)
    codex_total, codex_ok = fetch_codex(start, end)

    if not claude_ok and not codex_ok:
        log("[fatal] both sources failed, preserving existing tokens")
        return 1

    existing = data['currentWeek']['metrics'].get('tokens') or {}
    new_claude = claude_total if claude_ok else int(existing.get('claude') or 0)
    new_codex = codex_total if codex_ok else int(existing.get('codex') or 0)
    new_total = new_claude + new_codex

    data['currentWeek']['metrics']['tokens'] = {
        'claude': new_claude,
        'codex': new_codex,
        'total': new_total,
        'updatedAt': datetime.now(KST).isoformat(timespec='seconds'),
    }

    # Backfill any stale weeklyHistory entries (Mac-off-across-Monday case).
    # Best-effort: unexpected exceptions are logged and don't fail the wrapper.
    try:
        n = backfill_weekly_history(data)
        if n:
            log(f"[backfill] updated {n} stale weeklyHistory entries")
    except Exception as exc:  # noqa: BLE001 — last-resort safety net
        log(f"[backfill] unexpected error, skipping: {exc}")

    DATA.write_text(json.dumps(data, indent=2) + '\n')

    print(
        f"Updated tokens: claude={fmt_b(new_claude)}, "
        f"codex={fmt_b(new_codex)}, total={fmt_b(new_total)}, "
        f"range={start}..{end}"
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
