#!/usr/bin/env python3
"""
update_readme_charts.py — (2026-09-21 redesign) SVG regeneration + timestamp.

The new README embeds self-contained SVGs (weekly_dashboard.svg,
progress_sparklines.svg); no QuickChart URLs, no chart-url injection.
This script now: regenerates both SVGs from data.json, updates the
"updated at" lines in README.md, and exits cleanly.

The old dual-axis QuickChart / Token Usage sections were removed with the
redesign; their generators remain in the repo for reference.
"""

import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
README = HERE / '..' / 'README.md'
KST = timezone(timedelta(hours=9))


def update_timestamps():
    today = datetime.now(KST).strftime('%m/%d/%y')
    content = README.read_text()
    content = re.sub(
        r'updated at \d{2}/\d{2}/\d{2}',
        f'updated at {today}',
        content,
    )
    README.write_text(content)
    print(f'✅ Timestamps updated to {today}')


def main():
    from generate_svg import generate_dashboard_svg
    from generate_progress_chart import generate_progress_chart
    generate_dashboard_svg()
    generate_progress_chart()
    update_timestamps()
    print('✅ Charts and timestamps updated')


if __name__ == '__main__':
    main()
