#!/usr/bin/env python3
"""
Ultra-simple Slack metrics parser
Usage: echo "Instagram: 3, TikTok: 2" | python3 slack_update.py
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta

# KST = UTC + 9 hours
KST = timezone(timedelta(hours=9))

def parse_metrics(text):
    """Extract numbers from Slack message (supports both formats)"""
    # Try new 8-number format first: "1 0 0 2 0 0 1 1"
    numbers = re.findall(r'\d+', text.strip())
    if len(numbers) >= 8:
        # Order: UserTalks, Instagram, TikTok, HelloTalk, CoffeeChats, BlogPosts, Running, Gym
        return {
            'usertalks': int(numbers[0]),
            'instagram': int(numbers[1]),
            'tiktok': int(numbers[2]),
            'hellotalk': int(numbers[3]),
            'coffeechats': int(numbers[4]),
            'blogposts': int(numbers[5]),
            'running': int(numbers[6]),
            'gym': int(numbers[7])
        }
    elif len(numbers) >= 7:
        # Fallback to 7-number format: "3 2 1 10 2 1 5"
        # Order: Instagram, TikTok, HelloTalk, UserTalks, CoffeeChats, BlogPosts, Workouts
        return {
            'instagram': int(numbers[0]),
            'tiktok': int(numbers[1]),
            'hellotalk': int(numbers[2]),
            'usertalks': int(numbers[3]),
            'coffeechats': int(numbers[4]),
            'blogposts': int(numbers[5]),
            'running': int(numbers[6]) // 2,  # Split workouts roughly
            'gym': int(numbers[6]) - (int(numbers[6]) // 2)
        }
    elif len(numbers) >= 6:
        # Fallback to old format: "5 10 2 1 3 2"
        # Order: Social, UserTalks, CoffeeChats, BlogPosts, Running, Gym
        total_social = int(numbers[0])
        return {
            'instagram': total_social // 3,  # Split social posts roughly
            'tiktok': total_social // 3,
            'hellotalk': total_social - (2 * (total_social // 3)),
            'usertalks': int(numbers[1]),
            'coffeechats': int(numbers[2]),
            'blogposts': int(numbers[3]),
            'running': int(numbers[4]),
            'gym': int(numbers[5])
        }

    # Fallback to old format: "Instagram: 3, TikTok: 2, ..."
    patterns = {
        'instagram': r'instagram:\s*(\d+)',
        'tiktok': r'tiktok:\s*(\d+)',
        'hellotalk': r'hellotalk:\s*(\d+)',
        'usertalks': r'usertalks:\s*(\d+)',
        'coffeechats': r'coffeechats:\s*(\d+)',
        'blogposts': r'blogposts:\s*(\d+)',
        'running': r'running:\s*(\d+)',
        'gym': r'gym:\s*(\d+)'
    }

    result = {}
    text_lower = text.lower()

    for key, pattern in patterns.items():
        match = re.search(pattern, text_lower)
        result[key] = int(match.group(1)) if match else 0

    return result

def update_data(metrics):
    """Update data.json by adding new metrics to existing values"""
    with open('dashboard/data.json', 'r') as f:
        data = json.load(f)

    # Get current values
    current = data['currentWeek']['metrics']
    current_social = current['socialContent']
    current_workouts = current['workouts']

    # Add new metrics to existing values (additive approach)
    data['currentWeek']['metrics']['socialContent'] = {
        'instagram': current_social['instagram'] + metrics['instagram'],
        'tiktok': current_social['tiktok'] + metrics['tiktok'],
        'hellotalk': current_social['hellotalk'] + metrics['hellotalk']
    }
    data['currentWeek']['metrics']['userSessions'] = current['userSessions'] + metrics['usertalks']
    data['currentWeek']['metrics']['ctoMeetings'] = current['ctoMeetings'] + metrics['coffeechats']
    data['currentWeek']['metrics']['blogPosts'] = current['blogPosts'] + metrics['blogposts']
    data['currentWeek']['metrics']['workouts'] = {
        'running': current_workouts['running'] + metrics['running'],
        'gym': current_workouts['gym'] + metrics['gym']
    }
    data['lastUpdated'] = datetime.now(KST).strftime("%Y-%m-%d")

    with open('dashboard/data.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Return both added and new totals for confirmation message
    new_totals = {
        'added': metrics,
        'totals': {
            'instagram': data['currentWeek']['metrics']['socialContent']['instagram'],
            'tiktok': data['currentWeek']['metrics']['socialContent']['tiktok'],
            'hellotalk': data['currentWeek']['metrics']['socialContent']['hellotalk'],
            'usertalks': data['currentWeek']['metrics']['userSessions'],
            'coffeechats': data['currentWeek']['metrics']['ctoMeetings'],
            'blogposts': data['currentWeek']['metrics']['blogPosts'],
            'running': data['currentWeek']['metrics']['workouts']['running'],
            'gym': data['currentWeek']['metrics']['workouts']['gym']
        }
    }

    print(f"Added: {metrics}")
    print(f"New totals: {new_totals['totals']}")
    return new_totals

def send_confirmation_message(webhook_url, result):
    """Send confirmation message to Slack"""
    import requests
    from get_weekly_commits import get_weekly_commits

    added = result['added']
    totals = result['totals']

    total_social = totals['instagram'] + totals['tiktok'] + totals['hellotalk']
    total_workouts = totals['running'] + totals['gym']

    # Get current commit count
    commits = get_weekly_commits()

    confirmation = {
        "username": "GrindBot",
        "icon_emoji": ":white_check_mark:",
        "text": f"""✅ Well done! Progress updated successfully!

🔄 ADDED TODAY:
├─ 📱 Social: +{added['instagram'] + added['tiktok'] + added['hellotalk']} (IG: +{added['instagram']}, TT: +{added['tiktok']}, HT: +{added['hellotalk']})
├─ 💬 User Talks: +{added['usertalks']}
├─ ☕ Coffee Chats: +{added['coffeechats']}
├─ 🏃 Workouts: +{added['running'] + added['gym']} (Run: +{added['running']}, Gym: +{added['gym']})
└─ 📝 Blog Posts: +{added['blogposts']}

📊 NEW TOTALS:
├─ 🚀 Code Commits: {commits} builds
├─ 📱 Social Posts: {total_social} total
├─ 💬 User Talks: {totals['usertalks']} sessions
├─ ☕ Coffee Chats: {totals['coffeechats']} meetings
├─ 🏃 Workouts: {total_workouts} sessions
└─ 📝 Blog Posts: {totals['blogposts']} articles

Keep building! 🚀"""
    }

    try:
        response = requests.post(webhook_url, json=confirmation)
        if response.status_code == 200:
            print("Confirmation message sent successfully!")
        else:
            print(f"Failed to send confirmation: {response.status_code}")
    except Exception as e:
        print(f"Error sending confirmation: {e}")

if __name__ == "__main__":
    import os

    # Read from stdin or argument
    text = sys.stdin.read() if not sys.stdin.isatty() else ' '.join(sys.argv[1:])

    if text:
        metrics = parse_metrics(text)
        result = update_data(metrics)

        # Send confirmation message if webhook URL is provided
        webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        if webhook_url:
            send_confirmation_message(webhook_url, result)
    else:
        print("Usage: echo '1 0 0 2 0 0 1 1' | python3 slack_update.py")