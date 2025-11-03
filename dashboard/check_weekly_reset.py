#!/usr/bin/env python3
"""
Check if we're in a new week and reset metrics if needed
Runs daily at 7 AM KST before sending reminder
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# KST = UTC + 9 hours
KST = timezone(timedelta(hours=9))

def get_current_week_info():
    """Get current week's Monday and ISO week identifier"""
    today = datetime.now(KST)
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    week_id = f"{monday.year}-W{monday.isocalendar()[1]:02d}"

    return {
        'week_id': week_id,
        'monday': monday.strftime('%Y-%m-%d'),
        'sunday': sunday.strftime('%Y-%m-%d'),
        'monday_display': monday.strftime('%m/%d/%Y'),
        'sunday_display': sunday.strftime('%m/%d/%Y')
    }

def save_to_history(data, current_week_info):
    """Save current week data to weeklyHistory before reset"""
    current = data['currentWeek']

    if not current.get('metrics'):
        print("No metrics to save (empty week)")
        return False

    # Calculate the week_id from the stored startDate (last week)
    # Don't use current_week_info['week_id'] as that's for the NEW week
    stored_start = current.get('startDate')
    if stored_start:
        # Parse stored date and calculate its week number
        stored_date = datetime.strptime(stored_start, '%Y-%m-%d')
        week_num = stored_date.isocalendar()[1]
        week_id = f"{stored_date.year}-W{week_num:02d}"
    else:
        # Fallback: calculate last week's ID
        today = datetime.now(KST)
        last_monday = today - timedelta(days=today.weekday() + 7)
        week_id = f"{last_monday.year}-W{last_monday.isocalendar()[1]:02d}"

    history_entry = {
        "week": week_id,
        "startDate": current.get('startDate', current_week_info['monday']),
        "endDate": current.get('endDate', current_week_info['sunday']),
        "metrics": {
            "commits": current['metrics'].get('commits', 0),
            "socialContent": current['metrics'].get('socialContent', {
                'instagram': 0,
                'tiktok': 0,
                'hellotalk': 0
            }),
            "userSessions": current['metrics'].get('userSessions', 0),
            "ctoMeetings": current['metrics'].get('ctoMeetings', 0),
            "blogPosts": current['metrics'].get('blogPosts', 0),
            "workouts": current['metrics'].get('workouts', {
                'running': 0,
                'gym': 0
            })
        }
    }

    # Check if this week already exists in history
    existing_index = None
    for i, entry in enumerate(data['weeklyHistory']):
        if entry.get('week') == week_id:
            existing_index = i
            break

    if existing_index is not None:
        # Update existing entry (overwrite with latest data)
        data['weeklyHistory'][existing_index] = history_entry
        print(f"Updated existing history entry for {week_id}")
    else:
        # Add new entry at the beginning
        data['weeklyHistory'].insert(0, history_entry)
        print(f"Added new history entry for {week_id}")

    # Keep only last 12 weeks
    data['weeklyHistory'] = data['weeklyHistory'][:12]

    return True

def reset_current_week_metrics(data):
    """Reset all metrics to 0 (except commits which is calculated from git)"""
    data['currentWeek']['metrics'] = {
        'socialContent': {
            'instagram': 0,
            'tiktok': 0,
            'hellotalk': 0
        },
        'userSessions': 0,
        'ctoMeetings': 0,
        'blogPosts': 0,
        'workouts': {
            'running': 0,
            'gym': 0
        }
    }
    print("✅ All metrics reset to 0")

def check_and_reset_weekly_data():
    """Main function: check if new week and reset if needed"""
    data_file = Path('dashboard/data.json')

    if not data_file.exists():
        print("❌ data.json not found")
        sys.exit(1)

    # Load current data
    with open(data_file, 'r') as f:
        data = json.load(f)

    # Get current week info
    current_week = get_current_week_info()

    # Get stored week's Monday date
    stored_start_date = data['currentWeek'].get('startDate', '')

    print(f"Current week Monday: {current_week['monday']}")
    print(f"Stored week Monday: {stored_start_date}")

    # Check if we're in a new week
    if stored_start_date != current_week['monday']:
        print(f"\n🔄 NEW WEEK DETECTED: {current_week['week_id']}")
        print(f"   Period: {current_week['monday_display']} - {current_week['sunday_display']}")

        # Step 1: Save last week's data to history
        print("\n📚 Step 1: Saving last week to history...")
        saved = save_to_history(data, current_week)

        if saved:
            # Step 2: Generate history SVG for last week (will be done by generate_weekly_history.py)
            print("   (History SVG will be generated in next step)")

        # Step 3: Reset current week metrics
        print("\n🔄 Step 2: Resetting current week metrics...")
        reset_current_week_metrics(data)

        # Step 4: Update week dates
        print("\n📅 Step 3: Updating week dates...")
        data['currentWeek']['startDate'] = current_week['monday']
        data['currentWeek']['endDate'] = current_week['sunday']

        # Step 5: Save updated data
        print("\n💾 Step 4: Saving data.json...")
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✅ Weekly reset completed for {current_week['week_id']}")
        print(f"   All metrics reset to 0")
        print(f"   History saved (last {len(data['weeklyHistory'])} weeks)")

        # Exit code 0 = reset happened, workflow should generate SVGs and commit
        sys.exit(0)
    else:
        print(f"\n✓ Same week ({current_week['week_id']}), no reset needed")
        # Exit code 1 = no reset, workflow continues normally
        sys.exit(1)

if __name__ == "__main__":
    check_and_reset_weekly_data()
