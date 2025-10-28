#!/usr/bin/env python3
"""
Update README.md with progress charts
Inserts cumulative progress charts before Tech Stack section
"""

import re
from pathlib import Path
from generate_progress_chart import load_weekly_data, generate_chart_url, generate_individual_chart_urls

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
    individual_urls = generate_individual_chart_urls(data)

    from datetime import datetime, timedelta, timezone
    KST = timezone(timedelta(hours=9))
    current_date = datetime.now(KST).strftime('%m/%d/%y')

    charts_section = f"""# Progress Tracker

<p align="center">
  <img src="{combined_url}" alt="Progress Tracker">
</p>

<details>
<summary><strong>More details</strong></summary>

<p align="center">
  <img src="{individual_urls['commits']}" alt="Commits Progress">
  <img src="{individual_urls['user_talks']}" alt="User Talks Progress">
</p>

<p align="center">
  <img src="{individual_urls['social_posts']}" alt="Social Posts Progress">
  <img src="{individual_urls['coffee_chats']}" alt="Coffee Chats Progress">
</p>

<p align="center">
  <img src="{individual_urls['workouts']}" alt="Workouts Progress">
  <img src="{individual_urls['blog_posts']}" alt="Blog Posts Progress">
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

    charts_pattern = r'# Progress Tracker\n\n.*?</details>\n\n<div align="right"><sub>updated at \d{2}/\d{2}/\d{2}</sub></div>\n\n'

    if re.search(charts_pattern, readme_content, re.DOTALL):
        readme_content = re.sub(charts_pattern, charts_section, readme_content, flags=re.DOTALL)
        print("✅ Updated existing Progress Tracker section")
    else:
        tech_stack_index = readme_content.find('# Tech Stack')

        if tech_stack_index != -1:
            readme_content = (
                readme_content[:tech_stack_index] +
                charts_section +
                readme_content[tech_stack_index:]
            )
            print("✅ Added new Progress Tracker section before Tech Stack")
        else:
            readme_content += '\n\n' + charts_section
            print("✅ Added new Progress Tracker section at end")

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    return True

if __name__ == "__main__":
    print("📊 Updating README with progress charts...\n")
    success = update_readme_with_charts()
    exit(0 if success else 1)
