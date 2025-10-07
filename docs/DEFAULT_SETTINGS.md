# Default Settings Reference

## Overview

This document outlines the default settings for the AI Newsletter Scraper and how to adjust them for optimal results.

## Default Values (Updated)

### RSS Feed Settings
- **Default Feed URL**: `https://openai.com/news/rss.xml`
- **Entries per feed**: 25 (range: 5-100)
- **Why**: RSS feeds typically have many articles, so a higher default ensures you see more content

### Reddit Settings
- **Default Subreddits**: `AI_Agents,MachineLearning`
- **Posts per subreddit**: 10 (range: 5-50)
- **Sort**: hot
- **Why**: Reddit posts are more focused, 10 posts per subreddit is usually sufficient

### Blog Settings
- **Default URLs**: None (must be provided)
- **Articles per blog**: 10 (range: 5-20)
- **Template**: wordpress
- **Why**: Blogs typically have focused content, 10 articles is a good starting point

### X/Twitter Settings
- **Default Query**: `#AI`
- **Posts**: 10 (range: 5-50)
- **Why**: Twitter content is high-volume, 10 posts provides good sampling

### General Settings
- **Max total items**: 200 (range: 10-1000)
- **Why**: Allows viewing substantial content across multiple sources without overwhelming the UI

## How Limiting Works

### Per-Source Limits
Each source has its own limit setting:
```
Reddit: 10 posts × 2 subreddits = 20 items
RSS: 25 entries × 1 feed = 25 items
Total fetched = 45 items
```

### Global Max Total Items
After fetching from all sources, items are limited to `max_total_items`:
```
If total_fetched = 45 items
And max_total_items = 200
Then displayed = 45 items (no truncation)

If total_fetched = 250 items
And max_total_items = 200
Then displayed = 200 items (warning shown)
```

### Truncation Warning
When items are truncated, you'll see:
```
⚠️ Showing 200 of 250 items. Increase 'Max total items' to see more.
```

## Recommended Settings by Use Case

### 1. Quick Daily Overview
**Goal**: Fast scan of top content
```
Reddit: 5 posts per subreddit
RSS: 10 entries per feed
Max total: 50 items
```

### 2. Comprehensive Research
**Goal**: Deep dive into all available content
```
Reddit: 25 posts per subreddit
RSS: 50 entries per feed
Max total: 500 items
```

### 3. Multiple RSS Feeds
**Goal**: Aggregate from many sources
```
RSS feeds: 5-10 feeds
Entries per feed: 10-15
Max total: 200-300
```

### 4. Single Source Focus
**Goal**: Deep exploration of one source
```
Enable only one source
Set high limit (50-100)
Max total: 200
```

## RSS Feed Tips

### Popular AI RSS Feeds

Based on the OpenAI feed structure, here are recommended feeds:

```
https://openai.com/news/rss.xml
https://www.anthropic.com/news/rss
https://blog.google/technology/ai/rss/
https://blogs.microsoft.com/ai/feed/
https://ai.meta.com/blog/rss/
```

### Feed-Specific Recommendations

**High-Volume Feeds** (OpenAI, Google AI):
- Entries per feed: 25-50
- These feeds update frequently with many articles

**Low-Volume Feeds** (Company blogs):
- Entries per feed: 10-15
- These feeds update less frequently

**Multiple Feeds**:
- Entries per feed: 10-15 each
- Increase max total items: 200-300

## Adjusting Settings

### In the Streamlit UI

1. **Per-Source Settings**: Expand the source panel in sidebar
   - Reddit Settings
   - RSS Settings
   - Blog Settings
   - X (Twitter) Settings

2. **Global Settings**: Under "General" section
   - Max total items

### Settings Interaction

```
Items Displayed = min(
    sum(all_fetched_items),
    max_total_items
)
```

Example:
```
Reddit: 2 subreddits × 10 posts = 20
RSS: 1 feed × 25 entries = 25
Total fetched = 45
Max total = 200
Result: 45 items displayed ✓

RSS: 5 feeds × 50 entries = 250
Max total = 200
Result: 200 items displayed (50 truncated) ⚠️
```

## Performance Considerations

### Fetch Time Estimates

| Setting | Time (approx) |
|---------|---------------|
| Reddit (10 posts) | 2-3 seconds |
| Reddit (50 posts) | 5-7 seconds |
| RSS (25 entries, 1 feed) | 3-5 seconds |
| RSS (25 entries, 5 feeds) | 10-15 seconds |
| Blog (10 articles) | 5-10 seconds |

### Recommendations

- **Fast fetching**: Keep per-source limits low (10-15)
- **Comprehensive data**: Increase limits but expect 15-30 seconds
- **Multiple sources**: Balance limits across sources

## Troubleshooting

### "Only seeing 1 item instead of 10"

**Possible causes**:
1. ✅ **Max total items too low** - Increase from 100 to 200+
2. Feed actually has only 1 item - Check feed URL
3. Network/parsing issues - Check sidebar for errors

**Solution**:
```
1. Check sidebar success message: "✓ RSS: 10 articles"
2. Check if warning appears: "⚠️ Showing X of Y items"
3. Increase "Max total items" if warning shown
```

### "Not all RSS entries showing"

**Check**:
1. "Entries per feed" setting (increase to 25-50)
2. "Max total items" setting (increase to 200-300)
3. Look for truncation warning in sidebar

### "Fetching takes too long"

**Solutions**:
1. Reduce "Entries per feed" (10-15)
2. Reduce number of feeds (2-3 feeds)
3. Don't mix too many sources at once

## Best Practices

### 1. Start Conservative
Begin with default settings and increase as needed

### 2. Monitor Truncation Warnings
If you see truncation warnings, increase `max_total_items`

### 3. Balance Across Sources
```
Good:
Reddit: 10 posts × 2 = 20
RSS: 25 × 1 = 25
Total: 45 items ✓

Too much:
Reddit: 50 posts × 5 = 250
RSS: 100 × 5 = 500
Total: 750 items (slow, overwhelming)
```

### 4. Use Filtering
Instead of fetching 500 items, fetch 100 and use filters:
- Min score
- Min comments  
- Time period
- Source selection

## Configuration File

You can also set defaults in `config.json`:

```json
{
  "rss": {
    "enabled": true,
    "limit": 25,
    "feed_urls": [
      "https://openai.com/news/rss.xml"
    ]
  }
}
```

## Summary

**Key Changes from Initial Release**:
- ✅ RSS default limit: 10 → **25 entries per feed**
- ✅ Max total items: 100 → **200 items**
- ✅ Default RSS feed: Updated to OpenAI news feed
- ✅ Added truncation warnings
- ✅ Added helpful tooltips

**Result**: Better defaults that show more content while maintaining performance.

---

**Last Updated**: October 8, 2025  
**Version**: 1.1

