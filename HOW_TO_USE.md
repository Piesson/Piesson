# 🚀 How to Use Piesson Dashboard

> Automated startup grind tracking via Slack → GitHub profile

## ⚡ Quick Start

### Daily Routine
1. **7 AM**: Get Slack reminder with current week progress
2. **Input your grind**: Reply with 8 numbers
3. **Get confirmation**: "✅ Well done!" message
4. **See updates**: GitHub profile automatically refreshes

### Input Format
```
1 0 0 2 0 0 1 1
```
**Order**: Instagram, TikTok, HelloTalk, UserTalks, CoffeeChats, BlogPosts, Running, Gym

**Remember**: Enter **daily additions** only (not weekly totals)

## 📊 What Gets Tracked

| Metric | Description | Auto/Manual |
|--------|-------------|-------------|
| 🚀 Code Commits | GitHub commits | Auto |
| 💬 User Talks | All conversations/meetings | Manual |
| 📱 Social Posts | IG + TikTok + HelloTalk | Manual |
| ☕ Coffee Chats | Co-founder meetings | Manual |
| 🏃 Workouts | Running + Gym sessions | Manual |
| 📝 Blog Posts | AI/startup articles | Manual |

## 🎯 Examples

### Example Input: `2 1 0 3 1 0 1 0`
- Instagram: +2 posts
- TikTok: +1 post
- HelloTalk: +0 posts
- User Talks: +3 conversations
- Coffee Chats: +1 meeting
- Blog Posts: +0 articles
- Running: +1 session
- Gym: +0 sessions

### Zero Day: `0 0 0 0 0 0 0 0`
- No activity today (happens to everyone!)

## ⏰ Reminder System

### Morning (7 AM KST)
```
⏰ Time to grind

╔══════════════════════════╗
║  📊 THIS WEEK'S GRIND     ║
╚══════════════════════════╝

[Current metrics displayed]

💡 Let's ship it! 🚀
```

### Evening (7 PM KST) - Only if no input
```
🚨 GRIND CHECK: Still 0 today?

[Same metrics display]

💡 Time to lock in! 💪
```

## 🛠️ Manual Options

### GitHub Actions
1. Go to: https://github.com/Piesson/Piesson/actions
2. Select "Process Slack Response"
3. Click "Run workflow"
4. Enter your numbers: `1 0 0 2 0 0 1 1`

### Local Testing
```bash
cd /Users/apple/Desktop/Piesson
echo "1 0 0 2 0 0 1 1" | python3 dashboard/slack_update.py
```

## 🎨 Dashboard Features

- **Real-time sync**: Slack → GitHub profile
- **No duplicates**: Smart reminder system
- **Visual breakdown**: Shows individual + total metrics
- **Startup aesthetic**: Clean, modern dashboard design

## 💡 Pro Tips

1. **Consistency > Perfection**: Enter 0s rather than skip days
2. **Track everything**: Every conversation counts as user talk
3. **Batch similar activities**: Count all social platforms
4. **Weekly perspective**: Focus on trends, not daily fluctuations

---

**Philosophy**: "What gets measured gets managed" - track your startup journey daily! 📈