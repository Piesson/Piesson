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

def generate_slack_message(message_type="morning"):
    """Generate Slack message JSON with current metrics"""
    m = load_current_metrics()

    total_social = m['instagram'] + m['tiktok'] + m['hellotalk']
    total_workouts = m['running'] + m['gym']

    # Different greetings based on time
    if message_type == "evening":
        greeting = "🌆 Evening Reminder - No input received today!"
        icon = ":warning:"
        motivation = "Don't break the streak! 💪"
    else:
        greeting = "🌅 Good morning! Time to track your progress"
        icon = ":fire:"
        motivation = "Let's build something great today! 🚀"

    message = {
        "username": "GrindBot",
        "icon_emoji": icon,
        "text": f"""{greeting}

━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 CURRENT WEEK PROGRESS

🚀 Code Commits: `{m['commits']}` builds

💬 User Talks: `{m['usertalks']}` conversations

📱 Social Posts: `{total_social}` total
    ├─ Instagram: `{m['instagram']}`
    ├─ TikTok: `{m['tiktok']}`
    └─ HelloTalk: `{m['hellotalk']}`

☕ Coffee Chats: `{m['coffeechats']}` co-founder meetings

🏃 Workouts: `{total_workouts}` sessions
    ├─ Running: `{m['running']}`
    └─ Gym: `{m['gym']}`

📝 Blog Posts: `{m['blogposts']}` AI/startup articles

━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 INPUT FORMAT (Daily additions):
`1 0 0 2 0 0 1 1`
(+IG, +TT, +HT, +UserTalks, +CoffeeChats, +BlogPosts, +Running, +Gym)

💡 {motivation}
Enter how many you did TODAY (will be added to current totals)"""
    }

    return json.dumps(message)

if __name__ == "__main__":
    import sys
    message_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    print(generate_slack_message(message_type))