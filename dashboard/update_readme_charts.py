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

    charts_section = f"""# Cumulative Progress

<p align="center">
  <img src="{combined_url}" alt="Cumulative Progress - All Metrics">
</p>

## Individual Metrics

<p align="center">
  <img src="{individual_urls['commits']}" alt="Code Commits Progress">
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

"""

    with open(readme_path, 'r') as f:
        readme_content = f.read()

    charts_pattern = r'# Cumulative Progress\n\n.*?(?=\n# )'

    if re.search(charts_pattern, readme_content, re.DOTALL):
        readme_content = re.sub(charts_pattern, charts_section.rstrip() + '\n\n', readme_content, flags=re.DOTALL)
        print("✅ Updated existing Cumulative Progress section")
    else:
        tech_stack_index = readme_content.find('# Tech Stack')

        if tech_stack_index != -1:
            readme_content = (
                readme_content[:tech_stack_index] +
                charts_section +
                readme_content[tech_stack_index:]
            )
            print("✅ Added new Cumulative Progress section before Tech Stack")
        else:
            readme_content += '\n\n' + charts_section
            print("✅ Added new Cumulative Progress section at end")

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    return True

if __name__ == "__main__":
    print("📊 Updating README with progress charts...\n")
    success = update_readme_with_charts()
    exit(0 if success else 1)
