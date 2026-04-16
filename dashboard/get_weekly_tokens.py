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

    DATA.write_text(json.dumps(data, indent=2) + '\n')

    print(
        f"Updated tokens: claude={fmt_b(new_claude)}, "
        f"codex={fmt_b(new_codex)}, total={fmt_b(new_total)}, "
        f"range={start}..{end}"
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
