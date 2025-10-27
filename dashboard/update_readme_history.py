#!/usr/bin/env python3
"""
Update README.md with weekly history section
Shows last 12 weeks with clickable links to history SVGs
"""

import json
import re
from pathlib import Path
from datetime import datetime

def generate_history_table(weekly_history):
    """Generate Markdown table for weekly history"""
    if not weekly_history:
        return ""

    lines = []
    lines.append("# Weekly History")
    lines.append("")
    lines.append("| Week | Period | Commits | Social | Talks | Chats | Workouts | Posts |")
    lines.append("|------|--------|---------|--------|-------|-------|----------|-------|")

    for entry in weekly_history[:12]:
        week_id = entry['week']
        week_num = week_id.split('-W')[1]

        try:
            start_date = datetime.strptime(entry['startDate'], '%m/%d/%Y')
            end_date = datetime.strptime(entry['endDate'], '%m/%d/%Y')
            period = f"{start_date.strftime('%m/%d')} - {end_date.strftime('%m/%d')}"
        except:
            period = f"{entry['startDate']} - {entry['endDate']}"

        metrics = entry['metrics']

        social = metrics.get('socialContent', {})
        if isinstance(social, dict):
            total_social = social.get('instagram', 0) + social.get('tiktok', 0) + social.get('hellotalk', 0)
        else:
            total_social = social

        workouts = metrics.get('workouts', {})
        if isinstance(workouts, dict):
            total_workouts = workouts.get('running', 0) + workouts.get('gym', 0)
        else:
            total_workouts = workouts

        commits = metrics.get('commits', 0)
        user_sessions = metrics.get('userSessions', 0)
        cto_meetings = metrics.get('ctoMeetings', 0)
        blog_posts = metrics.get('blogPosts', 0)

        svg_url = f"https://raw.githubusercontent.com/Piesson/Piesson/main/dashboard/history/weekly_history_{week_id}.svg"

        lines.append(
            f"| [**Week {week_num}**]({svg_url}) | {period} | {commits} | {total_social} | "
            f"{user_sessions} | {cto_meetings} | {total_workouts} | {blog_posts} |"
        )

    lines.append("")
    return "\n".join(lines)

def update_readme_with_history():
    """Update README.md with weekly history section"""
    readme_path = Path('README.md')
    data_path = Path('dashboard/data.json')

    if not readme_path.exists():
        print("❌ README.md not found")
        return False

    if not data_path.exists():
        print("❌ data.json not found")
        return False

    with open(data_path, 'r') as f:
        data = json.load(f)

    weekly_history = data.get('weeklyHistory', [])

    if not weekly_history:
        print("No weekly history to add")
        return False

    with open(readme_path, 'r') as f:
        readme_content = f.read()

    history_table = generate_history_table(weekly_history)

    history_pattern = r'# Weekly History\n\n\|.*?\n\|.*?\n(?:\|.*?\n)*\n'

    if re.search(history_pattern, readme_content):
        readme_content = re.sub(history_pattern, history_table + '\n', readme_content)
        print("✅ Updated existing Weekly History section")
    else:
        tech_stack_index = readme_content.find('# Tech Stack')

        if tech_stack_index != -1:
            readme_content = (
                readme_content[:tech_stack_index] +
                history_table + '\n\n' +
                readme_content[tech_stack_index:]
            )
            print("✅ Added new Weekly History section before Tech Stack")
        else:
            readme_content += '\n\n' + history_table
            print("✅ Added new Weekly History section at end")

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    return True

if __name__ == "__main__":
    success = update_readme_with_history()
    exit(0 if success else 1)
