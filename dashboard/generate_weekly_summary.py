#!/usr/bin/env python3
"""
Generate weekly summary message for Slack
Sends on Monday morning after weekly reset
"""

import json
from pathlib import Path

def generate_weekly_summary():
    """Generate weekly summary message from last week's data"""
    data_file = Path('dashboard/data.json')

    if not data_file.exists():
        print("❌ data.json not found")
        return None

    with open(data_file, 'r') as f:
        data = json.load(f)

    if not data.get('weeklyHistory'):
        print("No weekly history found")
        return None

    last_week = data['weeklyHistory'][0]
    week_id = last_week['week']
    week_num = week_id.split('-W')[1]
    start_date = last_week['startDate']
    end_date = last_week['endDate']

    metrics = last_week['metrics']

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

    message = {
        "username": "GrindBot",
        "icon_emoji": ":tada:",
        "text": f"""Fresh week huh?

Last Week Summary (Week {week_num}: {start_date} - {end_date})
━━━━━━━━━━━━━━━━━
🚀 Code Commits: `{commits}` builds (avg `{commits/7:.1f}` per day)

💬 User Talks: `{user_sessions}` sessions (avg `{user_sessions/7:.1f}` per day)

📱 Social Posts: `{total_social}` total (avg `{total_social/7:.1f}` per day)

☕ Coffee Chats: `{cto_meetings}` meetings (avg `{cto_meetings/7:.1f}` per day)

🏃 Workouts: `{total_workouts}` sessions (avg `{total_workouts/7:.1f}` per day)

📝 Blog Posts: `{blog_posts}` articles (avg `{blog_posts/7:.1f}` per day)

━━━━━━━━━━━━━━━━━━
"""
    }

    return json.dumps(message)

if __name__ == "__main__":
    summary = generate_weekly_summary()
    if summary:
        print(summary)
    else:
        exit(1)
