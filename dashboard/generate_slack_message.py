#!/usr/bin/env python3
"""
Generate Slack message with current metrics from data.json
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from get_weekly_commits import get_weekly_commits

# KST = UTC + 9 hours
KST = timezone(timedelta(hours=9))

def load_current_metrics():
    """Load current week metrics from data.json"""
    try:
        with open('dashboard/data.json', 'r') as f:
            data = json.load(f)

        metrics = data['currentWeek']['metrics']
        social = metrics['socialContent']
        workouts = metrics['workouts']

        return {
            'commits': get_weekly_commits(),
            'instagram': social['instagram'],
            'tiktok': social['tiktok'],
            'hellotalk': social['hellotalk'],
            'usertalks': metrics['userSessions'],
            'coffeechats': metrics['ctoMeetings'],
            'blogposts': metrics['blogPosts'],
            'running': workouts['running'],
            'gym': workouts['gym']
        }
    except Exception as e:
        print(f"Error loading metrics: {e}")
        return {
            'commits': 0, 'instagram': 0, 'tiktok': 0, 'hellotalk': 0,
            'usertalks': 0, 'coffeechats': 0, 'blogposts': 0,
            'running': 0, 'gym': 0
        }

def generate_slack_message(message_type="morning"):
    """Generate Slack message JSON with current metrics"""
    m = load_current_metrics()

    total_social = m['instagram'] + m['tiktok'] + m['hellotalk']
    total_workouts = m['running'] + m['gym']

    # Different vibes based on time
    if message_type == "evening":
        greeting = "🚨 GRIND CHECK: Still 0 today?"
        icon = ":rotating_light:"
    else:
        greeting = "Time to get things done"
        icon = ":fire:"

    message = {
        "username": "GrindBot",
        "icon_emoji": icon,
        "text": f"""{greeting}

THIS WEEK'S GRIND
━━━━━━━━━━━━━━━━━
🚀 Code Commits: `{m['commits']}` builds

💬 User Talks: `{m['usertalks']}` conversations

📱 Social Posts: `{total_social}` total (IG: `{m['instagram']}`, TT: `{m['tiktok']}`, HT: `{m['hellotalk']}`)

☕ Coffee Chats: `{m['coffeechats']}` meetings

🏃 Workouts: `{total_workouts}` sessions (Run: `{m['running']}`, Gym: `{m['gym']}`)

📝 Blog Posts: `{m['blogposts']}` articles

━━━━━━━━━━━━━━━━━

📥 INPUT: `2 1 0 3 0 1 2 0`
(Talks, IG, TT, HT, Coffee, Blog, Run, Gym)"""
    }

    return json.dumps(message)

if __name__ == "__main__":
    import sys
    message_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    print(generate_slack_message(message_type))