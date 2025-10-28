#!/usr/bin/env python3
"""
Update README.md with weekly history section and progress charts
Shows last 12 weeks with clickable links to history SVGs
Auto-updates cumulative and individual progress chart URLs
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

def generate_history_table(weekly_history):
    """Generate Markdown table for weekly history"""
    if not weekly_history:
        return ""

    lines = []
    lines.append("# Weekly History")
    lines.append("")
    lines.append("| Week | Period | 🚀 Commits | 📱 Social | 💬 Talks | ☕ Chats | 🏃 Workouts | 📝 Posts |")
    lines.append("|------|--------|-----------|----------|---------|---------|------------|----------|")

    for entry in weekly_history[:12]:
        week_id = entry['week']
        week_num = week_id.split('-W')[1]

        try:
            start_date = datetime.strptime(entry['startDate'], '%m/%d/%Y')
            end_date = datetime.strptime(entry['endDate'], '%m/%d/%Y')
            period = f"{start_date.strftime('%m/%d/%Y')} - {end_date.strftime('%m/%d/%Y')}"
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
    current_date = datetime.now(KST).strftime('%m/%d/%y')
    lines.append(f'<div align="right"><sub>updated at {current_date}</sub></div>')
    lines.append("")
    return "\n".join(lines)

def generate_chart_urls(weekly_history):
    """Generate Image-Charts URLs for cumulative and individual charts"""
    if not weekly_history:
        return None, {}

    history_sorted = sorted(weekly_history, key=lambda x: x['week'])

    weeks = []
    commits = []
    user_talks = []
    social_posts = []
    coffee_chats = []
    workouts = []
    blog_posts = []

    cumulative_commits = 0
    cumulative_talks = 0
    cumulative_social = 0
    cumulative_chats = 0
    cumulative_workouts = 0
    cumulative_posts = 0

    for entry in history_sorted:
        week_id = entry['week']
        week_num = week_id.split('-W')[1]
        weeks.append(f"W{week_num}")

        metrics = entry['metrics']

        social = metrics.get('socialContent', {})
        if isinstance(social, dict):
            total_social = social.get('instagram', 0) + social.get('tiktok', 0) + social.get('hellotalk', 0)
        else:
            total_social = social

        workouts_data = metrics.get('workouts', {})
        if isinstance(workouts_data, dict):
            total_workouts = workouts_data.get('running', 0) + workouts_data.get('gym', 0)
        else:
            total_workouts = workouts_data

        cumulative_commits += metrics.get('commits', 0)
        cumulative_talks += metrics.get('userSessions', 0)
        cumulative_social += total_social
        cumulative_chats += metrics.get('ctoMeetings', 0)
        cumulative_workouts += total_workouts
        cumulative_posts += metrics.get('blogPosts', 0)

        commits.append(cumulative_commits)
        user_talks.append(cumulative_talks)
        social_posts.append(cumulative_social)
        coffee_chats.append(cumulative_chats)
        workouts.append(cumulative_workouts)
        blog_posts.append(cumulative_posts)

    week_dates = []
    for week_id in [f"2025-W{w.replace('W', '')}" for w in weeks]:
        week_num = int(week_id.split('-W')[1])
        year = int(week_id.split('-W')[0])
        jan_1 = datetime(year, 1, 1)
        days_to_monday = (week_num - 1) * 7 - jan_1.weekday()
        monday = jan_1 + timedelta(days=days_to_monday)
        week_dates.append(monday.strftime('%m/%d/%y'))

    weeks_with_dates = '|'.join([f"{w}+({d})" for w, d in zip(weeks, week_dates)])
    weeks_label = '|'.join(weeks)

    commits_data = ','.join(map(str, commits))
    talks_data = ','.join(map(str, user_talks))
    social_data = ','.join(map(str, social_posts))
    chats_data = ','.join(map(str, coffee_chats))
    workouts_data = ','.join(map(str, workouts))
    posts_data = ','.join(map(str, blog_posts))

    chart_data = f"{commits_data}|{talks_data}|{social_data}|{chats_data}|{workouts_data}|{posts_data}"
    colors = "FF6384,36A2EB,FFCE56,4BC0C0,9966FF,FF9F40"
    legend = "Code+Commits|User+Talks|Social+Posts|Coffee+Chats|Workouts|Blog+Posts"

    combined_url = f"https://image-charts.com/chart?cht=lc&chd=t:{chart_data}&chs=900x450&chxt=x,y&chxl=0:|{weeks_with_dates}&chco={colors}&chdl={legend}&chtt=Cumulative+Progress&chts=000000,16&chls=3|3|3|3|3|3&chg=20,20,1,5"

    individual_urls = {
        'commits': f"https://image-charts.com/chart?cht=lc&chd=t:{commits_data}&chs=380x200&chxt=x,y&chxl=0:|{weeks_label}&chco=FF6384&chtt=Code+Commits&chts=000000,14&chls=3&chg=20,20,1,5&chf=bg,s,FFFFFF",
        'user_talks': f"https://image-charts.com/chart?cht=lc&chd=t:{talks_data}&chs=380x200&chxt=x,y&chxl=0:|{weeks_label}&chco=36A2EB&chtt=User+Talks&chts=000000,14&chls=3&chg=20,20,1,5&chf=bg,s,FFFFFF",
        'social_posts': f"https://image-charts.com/chart?cht=lc&chd=t:{social_data}&chs=380x200&chxt=x,y&chxl=0:|{weeks_label}&chco=FFCE56&chtt=Social+Posts&chts=000000,14&chls=3&chg=20,20,1,5&chf=bg,s,FFFFFF",
        'coffee_chats': f"https://image-charts.com/chart?cht=lc&chd=t:{chats_data}&chs=380x200&chxt=x,y&chxl=0:|{weeks_label}&chco=4BC0C0&chtt=Coffee+Chats&chts=000000,14&chls=3&chg=20,20,1,5&chf=bg,s,FFFFFF",
        'workouts': f"https://image-charts.com/chart?cht=lc&chd=t:{workouts_data}&chs=380x200&chxt=x,y&chxl=0:|{weeks_label}&chco=9966FF&chtt=Workouts&chts=000000,14&chls=3&chg=20,20,1,5&chf=bg,s,FFFFFF",
        'blog_posts': f"https://image-charts.com/chart?cht=lc&chd=t:{posts_data}&chs=380x200&chxt=x,y&chxl=0:|{weeks_label}&chco=FF9F40&chtt=Blog+Posts&chts=000000,14&chls=3&chg=20,20,1,5&chf=bg,s,FFFFFF"
    }

    return combined_url, individual_urls

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
    combined_url, individual_urls = generate_chart_urls(weekly_history)

    history_pattern = r'# Weekly History\n\n\|.*?\n\|.*?\n(?:\|.*?\n)*\n(?:<div align="right"><sub>updated at \d{2}/\d{2}/\d{2}</sub></div>\n)?\n?'

    if re.search(history_pattern, readme_content):
        readme_content = re.sub(history_pattern, history_table, readme_content)
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

    if combined_url and individual_urls:
        cumulative_pattern = r'<p align="center">\s*<img src="https://image-charts\.com/chart\?cht=lc&chd=t:[^"]*" alt="Cumulative Progress - All Metrics">\s*</p>'
        cumulative_replacement = f'<p align="center">\n  <img src="{combined_url}" alt="Cumulative Progress - All Metrics">\n</p>'

        if re.search(cumulative_pattern, readme_content):
            readme_content = re.sub(cumulative_pattern, cumulative_replacement, readme_content)
            print("✅ Updated Cumulative Progress chart URL")

        individual_patterns = {
            'commits': r'<img src="https://image-charts\.com/chart\?cht=lc&chd=t:[^"]*&chco=FF6384&chtt=Code\+Commits[^"]*" alt="Code Commits Progress">',
            'user_talks': r'<img src="https://image-charts\.com/chart\?cht=lc&chd=t:[^"]*&chco=36A2EB&chtt=User\+Talks[^"]*" alt="User Talks Progress">',
            'social_posts': r'<img src="https://image-charts\.com/chart\?cht=lc&chd=t:[^"]*&chco=FFCE56&chtt=Social\+Posts[^"]*" alt="Social Posts Progress">',
            'coffee_chats': r'<img src="https://image-charts\.com/chart\?cht=lc&chd=t:[^"]*&chco=4BC0C0&chtt=Coffee\+Chats[^"]*" alt="Coffee Chats Progress">',
            'workouts': r'<img src="https://image-charts\.com/chart\?cht=lc&chd=t:[^"]*&chco=9966FF&chtt=Workouts[^"]*" alt="Workouts Progress">',
            'blog_posts': r'<img src="https://image-charts\.com/chart\?cht=lc&chd=t:[^"]*&chco=FF9F40&chtt=Blog\+Posts[^"]*" alt="Blog Posts Progress">'
        }

        for key, pattern in individual_patterns.items():
            alt_text = key.replace('_', ' ').title() + ' Progress'
            replacement = f'<img src="{individual_urls[key]}" alt="{alt_text}">'
            if re.search(pattern, readme_content):
                readme_content = re.sub(pattern, replacement, readme_content)

        print("✅ Updated Individual chart URLs")

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    return True

if __name__ == "__main__":
    success = update_readme_with_history()
    exit(0 if success else 1)
