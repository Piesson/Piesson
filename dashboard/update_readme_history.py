#!/usr/bin/env python3
"""Update README.md with the current and completed weekly history table."""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone

from metric_totals import grouped_total
from week_utils import iso_week_id

KST = timezone(timedelta(hours=9))

LIVE_DASHBOARD_URL = (
    "https://raw.githubusercontent.com/Piesson/Piesson/main/"
    "dashboard/weekly_dashboard.svg"
)


def _synthesize_live_entry(current):
    """Build a weekly_history-shaped dict from data.currentWeek so the same
    rendering path produces a 'live' first row in the table."""
    if not isinstance(current, dict):
        return None
    start = current.get('startDate') or ''
    end = current.get('endDate') or ''
    if not start:
        return None
    try:
        week_id = iso_week_id(datetime.strptime(start, '%Y-%m-%d'))
    except ValueError:
        return None
    return {
        'week': week_id,
        'startDate': start,
        'endDate': end,
        'metrics': current.get('metrics', {}),
        'manualMetricsSource': current.get('manualMetricsSource'),
        '_live': True,
    }


def _build_rows(weekly_history, live_entry):
    """Yield history entries in render order with the live row first.
    weeklyHistory is capped at 11 so the total stays at 12 rows when live
    is present."""
    if live_entry is not None:
        yield live_entry
        for entry in weekly_history[:11]:
            yield entry
    else:
        for entry in weekly_history[:12]:
            yield entry


def generate_history_table(weekly_history, current_week=None):
    """Generate Markdown table for weekly history.

    If current_week is provided, a synthetic 'Week N (live)' row is prepended
    and the cap on completed weeks becomes 11 so the table stays at 12 rows.
    """
    live_entry = _synthesize_live_entry(current_week) if current_week else None
    if not weekly_history and live_entry is None:
        return ""

    lines = []
    lines.append("# Weekly History")
    lines.append("")
    lines.append("| Week | Period | 🚀 PRs | 📱 Social | 💬 Talks | ☕ Coffee | 🏃 Workouts | 📝 Posts |")
    lines.append("|------|--------|--------|----------|---------|---------|------------|----------|")

    for entry in _build_rows(weekly_history, live_entry):
        week_id = entry['week']
        week_num = week_id.split('-W')[1]

        try:
            start_date = datetime.strptime(entry['startDate'], '%m/%d/%Y')
            end_date = datetime.strptime(entry['endDate'], '%m/%d/%Y')
            period = f"{start_date.strftime('%m/%d/%Y')} - {end_date.strftime('%m/%d/%Y')}"
        except:
            period = f"{entry['startDate']} - {entry['endDate']}"

        metrics = entry['metrics']

        total_social = grouped_total(metrics.get('socialContent', {}))
        total_workouts = grouped_total(metrics.get('workouts', {}))

        prs = metrics.get('pullRequests', 0)
        user_sessions = metrics.get('userSessions', 0)
        cto_meetings = metrics.get('ctoMeetings', 0)
        blog_posts = metrics.get('blogPosts', 0)
        # Managed weeks display honest zeros; untouched legacy gaps use em-dashes.
        def _cell(v, week_has_data):
            return str(v) if week_has_data else '\u2014'
        _filed = (
            entry.get('manualMetricsSource') == 'daily-notes'
            or any([user_sessions, total_social, cto_meetings, total_workouts, blog_posts])
        )

        if entry.get('_live'):
            week_label = f"[**Week {week_num} (live)**]({LIVE_DASHBOARD_URL})"
        else:
            svg_url = f"https://raw.githubusercontent.com/Piesson/Piesson/main/dashboard/history/weekly_history_{week_id}.svg"
            week_label = f"[**Week {week_num}**]({svg_url})"

        lines.append(
            f"| {week_label} | {period} | {prs} | {_cell(total_social, _filed)} | "
            f"{_cell(user_sessions, _filed)} | {_cell(cto_meetings, _filed)} | {_cell(total_workouts, _filed)} | {_cell(blog_posts, _filed)} |"
        )

    lines.append("")
    current_date = datetime.now(KST).strftime('%m/%d/%y')
    lines.append(f'<div align="right"><sub>updated at {current_date}</sub></div>')
    lines.append("")
    lines.append("")  # Extra blank line before next section
    return "\n".join(lines)

def update_readme_with_history():
    """Update README.md with weekly history section"""
    readme_path = Path('README.md')
    data_path = Path('dashboard/data.json')

    if not readme_path.exists():
        print("❌ README.md not found")
        return False

    if not data_path.exists():
        print("❌ data.json not found")
        return False

    with open(data_path, 'r') as f:
        data = json.load(f)

    weekly_history = data.get('weeklyHistory', [])
    current_week = data.get('currentWeek')

    if not weekly_history and not current_week:
        print("No weekly history or current week to add")
        return False

    with open(readme_path, 'r') as f:
        readme_content = f.read()

    history_table = generate_history_table(weekly_history, current_week=current_week)

    history_pattern = r'# Weekly History\n\n\|.*?\n\|.*?\n(?:\|.*?\n)*\n(?:<div align="right"><sub>updated at \d{2}/\d{2}/\d{2}</sub></div>\n)?\n?'

    if re.search(history_pattern, readme_content):
        readme_content = re.sub(history_pattern, history_table, readme_content)
        print("✅ Updated existing Weekly History section")
    else:
        progress_tracker_pattern = r'(# Consistent enough\?\n\n.*?</details>\n\n<div align="right"><sub>updated at \d{2}/\d{2}/\d{2}</sub></div>\n\n)'
        match = re.search(progress_tracker_pattern, readme_content, re.DOTALL)

        if match:
            insert_pos = match.end()
            readme_content = (
                readme_content[:insert_pos] +
                history_table + '\n' +
                readme_content[insert_pos:]
            )
            print("✅ Added new Weekly History section after Consistent enough?")
        else:
            tech_stack_index = readme_content.find('# Tech Stack')
            if tech_stack_index != -1:
                readme_content = (
                    readme_content[:tech_stack_index] +
                    history_table + '\n\n' +
                    readme_content[tech_stack_index:]
                )
                print("✅ Added new Weekly History section before Tech Stack")
            else:
                readme_content += '\n\n' + history_table
                print("✅ Added new Weekly History section at end")

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    return True

if __name__ == "__main__":
    success = update_readme_with_history()
    exit(0 if success else 1)
