# CLAUDE.md

This file provides comprehensive guidance to Claude Code when working with the Piesson GitHub profile dashboard project.

## 🚨 CRITICAL RULES

### Git Commit Guidelines
- **NEVER use emojis in commit messages**
- Use clear, descriptive commit messages in English
- Follow conventional commit format: `type: description`
- Examples:
  - `feat: add new dashboard metric for workouts`
  - `fix: resolve XML parsing error in SVG`
  - `docs: update README with usage instructions`
  - `refactor: improve dashboard layout and styling`

## 📁 Project Structure

```
Piesson/
├── dashboard/                   # Dashboard system
│   ├── data.json               # Weekly metrics data storage
│   ├── generate_svg.py         # SVG dashboard generator
│   ├── update_data.py          # Data collection script (MAIN FILE TO EDIT)
│   ├── weekly_dashboard.svg    # Generated dashboard image
│   └── README.md              # Technical documentation
├── .github/workflows/          # GitHub Actions automation
│   └── update_dashboard.yml    # Daily auto-update workflow
├── profile-summary-card-output/ # GitHub stats cards
├── README.md                   # Main GitHub profile page
├── HOW_TO_USE.md              # User-friendly guide
└── CLAUDE.md                  # This file (Claude instructions)
```

## 🎯 Project Purpose

This is a **GitHub profile dashboard system** that tracks weekly startup progress metrics:

1. **CODE COMMITS** - GitHub commits (automated)
2. **SOCIAL POSTS** - Instagram + TikTok + HelloTalk posts (manual)
3. **USER TALKS** - All user conversations: chat/email/zoom/meetings (manual)
4. **COFFEE CHATS** - Co-founder candidate meetings (manual)
5. **WORKOUTS** - Running + Gym sessions (manual)
6. **BLOG POSTS** - AI & Startup content (manual)

## 🔧 How It Works

### Automation Flow
1. **GitHub Actions** runs daily at 6 PM KST
2. **Auto-collects** git commits via GitHub API
3. **Generates** new dashboard SVG
4. **Commits** and pushes changes automatically

### Manual Updates (Weekly)
1. User edits `dashboard/update_data.py`
2. Updates manual metrics (social, talks, workouts, etc.)
3. Runs update scripts
4. Commits changes

## 📝 Weekly Update Process

### Main File to Edit: `dashboard/update_data.py`

Look for this section (around line 128):

```python
manual_metrics = {
    # 📱 Social Media Posts (Instagram + TikTok + HelloTalk count)
    "socialContent": {
        "instagram": 4,   # ← Update weekly
        "tiktok": 3,      # ← Update weekly
        "hellotalk": 5    # ← Update weekly
    },

    # 👥 User Conversations (total conversations count)
    "userSessions": 134,  # ← Update weekly

    # ☕ Co-founder Coffee Chats (co-founder candidate meetings)
    "ctoMeetings": 5,     # ← Update weekly

    # ✍️ Blog Posts (AI/startup blog posts count)
    "blogPosts": 3,       # ← Update weekly

    # 🏃‍♂️ Workouts (exercise sessions)
    "workouts": {
        "running": 3,     # ← Update weekly
        "gym": 2          # ← Update weekly
    }
}
```

### Commands to Run (Weekly)
```bash
cd /Users/apple/Desktop/Piesson

# 1. Update data (git commits auto-calculated)
python3 dashboard/update_data.py

# 2. Generate new dashboard image
python3 dashboard/generate_svg.py

# 3. Commit and push changes
git add .
git commit -m "update: weekly metrics for [date]"
git push
```

## 🎨 Dashboard Design

### Current Theme: Modern Monochrome
- **Colors**: Black, white, gray only
- **Size**: 520x440px (compact for GitHub)
- **Layout**: 2x3 grid of metric cards
- **Style**: Clean cards with subtle shadows
- **Typography**: System fonts with proper weights

### Key Files:
- **generate_svg.py**: Contains all visual design code
- **data.json**: Stores current and historical data
- **weekly_dashboard.svg**: Final generated image

## 🔄 Making Changes

### Adding New Metrics
1. Update data structure in `data.json`
2. Modify `update_data.py` to include new metric
3. Add new card in `generate_svg.py`
4. Test and commit

### Changing Design
1. Edit `generate_svg.py`
2. Modify colors, layout, or styling
3. Run `python3 dashboard/generate_svg.py`
4. Test SVG output
5. Commit changes

### Debugging
- **XML errors**: Check for unescaped characters (&, <, >)
- **Layout issues**: Verify SVG coordinates and sizing
- **Data errors**: Check JSON format in data.json

## 📊 Data Structure

### Current Week Format
```json
{
  "currentWeek": {
    "startDate": "2025-01-20",
    "endDate": "2025-01-26",
    "metrics": {
      "commits": 42,
      "socialContent": {"instagram": 3, "tiktok": 2, "hellotalk": 4},
      "userSessions": 127,
      "ctoMeetings": 4,
      "blogPosts": 2,
      "workouts": {"running": 3, "gym": 2}
    }
  }
}
```

## ⚠️ Important Notes

### What's Automated
- Git commit counting (GitHub API)
- Dashboard SVG generation
- Daily updates via GitHub Actions
- README integration

### What's Manual
- Social media post counts
- User conversation tracking
- Co-founder meeting counts
- Blog post counts
- Workout session counts

### File Locations
- **User edits**: `dashboard/update_data.py` only
- **Generated files**: `dashboard/weekly_dashboard.svg`
- **Configuration**: `dashboard/data.json`
- **GitHub display**: README.md shows the dashboard

## 🚀 Quick Reference

### Most Common Task: Weekly Update
1. Open `dashboard/update_data.py`
2. Find `manual_metrics = {` (line ~128)
3. Update numbers for the week
4. Run: `python3 dashboard/update_data.py`
5. Run: `python3 dashboard/generate_svg.py`
6. Commit: `git add . && git commit -m "update: weekly metrics" && git push`

### Emergency Reset
If dashboard breaks:
1. Check `dashboard/weekly_dashboard.svg` for XML errors
2. Run `python3 dashboard/generate_svg.py` to regenerate
3. Check `dashboard/data.json` for valid JSON format

## 📋 Commit Message Examples

**Good Commits:**
- `update: weekly metrics for 2025-01-27`
- `fix: resolve SVG XML parsing error`
- `feat: add new workout tracking metric`
- `refactor: improve dashboard card layout`
- `docs: update usage instructions`

**Bad Commits (DON'T USE):**
- `📊 Update weekly dashboard` (has emoji)
- `fixed stuff` (not descriptive)
- `🎨 Redesign dashboard` (has emoji)

## 🎯 Success Criteria

Dashboard is working correctly when:
- SVG displays properly on GitHub profile
- No XML parsing errors
- Data updates reflect in dashboard
- GitHub Actions runs without errors
- Manual updates work via `update_data.py`

Remember: This is a **weekly habit tracker** for startup progress, displayed on GitHub profile for public accountability.