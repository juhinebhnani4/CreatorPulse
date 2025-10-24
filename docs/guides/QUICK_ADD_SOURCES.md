# Quick Add Sources - Copy-Paste Ready Configs

## Overview

This guide provides copy-paste ready JSON configurations for quickly adding 50+ curated content sources to your workspace. Perfect for getting started or expanding your content library.

**Last Updated**: 2025-01-24
**Related Docs**: [RECOMMENDED_CONTENT_SOURCES.md](../RECOMMENDED_CONTENT_SOURCES.md), [MANAGING_CONTENT_SOURCES.md](./MANAGING_CONTENT_SOURCES.md)

---

## Quick Start

### Method 1: API (Fastest)

```bash
# 1. Set your auth token
export TOKEN="your-jwt-token-here"
export WORKSPACE_ID="your-workspace-id"

# 2. Copy one of the configs below
# 3. Save to file (e.g., sources_config.json)
# 4. Run:
curl -X PUT http://localhost:8000/api/v1/workspaces/$WORKSPACE_ID/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @sources_config.json
```

### Method 2: UI (Visual)

1. Navigate to: `/app/settings` → **Sources**
2. Copy JSON config from sections below
3. Click "Import JSON" button
4. Paste JSON
5. Click "Save"

---

## Pre-Built Configurations

### Config 1: AI/ML Starter Pack (15 sources)

**Best for**: AI newsletters, ML research updates, GPT news

**Sources**: 5 Reddit subs + 5 YouTube channels + 5 RSS feeds

```json
{
  "sources": [
    {
      "type": "reddit",
      "enabled": true,
      "config": {
        "subreddits": [
          "MachineLearning",
          "artificial",
          "LocalLLaMA",
          "OpenAI",
          "LangChain"
        ],
        "sort": "hot",
        "limit": 25
      }
    },
    {
      "type": "youtube",
      "enabled": true,
      "config": {
        "channel_ids": [
          "UCbfYPyITQ-7l4upoX8nvctg",
          "UCYO_jab_esuFRV4b17AJtAw",
          "UC295-Dw_tDNtZXFeAPAW6Aw",
          "UCXZCJLdBC09xxGZ6gcdrc6A",
          "UCJ0-OtVpF0wOKEqT2Z1HEtA"
        ],
        "max_results": 10,
        "order": "date"
      }
    },
    {
      "type": "rss",
      "enabled": true,
      "config": {
        "feed_urls": [
          "https://openai.com/blog/rss/",
          "https://blog.google/technology/ai/rss/",
          "https://www.anthropic.com/news/rss",
          "https://huggingface.co/blog/feed.xml",
          "https://www.deepmind.com/blog/rss.xml"
        ]
      }
    }
  ],
  "generation": {
    "model": "openai",
    "openai_model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "tone": "professional",
    "language": "en",
    "max_items": 10
  },
  "delivery": {
    "method": "smtp",
    "from_name": "AI Weekly"
  }
}
```

**Expected Output**:
- 125 Reddit posts/day (25 posts × 5 subs)
- 10 YouTube videos/day
- 5-10 RSS articles/week

**Scraping Schedule**:
- Reddit: Every 6 hours
- YouTube: Once daily
- RSS: Once weekly

---

### Config 2: Web Development Pro (20 sources)

**Best for**: Web dev newsletters, framework updates, coding tutorials

**Sources**: 7 Reddit subs + 8 YouTube channels + 5 RSS feeds

```json
{
  "sources": [
    {
      "type": "reddit",
      "enabled": true,
      "config": {
        "subreddits": [
          "programming",
          "webdev",
          "reactjs",
          "nextjs",
          "javascript",
          "Python",
          "docker"
        ],
        "sort": "hot",
        "limit": 25
      }
    },
    {
      "type": "youtube",
      "enabled": true,
      "config": {
        "channel_ids": [
          "UC_x5XG1OV2P6uZZ5FSM9Ttw",
          "UCsBjURrPoezykLs9EqgamOA",
          "UCCezIgC97PvUuR4_gbFUs5g",
          "UCsooa4yRKGN_zEE8iknghZA",
          "UCXZCJLdBC09xxGZ6gcdrc6A",
          "UCJ0-OtVpF0wOKEqT2Z1HEtA",
          "UCbfYPyITQ-7l4upoX8nvctg",
          "UC295-Dw_tDNtZXFeAPAW6Aw"
        ],
        "max_results": 10,
        "order": "date"
      }
    },
    {
      "type": "rss",
      "enabled": true,
      "config": {
        "feed_urls": [
          "https://techcrunch.com/feed/",
          "https://www.theverge.com/rss/index.xml",
          "https://arstechnica.com/feed/",
          "https://news.ycombinator.com/rss",
          "https://www.wired.com/feed/rss"
        ]
      }
    }
  ],
  "generation": {
    "model": "openai",
    "openai_model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "tone": "casual",
    "language": "en",
    "max_items": 12
  },
  "delivery": {
    "method": "smtp",
    "from_name": "Dev Weekly"
  }
}
```

**Expected Output**:
- 175 Reddit posts/day
- 10 YouTube videos/day
- 50-100 RSS articles/day (filter by engagement)

---

### Config 3: Startup/Business Growth (15 sources)

**Best for**: Entrepreneur newsletters, startup funding news, growth strategies

**Sources**: 4 Reddit subs + 6 YouTube channels + 5 RSS feeds

```json
{
  "sources": [
    {
      "type": "reddit",
      "enabled": true,
      "config": {
        "subreddits": [
          "Entrepreneur",
          "startups",
          "SaaS",
          "productivity"
        ],
        "sort": "hot",
        "limit": 25
      }
    },
    {
      "type": "youtube",
      "enabled": true,
      "config": {
        "channel_ids": [
          "UC2D2CMWXMOVWx7giW1n3LIg",
          "UCfzlCWGWYyIQ0aLC5w48gBQ",
          "UC7cs8q-gJRlGwj4A8OmCmXg",
          "UCJbPGzawDH1njbqV-D5HqKw",
          "UC1fLEeYICmo3O9cUsqIi7HA",
          "UCsBjURrPoezykLs9EqgamOA"
        ],
        "max_results": 10,
        "order": "date"
      }
    },
    {
      "type": "rss",
      "enabled": true,
      "config": {
        "feed_urls": [
          "https://techcrunch.com/feed/",
          "https://www.theverge.com/rss/index.xml",
          "https://arstechnica.com/feed/",
          "https://news.ycombinator.com/rss",
          "https://www.wired.com/feed/rss"
        ]
      }
    }
  ],
  "generation": {
    "model": "openai",
    "openai_model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "tone": "friendly",
    "language": "en",
    "max_items": 10
  },
  "delivery": {
    "method": "smtp",
    "from_name": "Startup Weekly"
  }
}
```

---

### Config 4: General Tech News (25 sources)

**Best for**: Broad tech newsletters, consumer tech, industry news

**Sources**: 10 Reddit subs + 10 YouTube channels + 5 RSS feeds

```json
{
  "sources": [
    {
      "type": "reddit",
      "enabled": true,
      "config": {
        "subreddits": [
          "technology",
          "gadgets",
          "Futurology",
          "MachineLearning",
          "programming",
          "webdev",
          "startups",
          "SaaS",
          "cryptocurrency",
          "science"
        ],
        "sort": "hot",
        "limit": 25
      }
    },
    {
      "type": "youtube",
      "enabled": true,
      "config": {
        "channel_ids": [
          "UCbfYPyITQ-7l4upoX8nvctg",
          "UCYO_jab_esuFRV4b17AJtAw",
          "UC295-Dw_tDNtZXFeAPAW6Aw",
          "UCXZCJLdBC09xxGZ6gcdrc6A",
          "UC_x5XG1OV2P6uZZ5FSM9Ttw",
          "UCsBjURrPoezykLs9EqgamOA",
          "UCCezIgC97PvUuR4_gbFUs5g",
          "UCsooa4yRKGN_zEE8iknghZA",
          "UC2D2CMWXMOVWx7giW1n3LIg",
          "UC7cs8q-gJRlGwj4A8OmCmXg"
        ],
        "max_results": 10,
        "order": "date"
      }
    },
    {
      "type": "rss",
      "enabled": true,
      "config": {
        "feed_urls": [
          "https://techcrunch.com/feed/",
          "https://www.theverge.com/rss/index.xml",
          "https://arstechnica.com/feed/",
          "https://news.ycombinator.com/rss",
          "https://www.wired.com/feed/rss"
        ]
      }
    }
  ],
  "generation": {
    "model": "openai",
    "openai_model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "tone": "professional",
    "language": "en",
    "max_items": 15
  },
  "delivery": {
    "method": "smtp",
    "from_name": "Tech Digest"
  }
}
```

**Expected Output**:
- 250 Reddit posts/day
- 10 YouTube videos/day
- 50-100 RSS articles/day

---

### Config 5: Maximum Diversity (50+ sources)

**Best for**: Large newsletters, comprehensive industry coverage, daily digests

**Sources**: 20 Reddit subs + 15 YouTube channels + 10 RSS feeds + 5 blogs

```json
{
  "sources": [
    {
      "type": "reddit",
      "enabled": true,
      "config": {
        "subreddits": [
          "MachineLearning",
          "artificial",
          "LocalLLaMA",
          "OpenAI",
          "StableDiffusion",
          "LangChain",
          "programming",
          "webdev",
          "Python",
          "javascript",
          "reactjs",
          "nextjs",
          "docker",
          "Entrepreneur",
          "startups",
          "SaaS",
          "productivity",
          "technology",
          "gadgets",
          "Futurology"
        ],
        "sort": "hot",
        "limit": 25
      }
    },
    {
      "type": "youtube",
      "enabled": true,
      "config": {
        "channel_ids": [
          "UCbfYPyITQ-7l4upoX8nvctg",
          "UCYO_jab_esuFRV4b17AJtAw",
          "UC295-Dw_tDNtZXFeAPAW6Aw",
          "UCXZCJLdBC09xxGZ6gcdrc6A",
          "UCJ0-OtVpF0wOKEqT2Z1HEtA",
          "UC_x5XG1OV2P6uZZ5FSM9Ttw",
          "UCsBjURrPoezykLs9EqgamOA",
          "UCCezIgC97PvUuR4_gbFUs5g",
          "UCsooa4yRKGN_zEE8iknghZA",
          "UCzL_0nIe8B4-7ShhVPfJkgw",
          "UC2D2CMWXMOVWx7giW1n3LIg",
          "UCfzlCWGWYyIQ0aLC5w48gBQ",
          "UC7cs8q-gJRlGwj4A8OmCmXg",
          "UCJbPGzawDH1njbqV-D5HqKw",
          "UC1fLEeYICmo3O9cUsqIi7HA"
        ],
        "max_results": 10,
        "order": "date"
      }
    },
    {
      "type": "rss",
      "enabled": true,
      "config": {
        "feed_urls": [
          "https://openai.com/blog/rss/",
          "https://blog.google/technology/ai/rss/",
          "https://www.anthropic.com/news/rss",
          "https://huggingface.co/blog/feed.xml",
          "https://www.deepmind.com/blog/rss.xml",
          "https://techcrunch.com/feed/",
          "https://www.theverge.com/rss/index.xml",
          "https://arstechnica.com/feed/",
          "https://news.ycombinator.com/rss",
          "https://www.wired.com/feed/rss"
        ]
      }
    }
  ],
  "generation": {
    "model": "openai",
    "openai_model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "tone": "professional",
    "language": "en",
    "max_items": 20
  },
  "delivery": {
    "method": "smtp",
    "from_name": "Tech Pulse Daily"
  }
}
```

**Expected Output**:
- 500 Reddit posts/day
- 15 YouTube videos/day
- 50-100 RSS articles/day

**⚠️ Warning**: This config generates high volume. Use aggressive filtering (score > 100, recency boost) to avoid content overload.

---

## Individual Source Snippets

### Reddit Subreddits

#### AI & Machine Learning (Copy-Paste Ready)

```json
{
  "type": "reddit",
  "enabled": true,
  "config": {
    "subreddits": [
      "MachineLearning",
      "artificial",
      "LocalLLaMA",
      "OpenAI",
      "StableDiffusion",
      "LangChain"
    ],
    "sort": "hot",
    "limit": 25
  }
}
```

#### Web Development

```json
{
  "type": "reddit",
  "enabled": true,
  "config": {
    "subreddits": [
      "programming",
      "webdev",
      "Python",
      "javascript",
      "reactjs",
      "nextjs",
      "docker"
    ],
    "sort": "hot",
    "limit": 25
  }
}
```

#### Business & Startups

```json
{
  "type": "reddit",
  "enabled": true,
  "config": {
    "subreddits": [
      "Entrepreneur",
      "startups",
      "SaaS",
      "productivity"
    ],
    "sort": "hot",
    "limit": 25
  }
}
```

#### General Tech News

```json
{
  "type": "reddit",
  "enabled": true,
  "config": {
    "subreddits": [
      "technology",
      "gadgets",
      "Futurology"
    ],
    "sort": "hot",
    "limit": 25
  }
}
```

---

### YouTube Channels

#### AI & Tech Creators

```json
{
  "type": "youtube",
  "enabled": true,
  "config": {
    "channel_ids": [
      "UCbfYPyITQ-7l4upoX8nvctg",
      "UCYO_jab_esuFRV4b17AJtAw",
      "UC295-Dw_tDNtZXFeAPAW6Aw",
      "UCXZCJLdBC09xxGZ6gcdrc6A",
      "UCJ0-OtVpF0wOKEqT2Z1HEtA",
      "UC_x5XG1OV2P6uZZ5FSM9Ttw",
      "UCsBjURrPoezykLs9EqgamOA",
      "UCCezIgC97PvUuR4_gbFUs5g",
      "UCsooa4yRKGN_zEE8iknghZA",
      "UCzL_0nIe8B4-7ShhVPfJkgw"
    ],
    "max_results": 10,
    "order": "date"
  }
}
```

**Channels Included**:
1. Two Minute Papers (AI Research)
2. 3Blue1Brown (Math/AI Explainers)
3. Siraj Raval (AI Projects)
4. Sentdex (Python/ML)
5. CodeEmporium (Deep Learning)
6. Google for Developers (Google Tech)
7. Fireship (Web Dev)
8. Corey Schafer (Python)
9. TechWorld with Nana (DevOps)
10. Cursor (AI Coding Tools)

---

#### Business & Productivity

```json
{
  "type": "youtube",
  "enabled": true,
  "config": {
    "channel_ids": [
      "UC2D2CMWXMOVWx7giW1n3LIg",
      "UCfzlCWGWYyIQ0aLC5w48gBQ",
      "UC7cs8q-gJRlGwj4A8OmCmXg",
      "UCJbPGzawDH1njbqV-D5HqKw",
      "UC1fLEeYICmo3O9cUsqIi7HA"
    ],
    "max_results": 10,
    "order": "date"
  }
}
```

**Channels Included**:
1. Y Combinator (Startups)
2. Techstars (Startup Advice)
3. Ali Abdaal (Productivity)
4. The Futur (Creative Business)
5. Matt D'Avella (Minimalism/Productivity)

---

### RSS Feeds

#### AI Research & Industry

```json
{
  "type": "rss",
  "enabled": true,
  "config": {
    "feed_urls": [
      "https://openai.com/blog/rss/",
      "https://blog.google/technology/ai/rss/",
      "https://www.anthropic.com/news/rss",
      "https://huggingface.co/blog/feed.xml",
      "https://www.deepmind.com/blog/rss.xml"
    ]
  }
}
```

---

#### Tech News & Analysis

```json
{
  "type": "rss",
  "enabled": true,
  "config": {
    "feed_urls": [
      "https://techcrunch.com/feed/",
      "https://www.theverge.com/rss/index.xml",
      "https://arstechnica.com/feed/",
      "https://news.ycombinator.com/rss",
      "https://www.wired.com/feed/rss"
    ]
  }
}
```

---

## Usage Instructions

### Step-by-Step (API Method)

**1. Get Your Auth Token**

```bash
# Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "yourpassword"}'

# Copy access_token from response
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**2. Get Your Workspace ID**

```bash
# List workspaces
curl -X GET http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer $TOKEN"

# Copy workspace id from response
export WORKSPACE_ID="workspace-uuid-here"
```

**3. Choose a Config**

Copy one of the configs above (Config 1-5 or individual snippets).

**4. Save to File**

```bash
# Save config to file
cat > sources_config.json << 'EOF'
{
  "sources": [
    ...your config here...
  ],
  "generation": {...},
  "delivery": {...}
}
EOF
```

**5. Update Workspace**

```bash
curl -X PUT http://localhost:8000/api/v1/workspaces/$WORKSPACE_ID/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @sources_config.json
```

**6. Trigger Scrape**

```bash
curl -X POST http://localhost:8000/api/v1/content/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"workspace_id\": \"$WORKSPACE_ID\"}"
```

**7. Verify Content**

```bash
curl -X GET "http://localhost:8000/api/v1/content/workspaces/$WORKSPACE_ID?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Customization Tips

### Adjust Tone

Change `generation.tone` to match your audience:
- `"professional"` - Formal, business-focused
- `"casual"` - Friendly, conversational
- `"technical"` - Developer-focused, detailed
- `"friendly"` - Warm, approachable

### Adjust Content Volume

Change `generation.max_items` to control newsletter length:
- `5-7` items: Quick digest (2-3 min read)
- `10-12` items: Standard newsletter (5-7 min read)
- `15-20` items: Comprehensive weekly (10-15 min read)

### Filter by Quality

Adjust Reddit `limit` and YouTube `max_results`:
- **High volume**: `limit: 50`, `max_results: 20`
- **Quality over quantity**: `limit: 10`, `max_results: 5`

Then use recency boost + score filtering to select best items.

---

## Troubleshooting

### Issue: Config Update Returns 400 Error

**Cause**: Invalid JSON syntax or missing required fields

**Fix**:
1. Validate JSON syntax: https://jsonlint.com/
2. Ensure `sources`, `generation`, `delivery` keys present
3. Verify `type` field is one of: `reddit`, `youtube`, `rss`, `blog`, `x`

---

### Issue: No Items Scraped After Adding Sources

**Cause**: Sources disabled or API keys missing

**Fix**:
1. Verify `"enabled": true` for each source
2. Check API keys in backend `.env`:
   - YouTube: `YOUTUBE_API_KEY`
   - X: `X_BEARER_TOKEN`
3. Check backend logs: `tail -f backend/logs/app.log`

---

### Issue: High Duplicate Rate

**Cause**: Scraping too frequently

**Fix**: See [RECOMMENDED_CONTENT_SOURCES.md](../RECOMMENDED_CONTENT_SOURCES.md) for scraping schedule recommendations.

---

## Additional Resources

- **Full Source List**: [RECOMMENDED_CONTENT_SOURCES.md](../RECOMMENDED_CONTENT_SOURCES.md)
- **Detailed Guide**: [MANAGING_CONTENT_SOURCES.md](./MANAGING_CONTENT_SOURCES.md)
- **API Reference**: [API_REFERENCE.md](../_PRIORITY_2_REFERENCE/API_REFERENCE.md)

---

**Questions?** Open an issue on GitHub or contact support.
