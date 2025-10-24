# Managing Content Sources

## Overview

This guide explains how to add, update, and remove content sources using both the UI (Settings page) and API (programmatic access).

**Last Updated**: 2025-01-24
**Related Docs**: [RECOMMENDED_CONTENT_SOURCES.md](../RECOMMENDED_CONTENT_SOURCES.md), [QUICK_ADD_SOURCES.md](./QUICK_ADD_SOURCES.md)

---

## Table of Contents

1. [UI Method (Settings Page)](#ui-method-settings-page)
2. [API Method (Programmatic)](#api-method-programmatic)
3. [Workspace Configuration Structure](#workspace-configuration-structure)
4. [Common Operations](#common-operations)
5. [Validation & Testing](#validation--testing)
6. [Troubleshooting](#troubleshooting)

---

## UI Method (Settings Page)

### Accessing Sources Settings

1. Navigate to: `/app/settings`
2. Click **"Sources"** in the left sidebar
3. View current sources and add/edit/remove sources

### Adding Reddit Subreddits

**Step 1**: Click "Add Reddit Subreddit" button

**Step 2**: Fill in the form:
- **Subreddit Name**: Enter subreddit name (without `/r/` prefix)
  - Example: `MachineLearning`, `webdev`, `startups`
- **Sort Method**: Choose from:
  - `hot` (default) - Trending posts
  - `new` - Latest posts
  - `top` - Top-rated posts
  - `rising` - Emerging posts
- **Item Limit**: Number of posts to fetch (default: 25)
- **Time Filter**: For `top` sort only
  - `day`, `week`, `month`, `year`, `all`

**Step 3**: Click "Save"

**Result**: Subreddit added to workspace config, will be scraped on next scrape job.

**Screenshot Example**:
```
┌───────────────────────────────────────────────┐
│ Add Reddit Subreddit                          │
├───────────────────────────────────────────────┤
│ Subreddit Name: [MachineLearning           ] │
│ Sort Method:    [hot ▼]                      │
│ Item Limit:     [25                        ] │
│ Time Filter:    [all ▼]                      │
│                                               │
│ [Cancel]  [Save]                             │
└───────────────────────────────────────────────┘
```

---

### Adding YouTube Channels

**Step 1**: Click "Add YouTube Channel" button

**Step 2**: Choose input method:
- **Channel ID** (recommended): `UCbfYPyITQ-7l4upoX8nvctg`
- **Channel Username**: `@GoogleDevelopers`
- **Search Query**: "AI tutorials"

**Step 3**: Configure settings:
- **Max Results**: Number of videos to fetch (default: 10)
- **Order By**: `date` (latest) or `relevance` (most relevant)

**Step 4**: Click "Save"

**Finding Channel IDs**:
1. Go to YouTube channel page
2. View page source (right-click → View Page Source)
3. Search for `"channelId":"UC..."`
4. Copy the 24-character ID starting with "UC"

**Alternative**: Use browser extension "YouTube Channel ID Finder"

---

### Adding RSS Feeds

**Step 1**: Click "Add RSS Feed" button

**Step 2**: Enter feed URL:
- Must be a valid RSS/Atom feed URL
- Example: `https://blog.openai.com/rss/`

**Step 3**: Test feed (optional):
- Click "Test Feed" to verify URL is accessible
- View sample items

**Step 4**: Click "Save"

**Finding RSS Feeds**:
- Look for RSS icon (📡) on blog homepages
- Try common URLs:
  - `/rss/`, `/feed/`, `/atom.xml`, `/rss.xml`
- Use RSS feed finder tools: https://rss.app/

---

### Adding Blog Scrapers

**Step 1**: Click "Add Blog Source" button

**Step 2**: Enter blog URL:
- Example: `https://www.fast.ai/posts/`

**Step 3**: Configure CSS selectors (advanced):
- **Article Container**: CSS selector for article wrapper
  - Example: `article`, `div.post`
- **Title Selector**: CSS selector for article title
  - Example: `h1.post-title`, `h2.entry-title`
- **Content Selector**: CSS selector for article body
  - Example: `div.post-content`, `article.entry-content`
- **Author Selector** (optional): CSS selector for author name
  - Example: `span.author`, `a.author-link`
- **Date Selector** (optional): CSS selector for publish date
  - Example: `time`, `span.post-date`

**Step 4**: Test scraper (recommended):
- Click "Test Scraper" to verify selectors work
- View extracted sample article

**Step 5**: Click "Save"

**Finding CSS Selectors**:
1. Open blog post in browser
2. Right-click on element (title, content, etc.) → Inspect
3. Find the CSS selector in DevTools:
   - Right-click element in inspector → Copy → Copy Selector
4. Simplify selector if needed (remove overly specific classes)

---

### Editing Sources

**Step 1**: Find source in sources list

**Step 2**: Click "Edit" button (pencil icon)

**Step 3**: Modify settings in modal

**Step 4**: Click "Save"

**Note**: Changes apply to next scrape job, not retroactively.

---

### Removing Sources

**Step 1**: Find source in sources list

**Step 2**: Click "Delete" button (trash icon)

**Step 3**: Confirm deletion in modal

**Result**: Source removed from workspace config, will not be scraped in future jobs.

**Important**: Existing content items from this source are NOT deleted (they remain in `content_items` table).

---

### Enabling/Disabling Sources

**Toggle Switch**: Click the toggle switch next to each source to enable/disable without deleting.

**Use Case**: Temporarily disable sources during testing or when hitting API rate limits.

---

## API Method (Programmatic)

### Authentication

All API requests require authentication:

```bash
# Get access token (login)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

# Use token in subsequent requests
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Get Current Workspace Config

```bash
curl -X GET http://localhost:8000/api/v1/workspaces/{workspace_id}/config \
  -H "Authorization: Bearer $TOKEN"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "config-uuid",
    "workspace_id": "workspace-uuid",
    "config": {
      "sources": [
        {
          "type": "reddit",
          "enabled": true,
          "config": {
            "subreddits": ["MachineLearning", "artificial"],
            "sort": "hot",
            "limit": 25
          }
        },
        {
          "type": "youtube",
          "enabled": true,
          "config": {
            "channel_ids": ["UC_x5XG1OV2P6uZZ5FSM9Ttw"],
            "max_results": 10
          }
        }
      ],
      "generation": {
        "model": "openai",
        "openai_model": "gpt-4-turbo-preview",
        "temperature": 0.7,
        "tone": "professional",
        "max_items": 10
      },
      "delivery": {
        "method": "smtp",
        "from_name": "CreatorPulse"
      }
    },
    "version": 1,
    "created_at": "2025-01-24T10:00:00Z",
    "updated_at": "2025-01-24T12:00:00Z"
  }
}
```

---

### Update Workspace Config (Add Sources)

**Method**: `PUT /api/v1/workspaces/{workspace_id}/config`

**Example 1: Add Reddit Subreddits**

```bash
curl -X PUT http://localhost:8000/api/v1/workspaces/{workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "sources": [
        {
          "type": "reddit",
          "enabled": true,
          "config": {
            "subreddits": [
              "MachineLearning",
              "LocalLLaMA",
              "OpenAI",
              "LangChain",
              "programming"
            ],
            "sort": "hot",
            "limit": 25
          }
        }
      ]
    }
  }'
```

**Example 2: Add YouTube Channels**

```bash
curl -X PUT http://localhost:8000/api/v1/workspaces/{workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "sources": [
        {
          "type": "youtube",
          "enabled": true,
          "config": {
            "channel_ids": [
              "UCbfYPyITQ-7l4upoX8nvctg",
              "UCYO_jab_esuFRV4b17AJtAw",
              "UC295-Dw_tDNtZXFeAPAW6Aw"
            ],
            "max_results": 10
          }
        }
      ]
    }
  }'
```

**Example 3: Add RSS Feeds**

```bash
curl -X PUT http://localhost:8000/api/v1/workspaces/{workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "sources": [
        {
          "type": "rss",
          "enabled": true,
          "config": {
            "feed_urls": [
              "https://openai.com/blog/rss/",
              "https://blog.google/technology/ai/rss/",
              "https://huggingface.co/blog/feed.xml"
            ]
          }
        }
      ]
    }
  }'
```

**Example 4: Add Blog Scraper**

```bash
curl -X PUT http://localhost:8000/api/v1/workspaces/{workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "sources": [
        {
          "type": "blog",
          "enabled": true,
          "config": {
            "url": "https://www.fast.ai/posts/",
            "selectors": {
              "article": "article",
              "title": "h1.post-title",
              "content": "div.post-content",
              "author": "span.author-name",
              "date": "time"
            }
          }
        }
      ]
    }
  }'
```

**Example 5: Add Multiple Sources at Once**

```bash
curl -X PUT http://localhost:8000/api/v1/workspaces/{workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "sources": [
        {
          "type": "reddit",
          "enabled": true,
          "config": {
            "subreddits": ["MachineLearning", "LocalLLaMA"],
            "sort": "hot",
            "limit": 25
          }
        },
        {
          "type": "youtube",
          "enabled": true,
          "config": {
            "channel_ids": ["UCbfYPyITQ-7l4upoX8nvctg"],
            "max_results": 10
          }
        },
        {
          "type": "rss",
          "enabled": true,
          "config": {
            "feed_urls": ["https://openai.com/blog/rss/"]
          }
        }
      ],
      "generation": {
        "model": "openai",
        "openai_model": "gpt-4-turbo-preview",
        "temperature": 0.7,
        "tone": "professional",
        "max_items": 10
      },
      "delivery": {
        "method": "smtp",
        "from_name": "CreatorPulse"
      }
    }
  }'
```

**Important**: `PUT` replaces the entire config. To add sources without losing existing ones:
1. First `GET` current config
2. Add new sources to `sources` array
3. `PUT` updated config

---

### Trigger Manual Scrape

After updating sources, trigger a scrape to test:

```bash
curl -X POST http://localhost:8000/api/v1/content/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": "workspace-uuid"}'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "message": "Content scraped successfully",
    "items_count": 87,
    "sources_scraped": ["reddit", "youtube", "rss"],
    "items": [
      {
        "id": "item-uuid",
        "title": "GPT-5 Release Announcement",
        "source": "reddit",
        "score": 1250,
        "created_at": "2025-01-24T12:00:00Z"
      }
    ]
  }
}
```

---

## Workspace Configuration Structure

### Full Schema

```typescript
interface WorkspaceConfig {
  sources: SourceConfig[]
  generation: GenerationConfig
  delivery: DeliveryConfig
}

interface SourceConfig {
  type: 'reddit' | 'youtube' | 'rss' | 'blog' | 'x'
  enabled: boolean
  config: RedditConfig | YouTubeConfig | RSSConfig | BlogConfig | XConfig
}

// Reddit
interface RedditConfig {
  subreddits: string[]           // ["MachineLearning", "artificial"]
  sort?: 'hot' | 'new' | 'top' | 'rising'  // default: 'hot'
  limit?: number                 // default: 25
  time_filter?: 'day' | 'week' | 'month' | 'year' | 'all'  // for 'top' sort only
}

// YouTube
interface YouTubeConfig {
  channel_ids?: string[]         // ["UC_x5XG1OV2P6uZZ5FSM9Ttw"]
  channel_usernames?: string[]   // ["GoogleDevelopers"]
  search_queries?: string[]      // ["AI tutorials"]
  max_results?: number           // default: 10
  order?: 'date' | 'relevance'   // default: 'date'
}

// RSS
interface RSSConfig {
  feed_urls: string[]            // ["https://blog.openai.com/rss/"]
}

// Blog
interface BlogConfig {
  url: string                    // "https://www.fast.ai/posts/"
  selectors: {
    article: string              // "article"
    title: string                // "h1.post-title"
    content: string              // "div.post-content"
    author?: string              // "span.author-name"
    date?: string                // "time"
  }
}

// X/Twitter
interface XConfig {
  usernames?: string[]           // ["@elonmusk"]
  search_query?: string          // "#AI"
  max_results?: number           // default: 10
}

// Generation settings
interface GenerationConfig {
  model: 'openai' | 'openrouter'
  openai_model?: string          // "gpt-4-turbo-preview"
  openrouter_model?: string      // "anthropic/claude-3.5-sonnet"
  temperature: number            // 0.0-1.0, default: 0.7
  tone: string                   // "professional" | "casual" | "technical" | "friendly"
  language: string               // "en"
  max_items: number              // default: 10
}

// Delivery settings
interface DeliveryConfig {
  method: 'smtp' | 'sendgrid'
  from_name: string              // "CreatorPulse"
  reply_to?: string              // "support@example.com"
}
```

---

## Common Operations

### Operation 1: Add 10 New Subreddits

```bash
# Step 1: Get current config
curl -X GET http://localhost:8000/api/v1/workspaces/{workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" > current_config.json

# Step 2: Edit current_config.json to add subreddits to sources[0].config.subreddits array

# Step 3: Update config
curl -X PUT http://localhost:8000/api/v1/workspaces/{workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @current_config.json

# Step 4: Trigger scrape
curl -X POST http://localhost:8000/api/v1/content/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": "workspace-uuid"}'
```

---

### Operation 2: Disable All YouTube Sources

```bash
# Update config with enabled: false
curl -X PUT http://localhost:8000/api/v1/workspaces/{workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "sources": [
        {
          "type": "youtube",
          "enabled": false,
          "config": {
            "channel_ids": ["UC_x5XG1OV2P6uZZ5FSM9Ttw"]
          }
        }
      ]
    }
  }'
```

---

### Operation 3: Copy Sources from Another Workspace

```bash
# Step 1: Get config from source workspace
curl -X GET http://localhost:8000/api/v1/workspaces/{source_workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" > source_config.json

# Step 2: Extract sources array from source_config.json

# Step 3: Get config from target workspace
curl -X GET http://localhost:8000/api/v1/workspaces/{target_workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" > target_config.json

# Step 4: Merge sources arrays in target_config.json

# Step 5: Update target workspace
curl -X PUT http://localhost:8000/api/v1/workspaces/{target_workspace_id}/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @target_config.json
```

---

## Validation & Testing

### Validate Config Structure

**Backend automatically validates**:
- Required fields present (`type`, `enabled`, `config`)
- Valid enum values (`type` must be one of: `reddit`, `youtube`, `rss`, `blog`, `x`)
- Correct config structure for each source type

**Validation Errors**:
```json
{
  "success": false,
  "error": "Invalid config structure: missing 'subreddits' in reddit config"
}
```

---

### Test Individual Source

**Method 1: UI Test**
1. Add source in Settings → Sources
2. Click "Test Source" button
3. View sample items fetched

**Method 2: Manual Scrape with Single Source**
1. Create temporary workspace with only one source
2. Trigger scrape
3. View logs and content items

**Method 3: Check Backend Logs**
```bash
# Tail backend logs
tail -f backend/logs/app.log

# Look for scraper output
# [Reddit] Fetched 25 posts from r/MachineLearning
# [YouTube] Fetched 10 videos from channel UC_x5XG1OV2P6uZZ5FSM9Ttw
```

---

### Verify Content Items

After scraping, verify items were added:

```bash
curl -X GET "http://localhost:8000/api/v1/content/workspaces/{workspace_id}?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Check**:
- Items from new sources appear
- `source` field matches source type (`reddit`, `youtube`, `rss`, `blog`)
- `source_url` is unique (no duplicates)

---

## Troubleshooting

### Issue 1: No Items Scraped from Source

**Symptoms**: Scrape completes but 0 items from specific source

**Debug Steps**:
1. Check if source is enabled: `sources[i].enabled === true`
2. Verify API keys are set (YouTube: `YOUTUBE_API_KEY`, X: `X_BEARER_TOKEN`)
3. Check backend logs for errors:
   ```bash
   tail -f backend/logs/app.log | grep ERROR
   ```
4. Test source manually (e.g., visit Reddit subreddit, RSS feed URL in browser)

**Common Causes**:
- Invalid subreddit name (subreddit doesn't exist or is private)
- Invalid YouTube channel ID (wrong format or channel deleted)
- RSS feed URL returns 404 (broken link)
- API rate limit exceeded (YouTube, X)

---

### Issue 2: High Duplicate Rate

**Symptoms**: Scraping returns 90%+ duplicates

**Cause**: Scraping too frequently (see [RECOMMENDED_CONTENT_SOURCES.md](../RECOMMENDED_CONTENT_SOURCES.md))

**Fix**: Adjust scraping schedule:
- Reddit: Every 6 hours (not every 15-30 min)
- YouTube: Once daily (not multiple times per day)
- RSS/Blogs: Once weekly (not daily)

---

### Issue 3: CSS Selectors Not Working (Blog Scraper)

**Symptoms**: Blog scraper returns 0 items or extracts wrong content

**Debug Steps**:
1. Open blog URL in browser
2. Right-click on article element → Inspect
3. Verify CSS selector matches element:
   ```javascript
   // In browser console
   document.querySelectorAll('article')  // Should return article elements
   document.querySelector('h1.post-title')  // Should return title element
   ```
4. Update selectors if blog structure changed

**Common Issues**:
- Blog redesigned, selectors outdated
- JavaScript-rendered content (use headless browser scraper instead)
- Selectors too specific (e.g., `div.post-123` instead of `div.post`)

---

### Issue 4: API Rate Limit Errors

**Symptoms**: YouTube/X scraper returns 429 errors

**Cause**: Exceeded API quota

**Fix**:
- **YouTube**: Reduce scraping frequency, use fewer channels, or add multiple API keys
- **X**: Reduce scraping frequency or upgrade API plan (X free tier is very limited)

---

### Issue 5: Config Update Doesn't Apply

**Symptoms**: Updated config but scraper still uses old sources

**Cause**: Backend cached old config

**Fix**:
1. Restart backend server:
   ```bash
   # In terminal running uvicorn
   Ctrl+C
   .venv/Scripts/python.exe -m uvicorn backend.main:app --reload
   ```
2. Or wait for auto-reload (if `--reload` flag is enabled)

---

## Additional Resources

- **Recommended Sources**: [RECOMMENDED_CONTENT_SOURCES.md](../RECOMMENDED_CONTENT_SOURCES.md)
- **Quick Add Guide**: [QUICK_ADD_SOURCES.md](./QUICK_ADD_SOURCES.md)
- **API Reference**: [API_REFERENCE.md](../_PRIORITY_2_REFERENCE/API_REFERENCE.md)
- **Database Schema**: [DATABASE_SCHEMA.md](../_PRIORITY_2_REFERENCE/DATABASE_SCHEMA.md)

---

**Questions?** Open an issue on GitHub or contact support.
