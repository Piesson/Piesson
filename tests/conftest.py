"""Shared test helpers: fake HTTP responses + dashboard sys.path injection."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Make dashboard/ importable from tests/
DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"
if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))


def fake_http_response(status: int, body):
    """Build a fake requests.Response-like object."""
    r = MagicMock()
    r.status_code = status
    r.json.return_value = body
    r.text = json.dumps(body) if isinstance(body, (dict, list)) else str(body)
    return r
