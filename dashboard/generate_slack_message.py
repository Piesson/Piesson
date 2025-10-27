#!/usr/bin/env python3
"""
Generate Slack message with current metrics from data.json
"""

import json
import subprocess
from datetime import datetime, timedelta

def get_git_commits_this_week():
    """Count commits in current week"""
    try:
        # Get Monday of current week
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        monday_str = monday.strftime('%Y-%m-%d')

        # Count commits since Monday
        result = subprocess.run([
            'git', 'rev-list', '--count', '--since', monday_str, 'HEAD'
        ], capture_output=True, text=True)

        return int(result.stdout.strip()) if result.returncode == 0 else 0
    except:
        return 0

def load_current_metrics():
    """Load current week metrics from data.json"""
    try:
        with open('dashboard/data.json', 'r') as f:
            data = json.load(f)

        metrics = data['currentWeek']['metrics']
        social = metrics['socialContent']
        workouts = metrics['workouts']

        return {
            'commits': get_git_commits_this_week(),
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

def generate_slack_message():
    """Generate Slack message JSON with current metrics"""
    m = load_current_metrics()

    total_social = m['instagram'] + m['tiktok'] + m['hellotalk']
    total_workouts = m['running'] + m['gym']

    message = {
        "username": "GrindBot",
        "icon_emoji": ":fire:",
        "text": f"""Yo, what did you do today?

```
Commits:       [{m['commits']}] (code building)
Instagram:     [{m['instagram']}]  (posts)
TikTok:        [{m['tiktok']}]  (posts)
HelloTalk:     [{m['hellotalk']}]  (posts)
Social Total:  [{total_social}]  (IG+TT+HT)
User Talks:    [{m['usertalks']}] (conversations)
Coffee Chats:  [{m['coffeechats']}] (co-founder meetings)
Blog Posts:    [{m['blogposts']}] (AI/startup articles)
Workouts:      [{total_workouts}] (running + gym total)
  Running:     [{m['running']}]  (times)
  Gym:         [{m['gym']}]  (times)
```

Type 7 numbers: 3 2 1 10 2 1 5
(Instagram, TikTok, HelloTalk, UserTalks, CoffeeChats, BlogPosts, Workouts)"""
    }

    return json.dumps(message)

if __name__ == "__main__":
    print(generate_slack_message())