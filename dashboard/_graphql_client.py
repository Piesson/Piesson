"""Shared GraphQL client. Single rule: never lie about what happened.

Returns (data, None) on success or (None, ErrorKind) on any failure.
Callers MUST check err and decide what to do — never silently treat None
as zero.
"""

from __future__ import annotations
import time
from enum import Enum
from typing import Optional, Tuple

import requests


class ErrorKind(str, Enum):
    RATE_LIMIT = "rate_limit"   # secondary or primary GraphQL rate limit
    AUTH       = "auth"         # 401/403 / bad credentials / missing token
    NETWORK    = "network"      # connection error / timeout / 5xx
    UNKNOWN    = "unknown"      # GraphQL errors we didn't classify


_TIMEOUT_SECONDS = 15
_MAX_ATTEMPTS = 3
_BACKOFF_BASE = 0.5  # 0.5s, 1.0s, 2.0s


def post_graphql(
    url: str,
    headers: dict,
    body: dict,
) -> Tuple[Optional[dict], Optional[ErrorKind]]:
    """Retries on NETWORK errors only. RATE_LIMIT/AUTH/UNKNOWN return immediately."""
    last_err: Optional[ErrorKind] = None
    for attempt in range(_MAX_ATTEMPTS):
        data, err = _post_once(url, headers, body)
        if err is None:
            return data, None
        last_err = err
        if err is not ErrorKind.NETWORK:
            return None, err  # rate-limit / auth / unknown — don't retry
        if attempt < _MAX_ATTEMPTS - 1:
            time.sleep(_BACKOFF_BASE * (2 ** attempt))
    return None, last_err


def _post_once(url, headers, body):
    try:
        r = requests.post(url, headers=headers, json=body, timeout=_TIMEOUT_SECONDS)
    except requests.RequestException:
        return None, ErrorKind.NETWORK

    if r.status_code == 429:
        return None, ErrorKind.RATE_LIMIT
    if r.status_code == 403 and r.headers.get("x-ratelimit-remaining") == "0":
        # Primary rate limit exhaustion is a 403, not a 429 — without this
        # check it was logged as "auth" and sent us chasing token expiry
        # (2026-07-19 incident).
        return None, ErrorKind.RATE_LIMIT
    if r.status_code in (401, 403):
        return None, ErrorKind.AUTH
    if r.status_code >= 500:
        return None, ErrorKind.NETWORK
    if r.status_code != 200:
        return None, ErrorKind.UNKNOWN

    try:
        data = r.json()
    except ValueError:
        return None, ErrorKind.UNKNOWN

    errs = data.get("errors") if isinstance(data, dict) else None
    if errs:
        for e in errs:
            t = (e.get("type") or "").upper()
            if t == "RATE_LIMIT":
                return None, ErrorKind.RATE_LIMIT
        return None, ErrorKind.UNKNOWN

    return data, None
