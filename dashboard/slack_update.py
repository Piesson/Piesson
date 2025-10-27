#!/usr/bin/env python3
"""
Ultra-simple Slack metrics parser
Usage: echo "Instagram: 3, TikTok: 2" | python3 slack_update.py
"""

import json
import re
import sys
from datetime import datetime

def parse_metrics(text):
    """Extract numbers from Slack message (supports both formats)"""
    # Try new 7-number format first: "3 2 1 10 2 1 5"
    numbers = re.findall(r'\d+', text.strip())
    if len(numbers) >= 7:
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
    """Update data.json with new metrics"""
    with open('dashboard/data.json', 'r') as f:
        data = json.load(f)

    # Update metrics (keep commits as is - auto-calculated)
    data['currentWeek']['metrics']['socialContent'] = {
        'instagram': metrics['instagram'],
        'tiktok': metrics['tiktok'],
        'hellotalk': metrics['hellotalk']
    }
    data['currentWeek']['metrics']['userSessions'] = metrics['usertalks']
    data['currentWeek']['metrics']['ctoMeetings'] = metrics['coffeechats']
    data['currentWeek']['metrics']['blogPosts'] = metrics['blogposts']
    data['currentWeek']['metrics']['workouts'] = {
        'running': metrics['running'],
        'gym': metrics['gym']
    }
    data['lastUpdated'] = datetime.now().strftime("%Y-%m-%d")

    with open('dashboard/data.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Updated: {metrics}")

if __name__ == "__main__":
    # Read from stdin or argument
    text = sys.stdin.read() if not sys.stdin.isatty() else ' '.join(sys.argv[1:])

    if text:
        metrics = parse_metrics(text)
        update_data(metrics)
    else:
        print("Usage: echo 'Instagram: 3, TikTok: 2, ...' | python3 slack_update.py")