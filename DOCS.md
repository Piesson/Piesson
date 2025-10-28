# GitHub Profile Dashboard - System Docs

**핵심**: 자동화된 GitHub 프로필 대시보드. 코드 작성 → Slack 입력 → README 자동 업데이트.

---

## System Overview

```
GitHub Profile (README.md)
├─ Profile Card         ← GitHub API (2020-2025 data, hourly)
├─ Weekly Dashboard     ← Git commits + Slack input (real-time)
├─ Progress Tracker     ← Cumulative charts (weekly reset)
└─ Weekly History       ← Last 12 weeks table
```

---

## What Updates What

### 3 GitHub Actions Workflows

| Workflow | Trigger | Updates | Scripts |
|----------|---------|---------|---------|
| **profile-summary-cards.yml** | Daily 7AM KST | Profile card + timestamp | `generate_profile_card.py` |
| **update_dashboard.yml** | Schedule (7AM/7PM) + Push | Dashboard + Progress + History | `generate_svg.py`<br>`update_readme_charts.py`<br>`update_readme_history.py` |
| **slack_response.yml** | Manual (Slack input) | Dashboard (triggers update_dashboard) | `slack_update.py`<br>`generate_svg.py` |

---

## Data Flow

```
1. Input
   ├─ Git commits (auto-counted weekly)
   └─ Slack: "1 0 0 2 0 0 1 1"
        ↓
2. Update data.json
   ├─ commits: auto-calculated from git
   └─ other metrics: additive (current + new)
        ↓
3. Generate SVGs
   ├─ profile-summary-card-output/default/0-profile-details.svg
   └─ dashboard/weekly_dashboard.svg
        ↓
4. Update README.md
   ├─ Profile card timestamp (below card)
   ├─ Dashboard timestamp (below SVG)
   ├─ Progress Tracker charts + timestamp
   └─ Weekly History table + timestamp
        ↓
5. Git commit + push
```

---

## Core Python Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| `generate_profile_card.py` | 4-quadrant pie chart | Profile SVG + README timestamp |
| `generate_svg.py` | Weekly dashboard 6 metrics | Dashboard SVG + README timestamp |
| `update_readme_charts.py` | Progress Tracker charts | README Progress section |
| `update_readme_history.py` | Weekly history table | README History section |
| `slack_update.py` | Parse Slack input | data.json (additive) |
| `check_weekly_reset.py` | Monday reset | Save history, reset metrics |

---

## Slack Messages & Input

### 3 Types of Messages

| Type | When | Icon | Who |
|------|------|------|-----|
| **Weekly Summary** | Mon 7AM KST | 🎉 | GrindBot |
| **Morning Reminder** | Tue-Sun 7AM KST | 🔥 | GrindBot |
| **Evening Reminder** | Daily 7PM KST | 🚨 | GrindBot |

### When You Get Messages

**Monday 7AM**: Weekly Summary (last week's totals + daily avg)
```
🎉 Fresh week huh?
Last Week: 83 commits, 2 talks, 3 social, 0 coffee, 7 workouts, 0 blog
```

**Tue-Sun 7AM**: Morning Reminder (this week's current totals)
```
🔥 Time to get things done
THIS WEEK: 120 commits, 15 talks, 9 social, 2 coffee, 9 workouts, 1 blog
📥 INPUT: 2 1 0 3 0 1 2 0
(Talks, IG, TT, HT, Coffee, Blog, Run, Gym)
```

**Daily 7PM**: Evening Reminder (same as morning, different tone)
```
🚨 GRIND CHECK: Still 0 today?
THIS WEEK: 120 commits, 15 talks, 9 social, 2 coffee, 9 workouts, 1 blog
📥 INPUT: 2 1 0 3 0 1 2 0
(Talks, IG, TT, HT, Coffee, Blog, Run, Gym)
```

### Message Skip Logic

Messages skip if `data.json → lastUpdated` == today (KST).

**Example**:
- 7AM: Morning reminder arrives
- 8AM: You input "2 1 0 3 0 1 2 0" → `lastUpdated` = today
- 7PM: Evening reminder **skipped** (already updated today)
- Next day 7AM: Morning reminder arrives again (new day)

### Input Format

**8 numbers**: `2 1 0 3 0 1 2 0`

**Order** (matches dashboard layout: Talks → Social → Coffee → Workouts → Blog):
```
[Talks] [IG] [TT] [HT] [Coffee] [Blog] [Run] [Gym]
```

**Example**: `2 1 0 3 0 1 2 0`
- User Talks: 2
- Instagram: 1
- TikTok: 0
- HelloTalk: 3
- Coffee Chats: 0
- Blog Posts: 1
- Running: 2
- Gym: 0

**Additive**: New values ADD to existing totals.

**Note**: Commits auto-counted from git. Don't input manually.

---

## Manual Testing

### Update Profile Card
```bash
python dashboard/generate_profile_card.py
```

### Update Dashboard
```bash
python dashboard/generate_svg.py
python dashboard/update_readme_history.py
python dashboard/update_readme_charts.py
```

### Process Slack Input
```bash
echo "2 1 0 3 0 1 2 0" | python dashboard/slack_update.py
python dashboard/generate_svg.py
```

### Full Regeneration
```bash
python dashboard/generate_profile_card.py
python dashboard/generate_svg.py
python dashboard/update_readme_history.py
python dashboard/update_readme_charts.py
git add -A && git commit -m "manual: regenerate dashboard" && git push
```

---

## Schedule

| Time | Day | Action |
|------|-----|--------|
| 7AM KST | Mon | Profile card + Weekly reset + Slack summary |
| 7AM KST | Tue-Sun | Profile card + Morning reminder |
| 7PM KST | Daily | Evening reminder (if no update) |
| On push | Any | Dashboard regeneration |

---

## Key Files

```
.github/workflows/
├─ profile-summary-cards.yml    (Profile card generation)
├─ update_dashboard.yml         (Dashboard + reminders + reset)
└─ slack_response.yml           (Slack input processor)

dashboard/
├─ data.json                    (Single source of truth)
├─ generate_profile_card.py     (Profile SVG + README)
├─ generate_svg.py              (Dashboard SVG + README)
├─ update_readme_charts.py      (Progress Tracker)
├─ update_readme_history.py     (Weekly History)
├─ slack_update.py              (Parse Slack → data.json)
└─ check_weekly_reset.py        (Monday reset)

README.md                       (Auto-updated by 4 scripts)
```

---

## Data Storage

**`dashboard/data.json`**
```json
{
  "lastUpdated": "2025-10-27",        // KST, updated by slack_update.py
  "currentWeek": {
    "startDate": "2025-10-27",        // Monday (KST)
    "endDate": "2025-11-02",          // Sunday (KST)
    "metrics": {
      "commits": 120,                 // Auto from git (NOT manual)
      "socialContent": {
        "instagram": 5,               // Additive from Slack
        "tiktok": 3,
        "hellotalk": 1
      },
      "userSessions": 15,             // Additive from Slack
      "ctoMeetings": 2,
      "blogPosts": 1,
      "workouts": {
        "running": 3,
        "gym": 6
      }
    }
  },
  "weeklyHistory": [                  // Last 12 weeks only
    {
      "week": "2025-W43",
      "startDate": "10/20/2025",
      "endDate": "10/26/2025",
      "metrics": { ... }              // Snapshot at week end
    }
  ]
}
```

---

## Timezone

**All timestamps use KST (UTC+9)**:
```python
KST = timezone(timedelta(hours=9))
datetime.now(KST).strftime('%m/%d/%y')
```

---

## Troubleshooting

**Profile card shows 0 commits?**
→ Missing `SUMMARY_CARDS_TOKEN` secret. Add GitHub PAT with `repo` scope.

**Dashboard not updating?**
→ Check `data.json → lastUpdated`. If today's date, reminder already sent.

**Tech Stack not rendering?**
→ Missing blank line before `# Tech Stack`. Markdown requires blank line after HTML.

**Duplicate sections in README?**
→ Scripts use regex patterns. Check patterns match current README structure.

**Monday reset not working?**
→ Verify cron: `0 22 * * 1` (10PM UTC = 7AM KST Monday).

---

## README Structure (Auto-updated)

```markdown
Profile Card Image
<div align="right"><sub>updated at MM/DD/YY</sub></div>  ← generate_profile_card.py

# Grinding metics
Dashboard SVG
<div align="right"><sub>updated at MM/DD/YY</sub></div>  ← generate_svg.py

# Progress Tracker
Cumulative Chart
<details><strong>More details</strong></details>
<div align="right"><sub>updated at MM/DD/YY</sub></div>  ← update_readme_charts.py

# Weekly History
Table (last 12 weeks)
<div align="right"><sub>updated at MM/DD/YY</sub></div>  ← update_readme_history.py

# Tech Stack
```

---

## Critical Rules

1. **Never manually edit `data.json → commits`**. Auto-calculated from git.
2. **All other metrics are additive**. New values ADD to existing.
3. **Monday resets everything**. History saved, metrics → 0.
4. **KST timezone everywhere**. No UTC timestamps in README.
5. **Blank lines matter**. Markdown headers need blank lines before them.

---

## That's It

This is a self-updating GitHub profile dashboard. Code → Slack → README. Automated with GitHub Actions. All timestamps KST. History kept for 12 weeks. Done.
