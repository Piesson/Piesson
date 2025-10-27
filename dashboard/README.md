# 📊 Weekly Progress Dashboard

This dashboard tracks your weekly startup progress across 5 key metrics:

## 📈 Metrics Tracked

1. **💻 GitHub Commits** - Coding productivity
2. **📱 Social Content** - Instagram + TikTok posts
3. **👥 User Sessions** - App user engagement
4. **🤝 CTO Meetings** - Co-founder networking
5. **✍️ Blog Posts** - AI & startup content creation

## 🔄 How to Update

### Manual Update (Weekly)
```bash
# Edit the metrics in update_data.py
python3 dashboard/update_data.py

# Generate new SVG
python3 dashboard/generate_svg.py

# Commit changes
git add dashboard/
git commit -m "📊 Update weekly metrics"
git push
```

### Automatic Update (GitHub Actions)
- Runs daily at 6 PM KST
- Updates the dashboard SVG automatically
- Commits changes to the repo

## 📁 Files Structure

```
dashboard/
├── data.json              # Weekly metrics data
├── generate_svg.py        # SVG dashboard generator
├── update_data.py         # Data collection script
├── weekly_dashboard.svg   # Generated dashboard image
└── README.md             # This documentation
```

## 🎨 Customization

### Colors & Theme
Edit `generate_svg.py` to customize:
- Background gradients
- Card colors
- Text styles
- Layout positioning

### Data Sources
Connect automated data collection in `update_data.py`:
- GitHub API for commits
- Instagram/TikTok APIs for social metrics
- Your app analytics for user sessions
- Calendar API for meetings
- CMS API for blog posts

## 📊 Usage Tips

1. **Weekly Reviews**: Update metrics every Sunday
2. **Goal Setting**: Use trends to set weekly targets
3. **Progress Tracking**: Compare week-over-week growth
4. **Visual Motivation**: Share dashboard in social media
5. **Investor Updates**: Include dashboard in pitch decks

## 🚀 Future Enhancements

- [ ] Add interactive charts with Chart.js
- [ ] Connect to analytics APIs for automated data
- [ ] Add monthly/quarterly views
- [ ] Include revenue/funding metrics
- [ ] Mobile-optimized dashboard version