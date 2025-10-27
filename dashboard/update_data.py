#!/usr/bin/env python3
"""
Weekly data collection script for startup progress dashboard
"""

import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path

class DataCollector:
    def __init__(self):
        self.data_file = Path('dashboard/data.json')

    def load_current_data(self):
        """Load existing data or create new structure"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
                "currentWeek": {},
                "weeklyHistory": []
            }

    def get_week_dates(self):
        """Get current week's start and end dates (Monday to Sunday)"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        return {
            "startDate": start_of_week.strftime("%Y-%m-%d"),
            "endDate": end_of_week.strftime("%Y-%m-%d"),
            "week": f"{start_of_week.year}-W{start_of_week.isocalendar()[1]:02d}"
        }

    def collect_github_commits(self, username="Piesson"):
        """Collect commits from GitHub API"""
        try:
            # Get commits from the last week
            week_dates = self.get_week_dates()
            since = week_dates["startDate"] + "T00:00:00Z"

            # You might want to add your GitHub token for higher rate limits
            headers = {}
            if os.getenv('GITHUB_TOKEN'):
                headers['Authorization'] = f"token {os.getenv('GITHUB_TOKEN')}"

            # Get all repos
            repos_url = f"https://api.github.com/users/{username}/repos"
            repos_response = requests.get(repos_url, headers=headers)

            if repos_response.status_code != 200:
                print(f"Failed to fetch repos: {repos_response.status_code}")
                return 0

            total_commits = 0
            repos = repos_response.json()

            for repo in repos[:10]:  # Limit to top 10 repos to avoid rate limits
                commits_url = f"https://api.github.com/repos/{username}/{repo['name']}/commits"
                params = {'since': since, 'author': username}

                commits_response = requests.get(commits_url, headers=headers, params=params)
                if commits_response.status_code == 200:
                    commits = commits_response.json()
                    total_commits += len(commits)

            return total_commits

        except Exception as e:
            print(f"Error collecting GitHub data: {e}")
            return 0

    def update_metrics(self, manual_data=None):
        """Update current week metrics"""
        week_info = self.get_week_dates()

        if manual_data:
            # Use manually provided data + auto-collected commits
            metrics = {
                "commits": self.collect_github_commits(),  # Always auto-collected
                "socialContent": manual_data.get("socialContent", {"instagram": 0, "tiktok": 0}),
                "userSessions": manual_data.get("userSessions", 0),
                "ctoMeetings": manual_data.get("ctoMeetings", 0),
                "blogPosts": manual_data.get("blogPosts", 0),
                "workouts": manual_data.get("workouts", {"running": 0, "gym": 0})
            }
        else:
            # Collect automated data
            metrics = {
                "commits": self.collect_github_commits(),
                "socialContent": {
                    "instagram": 0,  # Manual input required
                    "tiktok": 0,     # Manual input required
                    "hellotalk": 0   # Manual input required
                },
                "userSessions": 0,   # Manual input required
                "ctoMeetings": 0,    # Manual input required
                "blogPosts": 0,      # Manual input required
                "workouts": {
                    "running": 0,    # Manual input required
                    "gym": 0         # Manual input required
                }
            }

        return {
            "startDate": week_info["startDate"],
            "endDate": week_info["endDate"],
            "metrics": metrics
        }

    def save_data(self, data):
        """Save updated data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data updated: {self.data_file}")

def main():
    collector = DataCollector()

    # 🔥 WEEKLY UPDATE SECTION 🔥
    # 매주 일요일마다 이 숫자들만 수정하세요!
    # Git commits는 자동으로 계산됩니다.

    manual_metrics = {
        # 📱 Social Media Posts (인스타그램 + 틱톡 + HelloTalk 개수)
        "socialContent": {
            "instagram": 4,   # ← 이 주에 올린 인스타 포스트 개수
            "tiktok": 3,      # ← 이 주에 올린 틱톡 개수
            "hellotalk": 5    # ← 이 주에 올린 HelloTalk 포스트 개수
        },

        # 👥 User Conversations (사용자와 대화한 총 횟수)
        "userSessions": 134,  # ← 채팅/이메일/줌콜/실제만남 모든 대화 횟수

        # ☕ Co-founder Coffee Chats (잠재적 공동창업자와 커피챗 횟수)
        "ctoMeetings": 5,     # ← 이번 주 공동창업자 후보와 커피챗 횟수

        # ✍️ Blog Posts (블로그/웹사이트에 쓴 글 개수)
        "blogPosts": 3,       # ← AI/스타트업 관련 포스트 개수

        # 🏃‍♂️ Workouts (운동 횟수)
        "workouts": {
            "running": 3,     # ← 이번 주 러닝 횟수
            "gym": 2          # ← 이번 주 헬스장 간 횟수
        }
    }

    # Load existing data
    data = collector.load_current_data()

    # Update current week
    current_week = collector.update_metrics(manual_metrics)
    data['currentWeek'] = current_week
    data['lastUpdated'] = datetime.now().strftime("%Y-%m-%d")

    # Add to history if it's a new week
    week_info = collector.get_week_dates()
    existing_week = next((w for w in data['weeklyHistory'] if w.get('week') == week_info['week']), None)

    if not existing_week:
        # New week - add current week to history
        history_entry = {
            "week": week_info['week'],
            "startDate": current_week['startDate'],
            "endDate": current_week['endDate'],
            "metrics": {
                "commits": manual_metrics.get('commits', 0),
                "socialContent": manual_metrics['socialContent']['instagram'] + manual_metrics['socialContent']['tiktok'] + manual_metrics['socialContent']['hellotalk'],
                "userSessions": manual_metrics['userSessions'],
                "ctoMeetings": manual_metrics['ctoMeetings'],
                "blogPosts": manual_metrics['blogPosts'],
                "workouts": manual_metrics['workouts']['running'] + manual_metrics['workouts']['gym']
            }
        }
        data['weeklyHistory'].insert(0, history_entry)

        # Keep only last 8 weeks
        data['weeklyHistory'] = data['weeklyHistory'][:8]

    # Save updated data
    collector.save_data(data)

    print("📊 Dashboard data updated successfully!")
    print(f"Current week: {current_week['startDate']} → {current_week['endDate']}")
    print(f"Metrics: {current_week['metrics']}")

if __name__ == "__main__":
    main()