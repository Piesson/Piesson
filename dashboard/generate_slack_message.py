#!/usr/bin/env python3
"""
Generate Slack message with current metrics from data.json
"""

import json
import subprocess
from datetime import datetime, timedelta, timezone

# KST = UTC + 9 hours
KST = timezone(timedelta(hours=9))

def get_git_commits_this_week():
    """Count commits in current week (KST timezone)"""
    try:
        # Get Monday of current week in KST
        today = datetime.now(KST)
        monday = today - timedelta(days=today.weekday())
        # Convert KST monday to UTC for git --since
        monday_utc = monday.astimezone(timezone.utc)
        monday_str = monday_utc.strftime('%Y-%m-%d %H:%M:%S')

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

    # Different vibes based on time
    if message_type == "evening":
        greeting = "🚨 GRIND CHECK: Still 0 today?"
        icon = ":rotating_light:"
        motivation = "Time to lock in! 💪"
    else:
        greeting = "⏰ Time to grind"
        icon = ":fire:"
        motivation = "Let's ship it! 🚀"

    message = {
        "username": "GrindBot",
        "icon_emoji": icon,
        "text": f"""{greeting}

╔══════════════════════════╗
║  📊 THIS WEEK'S GRIND     ║
╚══════════════════════════╝

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

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

📥 INPUT: `1 0 0 2 0 0 1 1`
(IG, TT, HT, UserTalks, CoffeeChats, BlogPosts, Running, Gym)

💡 {motivation}"""
    }

    return json.dumps(message)

if __name__ == "__main__":
    import sys
    message_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    print(generate_slack_message(message_type))