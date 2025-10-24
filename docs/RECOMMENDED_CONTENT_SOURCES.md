# Recommended Content Sources

## Overview

This guide provides 50+ curated content sources optimized for AI newsletter generation, organized by update frequency and content quality. Each source includes ready-to-use JSON configuration and rationale.

**Last Updated**: 2025-01-24

---

## Quick Start

Copy-paste these sources into your workspace configuration via:
- **UI**: Settings → Sources → Add Source
- **API**: `PUT /api/v1/workspaces/{id}/config`

---

## Tier 1: High-Frequency Sources (Updates Every 1-6 Hours)

**Best for**: Breaking news, trending topics, daily newsletters

### Reddit Subreddits (20 sources)

#### AI & Machine Learning (6 sources)

```json
{
  "reddit": {
    "enabled": true,
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

**Rationale**:
- `MachineLearning`: 3M+ members, academic + industry mix, research papers and discussions
- `artificial`: 2M+ members, general AI news, beginner-friendly
- `LocalLLaMA`: 200K+ members, open-source LLMs, cutting-edge local AI
- `OpenAI`: 500K+ members, GPT news, API updates, ChatGPT discussions
- `StableDiffusion`: 400K+ members, generative art, model releases
- `LangChain`: 50K+ members, AI application development, framework updates

**Update Frequency**: Every 1-3 hours (hot posts refresh)

---

#### Tech & Programming (7 sources)

```json
{
  "reddit": {
    "enabled": true,
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

**Rationale**:
- `programming`: 6M+ members, general programming discussions, career advice
- `webdev`: 2M+ members, web development trends, best practices
- `Python`: 1.5M+ members, Python tutorials, library updates
- `javascript`: 3M+ members, JS ecosystem news, framework comparisons
- `reactjs`: 700K+ members, React patterns, component libraries
- `nextjs`: 200K+ members, Next.js releases, deployment tips
- `docker`: 200K+ members, containerization, DevOps practices

**Update Frequency**: Every 2-4 hours

---

#### Business & Productivity (4 sources)

```json
{
  "reddit": {
    "enabled": true,
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

**Rationale**:
- `Entrepreneur`: 2M+ members, business strategies, growth stories
- `startups`: 1.5M+ members, startup launches, funding news, pivots
- `SaaS`: 200K+ members, software-as-a-service trends, SaaS metrics
- `productivity`: 3M+ members, productivity tools, workflows, time management

**Update Frequency**: Every 3-6 hours

---

#### General Tech News (3 sources)

```json
{
  "reddit": {
    "enabled": true,
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

**Rationale**:
- `technology`: 14M+ members, general tech news, policy discussions
- `gadgets`: 20M+ members, hardware reviews, product launches
- `Futurology`: 19M+ members, future tech, predictions, speculative discussions

**Update Frequency**: Every 1-2 hours (high traffic)

---

## Tier 2: Medium-Frequency Sources (Updates Daily)

**Best for**: Quality over quantity, weekly newsletters

### YouTube Channels (15 sources)

#### AI & Tech Creators (10 channels)

```json
{
  "youtube": {
    "enabled": true,
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
    "max_results": 10
  }
}
```

**Channel Details**:

| Channel ID | Channel Name | Focus | Subscribers | Post Frequency |
|-----------|--------------|-------|-------------|----------------|
| `UCbfYPyITQ-7l4upoX8nvctg` | Two Minute Papers | AI Research | 1.5M | 3x/week |
| `UCYO_jab_esuFRV4b17AJtAw` | 3Blue1Brown | Math/AI Explainers | 6M | 1x/month |
| `UC295-Dw_tDNtZXFeAPAW6Aw` | Siraj Raval | AI Projects | 800K | 2x/week |
| `UCXZCJLdBC09xxGZ6gcdrc6A` | Sentdex | Python/ML Tutorials | 1.2M | 2x/week |
| `UCJ0-OtVpF0wOKEqT2Z1HEtA` | CodeEmporium | Deep Learning | 200K | 1x/week |
| `UC_x5XG1OV2P6uZZ5FSM9Ttw` | Google for Developers | Google Tech | 1M | Daily |
| `UCsBjURrPoezykLs9EqgamOA` | Fireship | Web Dev (Short) | 3M | 2x/week |
| `UCCezIgC97PvUuR4_gbFUs5g` | Corey Schafer | Python Tutorials | 1.2M | 1x/week |
| `UCsooa4yRKGN_zEE8iknghZA` | TechWorld with Nana | DevOps | 1M | 1x/week |
| `UCzL_0nIe8B4-7ShhVPfJkgw` | Cursor | AI Coding Tools | 50K | 2x/week |

**Rationale**:
- High-quality, educational content
- Mix of quick updates (Fireship 5-10 min) and deep dives (3Blue1Brown 20-30 min)
- Strong community engagement (high like/comment ratios)
- Consistent upload schedules

**Update Frequency**: Daily aggregate (1-3 new videos/day across all channels)

---

#### Business & Productivity Channels (5 channels)

```json
{
  "youtube": {
    "enabled": true,
    "channel_ids": [
      "UC2D2CMWXMOVWx7giW1n3LIg",
      "UCfzlCWGWYyIQ0aLC5w48gBQ",
      "UC7cs8q-gJRlGwj4A8OmCmXg",
      "UCJbPGzawDH1njbqV-D5HqKw",
      "UC1fLEeYICmo3O9cUsqIi7HA"
    ],
    "max_results": 10
  }
}
```

**Channel Details**:

| Channel ID | Channel Name | Focus | Subscribers | Post Frequency |
|-----------|--------------|-------|-------------|----------------|
| `UC2D2CMWXMOVWx7giW1n3LIg` | Y Combinator | Startups | 1.5M | 3x/week |
| `UCfzlCWGWYyIQ0aLC5w48gBQ` | Techstars | Startup Advice | 100K | 2x/week |
| `UC7cs8q-gJRlGwj4A8OmCmXg` | Ali Abdaal | Productivity | 5M | 1x/week |
| `UCJbPGzawDH1njbqV-D5HqKw` | The Futur | Creative Business | 2M | 2x/week |
| `UC1fLEeYICmo3O9cUsqIi7HA` | Matt D'Avella | Minimalism/Productivity | 4M | 1x/week |

**Update Frequency**: Daily aggregate (2-3 new videos/day)

---

## Tier 3: Low-Frequency Sources (Updates Weekly/Monthly)

**Best for**: Evergreen content, monthly digests

### RSS Feeds (10 sources)

#### AI Research & Industry Blogs (5 feeds)

```json
{
  "rss": {
    "enabled": true,
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

**Rationale**:
- **OpenAI Blog**: GPT model releases, API updates, safety research (2-3 posts/month)
- **Google AI Blog**: Research breakthroughs, product launches (4-6 posts/month)
- **Anthropic News**: Claude updates, AI safety research (1-2 posts/month)
- **Hugging Face Blog**: Model releases, tutorials, community highlights (8-10 posts/month)
- **DeepMind Blog**: Academic research, AlphaFold updates (2-3 posts/month)

**Update Frequency**: Weekly aggregate (5-10 new posts/week across all feeds)

---

#### Tech News & Analysis (5 feeds)

```json
{
  "rss": {
    "enabled": true,
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

**Rationale**:
- **TechCrunch**: Startup funding, product launches (20-30 posts/day)
- **The Verge**: Consumer tech, reviews, policy (30-40 posts/day)
- **Ars Technica**: Deep tech analysis, security (10-15 posts/day)
- **Hacker News**: Community-curated tech news (30 posts/30 min, filter by score)
- **Wired**: Tech culture, longform analysis (5-10 posts/day)

**Update Frequency**: Daily (filter by score/engagement to avoid spam)

---

### Blog Scrapers (5 sources)

#### Individual Tech Blogs

```json
{
  "blog": {
    "enabled": true,
    "urls": [
      {
        "url": "https://www.fast.ai/posts/",
        "selectors": {
          "article": "article",
          "title": "h1.post-title",
          "content": "div.post-content",
          "author": "span.author-name",
          "date": "time"
        }
      },
      {
        "url": "https://lilianweng.github.io/",
        "selectors": {
          "article": "article.post",
          "title": "h1.post-title",
          "content": "div.post-content",
          "author": "span.post-author",
          "date": "time.post-date"
        }
      },
      {
        "url": "https://distill.pub/",
        "selectors": {
          "article": "article",
          "title": "h1",
          "content": "d-article",
          "author": "d-byline",
          "date": "time"
        }
      },
      {
        "url": "https://www.understandingai.org/",
        "selectors": {
          "article": "article",
          "title": "h1.entry-title",
          "content": "div.entry-content",
          "author": "span.author",
          "date": "time.published"
        }
      },
      {
        "url": "https://sebastianraschka.com/blog/index.html",
        "selectors": {
          "article": "article",
          "title": "h2.post-title",
          "content": "div.post-content",
          "author": "span.author",
          "date": "time"
        }
      }
    ]
  }
}
```

**Rationale**:
- **fast.ai**: Practical deep learning, accessible tutorials (1 post/month)
- **Lilian Weng**: In-depth ML explainers, OpenAI research (1 post/2-3 months)
- **Distill.pub**: Interactive ML research visualizations (1 post/quarter)
- **Understanding AI**: AI policy, explainers (1 post/2 months)
- **Sebastian Raschka**: ML engineering, Python (2 posts/month)

**Update Frequency**: Monthly aggregate (3-5 new posts/month across all blogs)

---

## Recommended Scraping Schedule

Based on source update frequencies:

```json
{
  "scheduler": {
    "jobs": [
      {
        "name": "High-Frequency Content Scrape",
        "schedule": "0 */6 * * *",
        "sources": ["reddit"],
        "description": "Scrape Reddit every 6 hours (4x daily)"
      },
      {
        "name": "Medium-Frequency Content Scrape",
        "schedule": "0 9 * * *",
        "sources": ["youtube"],
        "description": "Scrape YouTube once daily (9 AM UTC)"
      },
      {
        "name": "Low-Frequency Content Scrape",
        "schedule": "0 9 * * 1",
        "sources": ["rss", "blog"],
        "description": "Scrape RSS/blogs once weekly (Monday 9 AM UTC)"
      }
    ]
  }
}
```

**Industry Standard**: Tier-based scraping aligns with how content platforms update:
- Reddit: 6-hour intervals capture 80% of new hot posts without excessive duplicates
- YouTube: Daily scraping captures new uploads without hitting API quotas
- RSS/Blogs: Weekly scraping balances freshness with low-frequency updates

---

## Content Quality Indicators

### Reddit
- **Score threshold**: Minimum 50 upvotes (filters low-quality posts)
- **Comment threshold**: Minimum 10 comments (indicates engagement)
- **Subreddit size**: 50K+ members (active community)

### YouTube
- **View threshold**: Minimum 10K views within 7 days (viral indicator)
- **Like ratio**: > 95% like ratio (quality signal)
- **Channel size**: 50K+ subscribers (consistent quality)

### RSS/Blogs
- **Post length**: Minimum 500 words (substantive content)
- **Update frequency**: At least 1 post/quarter (active blog)
- **Domain authority**: DA 50+ (trusted source)

---

## Source Expansion Strategy

### Phase 1: Core 15 Sources (Week 1)
Start with 3 Reddit subreddits + 2 YouTube channels + 2 RSS feeds for your niche.

### Phase 2: Diversify (Week 2-3)
Add 10 more Reddit subreddits + 5 YouTube channels + 3 RSS feeds.

### Phase 3: Optimize (Week 4+)
Analyze newsletter analytics:
- Which sources get highest click-through rates?
- Which sources generate most engagement?
- Remove low-performing sources, add similar high-performers.

---

## Niche-Specific Recommendations

### For AI/ML Newsletters
**Reddit**: MachineLearning, LocalLLaMA, OpenAI, LangChain
**YouTube**: Two Minute Papers, Sentdex, CodeEmporium
**RSS**: OpenAI Blog, Hugging Face Blog, Google AI Blog
**Blogs**: fast.ai, Lilian Weng

### For Web Development Newsletters
**Reddit**: webdev, reactjs, nextjs, javascript
**YouTube**: Fireship, Corey Schafer, TechWorld with Nana
**RSS**: TechCrunch, The Verge
**Blogs**: CSS-Tricks, Smashing Magazine

### For Startup/Business Newsletters
**Reddit**: Entrepreneur, startups, SaaS
**YouTube**: Y Combinator, Techstars
**RSS**: TechCrunch, Hacker News
**Blogs**: Paul Graham, First Round Review

### For General Tech Newsletters
**Reddit**: technology, gadgets, programming
**YouTube**: Google for Developers, Fireship
**RSS**: The Verge, Ars Technica, Wired
**Blogs**: Stratechery, Benedict Evans

---

## Troubleshooting

### High Duplicate Rate (> 90%)
**Cause**: Scraping too frequently for low-frequency sources
**Fix**: Adjust to 6-hour intervals for Reddit, daily for YouTube, weekly for RSS/blogs

### Low Content Variety
**Cause**: Too few sources or all sources in same niche
**Fix**: Add 5-10 sources from different categories (mix AI + business + productivity)

### Low Engagement Metrics
**Cause**: Low-quality sources or generic content
**Fix**: Use [Content Quality Indicators](#content-quality-indicators) to filter sources

### API Rate Limits
**Cause**: YouTube/Twitter API quota exceeded
**Fix**: Reduce scraping frequency or rotate API keys

---

## Additional Resources

- **Reddit API Docs**: https://www.reddit.com/dev/api/
- **YouTube Data API**: https://developers.google.com/youtube/v3
- **RSS Feed Finder**: https://rss.app/
- **Blog Scraper Testing**: Use browser DevTools to inspect CSS selectors

---

## Version History

- **v1.0** (2025-01-24): Initial release with 50+ sources
- Future: Add Twitter/X sources when API credentials fixed
- Future: Add LinkedIn sources (requires LinkedIn API access)
- Future: Add Substack/Ghost newsletter aggregation

---

**Need Help?** See [MANAGING_CONTENT_SOURCES.md](./guides/MANAGING_CONTENT_SOURCES.md) for UI/API instructions.
