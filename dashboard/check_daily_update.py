#!/usr/bin/env python3
"""
Check if daily update has been made today
Returns exit code 0 if update needed, 1 if already updated
"""

import json
import sys
from datetime import datetime, timezone, timedelta

# KST = UTC + 9 hours
KST = timezone(timedelta(hours=9))

def check_daily_update():
    """Check if data.json was updated today (KST timezone)"""
    try:
        with open('dashboard/data.json', 'r') as f:
            data = json.load(f)

        last_updated = data.get('lastUpdated', '')
        today = datetime.now(KST).strftime('%Y-%m-%d')

        if last_updated == today:
            print(f"Already updated today: {today}")
            sys.exit(1)  # Don't send reminder
        else:
            print(f"No update today. Last updated: {last_updated}, Today: {today}")
            sys.exit(0)  # Send reminder

    except Exception as e:
        print(f"Error checking update: {e}")
        sys.exit(0)  # Send reminder on error

if __name__ == "__main__":
    check_daily_update()