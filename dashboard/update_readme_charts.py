#!/usr/bin/env python3
"""
Update README.md with progress charts
Inserts cumulative progress charts before Tech Stack section, and a
weekly AI Tokens section between Consistent enough? and Weekly History.
"""

import json
import re
from pathlib import Path
from generate_progress_chart import (
    load_weekly_data,
    generate_chart_url,
    save_sparklines_svg,
    generate_tokens_chart_url,
)


def _insert_or_replace(readme_content, section_text, existing_pattern, anchors):
    """Replace an existing section matching `existing_pattern`, or insert
    `section_text` before the first anchor heading that appears in the
    README. Anchors is a list of heading strings tried in order. Falls
    back to appending at EOF."""
    if re.search(existing_pattern, readme_content, re.DOTALL):
        return re.sub(existing_pattern, section_text, readme_content, flags=re.DOTALL), "replaced"
    for anchor in anchors:
        idx = readme_content.find(anchor)
        if idx != -1:
            return readme_content[:idx] + section_text + readme_content[idx:], f"inserted before {anchor}"
    return readme_content + '\n\n' + section_text, "appended"


def update_readme_with_charts():
    """Update README.md with progress charts"""
    readme_path = Path('README.md')

    if not readme_path.exists():
        print("❌ README.md not found")
        return False

    data = load_weekly_data()

    if not data:
        print("❌ No weekly data to generate charts")
        return False

    combined_url = generate_chart_url(data)
    save_sparklines_svg(data)

    raw_path = Path('dashboard/data.json')
    raw_data = json.loads(raw_path.read_text()) if raw_path.exists() else None
    tokens_url = generate_tokens_chart_url(raw_data) if raw_data else None

    from datetime import datetime, timedelta, timezone
    KST = timezone(timedelta(hours=9))
    current_date = datetime.now(KST).strftime('%m/%d/%y')

    charts_section = f"""# Consistent enough?

<p align="center">
  <img src="{combined_url}" alt="Consistent enough?">
</p>

<details>
<summary><strong>More details</strong></summary>

<p align="center">
  <img src="https://raw.githubusercontent.com/Piesson/Piesson/main/dashboard/progress_sparklines.svg" alt="Individual Metric Sparklines">
</p>

</details>

<div align="right"><sub>updated at {current_date}</sub></div>

"""

    with open(readme_path, 'r') as f:
        readme_content = f.read()

    old_pattern = r'# Cumulative Progress\n\n.*?(?=\n# Tech Stack)'
    readme_content = re.sub(old_pattern, '', readme_content, flags=re.DOTALL)

    old_pattern2 = r'## Individual Metrics\n\n.*?(?=\n# Tech Stack)'
    readme_content = re.sub(old_pattern2, '', readme_content, flags=re.DOTALL)

    charts_pattern = r'# Consistent enough\?\n\n.*?</details>\n\n<div align="right"><sub>updated at \d{2}/\d{2}/\d{2}</sub></div>\n\n'

    readme_content, charts_action = _insert_or_replace(
        readme_content,
        section_text=charts_section,
        existing_pattern=charts_pattern,
        anchors=['# AI Tokens', '# Weekly History', '# Tech Stack'],
    )
    print(f"✅ Consistent enough? section: {charts_action}")

    tokens_pattern = r'# AI Tokens\n\n.*?</p>\n\n<div align="right"><sub>updated at \d{2}/\d{2}/\d{2}</sub></div>\n\n'

    if tokens_url:
        tokens_section = f"""# AI Tokens

<p align="center">
  <img src="{tokens_url}" alt="Weekly AI Tokens">
</p>

<div align="right"><sub>updated at {current_date}</sub></div>

"""
        readme_content, tokens_action = _insert_or_replace(
            readme_content,
            section_text=tokens_section,
            existing_pattern=tokens_pattern,
            anchors=['# Weekly History', '# Tech Stack'],
        )
        print(f"✅ AI Tokens section: {tokens_action}")
    else:
        # No tracked weeks yet — strip any stale section so the README stays clean.
        if re.search(tokens_pattern, readme_content, re.DOTALL):
            readme_content = re.sub(tokens_pattern, '', readme_content, flags=re.DOTALL)
            print("✅ AI Tokens section: removed (no tracked weeks)")
        else:
            print("ℹ️  AI Tokens section skipped (no tracked weeks yet)")

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    return True


if __name__ == "__main__":
    print("📊 Updating README with progress charts...\n")
    success = update_readme_with_charts()
    exit(0 if success else 1)
