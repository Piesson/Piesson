#!/usr/bin/env python3
"""
Generate cumulative progress chart URLs using Image-Charts
Creates line charts showing weekly progress for all 6 metrics
"""

import json
from pathlib import Path
from urllib.parse import quote

def load_weekly_data():
    """Load and process weekly history data"""
    data_file = Path('dashboard/data.json')

    if not data_file.exists():
        print("❌ data.json not found")
        return None

    with open(data_file, 'r') as f:
        data = json.load(f)

    history = data.get('weeklyHistory', [])

    if not history:
        print("No weekly history found")
        return None

    history_sorted = sorted(history, key=lambda x: x['week'])

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

    return {
        'weeks': weeks,
        'commits': commits,
        'user_talks': user_talks,
        'social_posts': social_posts,
        'coffee_chats': coffee_chats,
        'workouts': workouts,
        'blog_posts': blog_posts
    }

def generate_chart_url(data):
    """Generate Image-Charts URL for all 6 metrics"""
    if not data:
        return None

    weeks_label = '|'.join(data['weeks'])

    week_dates = []
    for week_id in [f"2025-W{w.replace('W', '')}" for w in data['weeks']]:
        week_num = int(week_id.split('-W')[1])
        year = int(week_id.split('-W')[0])
        from datetime import datetime, timedelta
        jan_1 = datetime(year, 1, 1)
        days_to_monday = (week_num - 1) * 7 - jan_1.weekday()
        monday = jan_1 + timedelta(days=days_to_monday)
        week_dates.append(monday.strftime('%m/%d/%y'))

    weeks_with_dates = '|'.join([f"{w}+({d})" for w, d in zip(data['weeks'], week_dates)])

    commits_data = ','.join(map(str, data['commits']))
    talks_data = ','.join(map(str, data['user_talks']))
    social_data = ','.join(map(str, data['social_posts']))
    chats_data = ','.join(map(str, data['coffee_chats']))
    workouts_data = ','.join(map(str, data['workouts']))
    posts_data = ','.join(map(str, data['blog_posts']))

    chart_data = f"{commits_data}|{talks_data}|{social_data}|{chats_data}|{workouts_data}|{posts_data}"

    colors = "FF6384,36A2EB,FFCE56,4BC0C0,9966FF,FF9F40"

    legend = "Code+Commits|User+Talks|Social+Posts|Coffee+Chats|Workouts|Blog+Posts"

    markers = "N*f0*,000000,0,-1,11|N*f0*,000000,1,-1,11|N*f0*,000000,2,-1,11|N*f0*,000000,3,-1,11|N*f0*,000000,4,-1,11|N*f0*,000000,5,-1,11"

    url = f"https://image-charts.com/chart?cht=lc&chd=t:{chart_data}&chs=900x450&chxt=x,y&chxl=0:|{weeks_with_dates}&chco={colors}&chdl={legend}&chtt=The+Grind+Never+Stops&chts=000000,16&chls=3|3|3|3|3|3&chg=20,20,1,5&chm={markers}"

    return url

def generate_individual_chart_urls(data):
    """Generate individual chart URLs for each metric"""
    if not data:
        return {}

    weeks_label = '|'.join(data['weeks'])

    charts = {
        'commits': {
            'title': 'Code+Commits',
            'data': ','.join(map(str, data['commits'])),
            'color': 'FF6384'
        },
        'user_talks': {
            'title': 'User+Talks',
            'data': ','.join(map(str, data['user_talks'])),
            'color': '36A2EB'
        },
        'social_posts': {
            'title': 'Social+Posts',
            'data': ','.join(map(str, data['social_posts'])),
            'color': 'FFCE56'
        },
        'coffee_chats': {
            'title': 'Coffee+Chats',
            'data': ','.join(map(str, data['coffee_chats'])),
            'color': '4BC0C0'
        },
        'workouts': {
            'title': 'Workouts',
            'data': ','.join(map(str, data['workouts'])),
            'color': '9966FF'
        },
        'blog_posts': {
            'title': 'Blog+Posts',
            'data': ','.join(map(str, data['blog_posts'])),
            'color': 'FF9F40'
        }
    }

    urls = {}
    for key, chart in charts.items():
        url = f"https://image-charts.com/chart?cht=lc&chd=t:{chart['data']}&chs=380x200&chxt=x,y&chxl=0:|{weeks_label}&chco={chart['color']}&chtt={chart['title']}&chts=000000,14&chls=3&chg=20,20,1,5&chf=bg,s,FFFFFF"
        urls[key] = url

    return urls

if __name__ == "__main__":
    print("📊 Generating progress chart URLs...\n")

    data = load_weekly_data()

    if data:
        combined_url = generate_chart_url(data)
        print("Combined Chart URL:")
        print(combined_url)
        print()

        individual_urls = generate_individual_chart_urls(data)
        print("Individual Chart URLs:")
        for key, url in individual_urls.items():
            print(f"\n{key}:")
            print(url)

        print("\n✅ Chart URLs generated!")
    else:
        print("❌ Failed to generate chart URLs")
        exit(1)
