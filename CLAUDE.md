# CLAUDE.md

This file provides guidance for Claude Code when working with the Piesson GitHub Profile Dashboard project.

## 🚨 CRITICAL RULES

### Git Commit Guidelines
- **NEVER use emojis in commit messages**
- Use clear, descriptive commit messages in English
- Follow conventional commit format: `type: description`

## 🎯 Project Overview

**Piesson GitHub Profile Dashboard** - Automated startup progress tracking system that displays weekly grind metrics on GitHub profile.

## 📁 Key Files Structure

```
dashboard/
├── data.json                    # Current week metrics storage
├── generate_svg.py             # Creates GitHub profile SVG
├── generate_slack_message.py   # Creates daily Slack reminders
├── slack_update.py             # Processes Slack input and updates data
├── check_daily_update.py       # Prevents duplicate reminders
└── weekly_dashboard.svg        # Generated GitHub profile dashboard

.github/workflows/
└── update_dashboard.yml        # Automation: daily reminders + auto-updates
```

## 🔄 System Flow

### Daily Automation
1. **7 AM KST**: Slack reminder with current metrics
2. **User inputs**: 8 numbers via Slack (daily additions)
3. **Auto-processing**: Data updates + confirmation message
4. **GitHub sync**: SVG regenerated + committed automatically
5. **7 PM KST**: Reminder if no input received (anti-procrastination)

### Metrics Tracked
- 🚀 **Code Commits** (auto-calculated from git)
- 💬 **User Talks** (conversations/meetings)
- 📱 **Social Posts** (Instagram + TikTok + HelloTalk)
- ☕ **Coffee Chats** (co-founder meetings)
- 🏃 **Workouts** (Running + Gym sessions)
- 📝 **Blog Posts** (AI/startup articles)

## 🎮 Usage

### Input Format
Slack message: `1 0 0 2 0 0 1 1`
Order: `(IG, TT, HT, UserTalks, CoffeeChats, BlogPosts, Running, Gym)`

### Additive System
- Enter **daily additions** only (not totals)
- System automatically adds to existing weekly totals
- No conflicts: duplicate reminders prevented by date checking

## 🛠️ Technical Details

### Slack Integration
- **Morning**: "⏰ Time to grind" + current metrics
- **Evening**: "🚨 GRIND CHECK: Still 0 today?" (if no input)
- **Confirmation**: "✅ Well done!" with breakdown after input

### GitHub Actions
- **Triggers**: Schedule (2x daily) + data.json changes
- **Smart reminders**: Only sends if no input received
- **Auto-commits**: SVG updates pushed automatically

### Data Flow
```
Slack Input → slack_update.py → data.json → generate_svg.py → GitHub Profile
```

## 🔧 Development Guidelines

### When Modifying
1. **Slack messages**: Edit `generate_slack_message.py`
2. **Input parsing**: Edit `slack_update.py`
3. **Dashboard design**: Edit `generate_svg.py`
4. **Scheduling**: Edit `.github/workflows/update_dashboard.yml`

### Testing
- **Local test**: `echo "1 0 0 2 0 0 1 1" | python3 dashboard/slack_update.py`
- **Message preview**: `python3 dashboard/generate_slack_message.py morning`
- **Manual trigger**: GitHub Actions → "Run workflow"

### Key Functions
- `parse_metrics()`: Converts input to metric object
- `update_data()`: Adds to existing totals (additive system)
- `generate_slack_message()`: Creates time-appropriate messages
- `check_daily_update()`: Prevents duplicate reminders

## 🚀 Startup Grind Philosophy

This system embodies the "grind mindset" - consistent daily tracking of progress across all dimensions of startup building: code, community, content, connections, health, and thought leadership.

**Core principle**: "What gets measured gets managed" - every day counts in the startup journey.