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
    """Load current week metrics from data.json.

    Returns dict with key 'commits_is_cached' indicating whether the
    commit count came from a successful API call (False) or fell back
    to data.json's last known good value (True).
    """
    try:
        with open('dashboard/data.json', 'r') as f:
            data = json.load(f)

        metrics = data['currentWeek']['metrics']
        social = metrics['socialContent']
        workouts = metrics['workouts']
        cached_commits = metrics.get('commits', 0)

        fresh = get_weekly_commits()
        if fresh is None:
            commits = cached_commits
            is_cached = True
        else:
            commits = fresh
            is_cached = False

        return {
            'commits': commits,
            'commits_is_cached': is_cached,
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
        print(f"Error loading metrics: {e}", file=sys.stderr)
        # data.json itself failed to load — show 0 with cached flag
        # so the suffix appears in the slack message rather than crashing.
        # T10 may want a distinct "(unavailable)" suffix for this branch
        # vs the api-failed-but-data-json-readable branch above.
        return {
            'commits': 0, 'commits_is_cached': True,
            'instagram': 0, 'tiktok': 0, 'hellotalk': 0,
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
        greeting = "GRIND CHECK: Still 0 today? 🚨"
        icon = ":rotating_light:"
    else:
        greeting = "Time to get things done 🔥"
        icon = ":fire:"

    cached_suffix = " (cached — API unavailable)" if m.get("commits_is_cached") else ""

    message = {
        "username": "GrindBot",
        "icon_emoji": icon,
        "text": f"""{greeting}

THIS WEEK'S GRIND
━━━━━━━━━━━━━━━━━
🚀 Code Commits: `{m['commits']}` builds{cached_suffix}

💬 User Talks: `{m['usertalks']}` sessions

📱 Social Posts: `{total_social}` total

☕ Coffee Chats: `{m['coffeechats']}` meetings

🏃 Workouts: `{total_workouts}` sessions

📝 Blog Posts: `{m['blogposts']}` articles

━━━━━━━━━━━━━━━━━━

📥 INPUT: `1 0 0 2 0 0 1 1`
(Talks, IG, TT, HT, Coffee, Blog, Run, Gym)"""
    }

    return json.dumps(message)

if __name__ == "__main__":
    message_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    print(generate_slack_message(message_type))
