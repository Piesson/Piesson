#!/usr/bin/env python3
"""Refresh README image URLs when their SVG bytes change.

GitHub can retain a rendered copy of an image when its URL stays unchanged.
Each public SVG therefore gets a short content hash in its query string. The
URL changes only when the corresponding file changes, so normal profile loads
remain cacheable while new dashboard layouts appear immediately.
"""

import hashlib
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
README = ROOT / "README.md"

ASSETS = {
    "profile-summary-card-output/default/0-profile-details.svg": (
        ROOT / "profile-summary-card-output/default/0-profile-details.svg"
    ),
    "dashboard/weekly_dashboard.svg": ROOT / "dashboard/weekly_dashboard.svg",
    "dashboard/progress_sparklines.svg": ROOT / "dashboard/progress_sparklines.svg",
}

RAW_PREFIX = "https://raw.githubusercontent.com/Piesson/Piesson/main/"


def content_version(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def update_asset_versions(readme: Path = README, assets=None) -> bool:
    """Write content-hash query strings and return whether README changed."""
    assets = ASSETS if assets is None else assets
    content = readme.read_text()
    updated = content

    for relative_path, asset_path in assets.items():
        if not asset_path.is_file():
            raise FileNotFoundError(f"README asset does not exist: {asset_path}")
        base_url = f"{RAW_PREFIX}{relative_path}"
        versioned_url = f"{base_url}?v={content_version(asset_path)}"
        updated, count = re.subn(
            rf"{re.escape(base_url)}(?:\?v=[A-Za-z0-9._-]+)?",
            versioned_url,
            updated,
        )
        if count == 0:
            raise ValueError(f"README does not reference expected asset: {base_url}")

    if updated == content:
        return False
    readme.write_text(updated)
    return True


def main():
    changed = update_asset_versions()
    print("README asset versions updated" if changed else "README asset versions unchanged")


if __name__ == "__main__":
    main()
