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
    """Extract numbers from Slack message"""
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