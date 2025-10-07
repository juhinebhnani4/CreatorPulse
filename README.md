# AI Newsletter Scraper

A modular and extensible content scraping framework for aggregating AI-related news from multiple sources including Reddit, RSS feeds, blogs, and X (Twitter).

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

- **Multi-Source Support**: Aggregate content from Reddit, RSS feeds, blogs, and X (Twitter)
- **Extensible Architecture**: Easy to add new scrapers for additional sources
- **Unified Data Model**: Consistent interface across all content sources
- **Interactive UI**: Beautiful Streamlit web interface for browsing content
- **Flexible Filtering**: Filter and sort content by score, comments, date, and more
- **Configuration Management**: JSON-based configuration with environment variable support
- **Export Capabilities**: Download aggregated content as CSV
- **Comprehensive Tests**: Unit and integration tests included

## 📁 Project Structure

```
ai-newsletter-v2/
├── src/
│   └── ai_newsletter/
│       ├── __init__.py
│       ├── scrapers/           # Scraper implementations
│       │   ├── base.py         # Abstract base scraper
│       │   ├── reddit_scraper.py
│       │   ├── rss_scraper.py
│       │   ├── blog_scraper.py
│       │   └── x_scraper.py
│       ├── models/             # Data models
│       │   └── content.py
│       ├── utils/              # Utility functions
│       │   └── scraper_registry.py
│       └── config/             # Configuration management
│           └── settings.py
│   └── streamlit_app.py        # Streamlit UI
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── docs/                       # Documentation
├── examples/                   # Example scripts
├── config.example.json         # Example configuration
├── requirements.txt
├── setup.py
├── pytest.ini
└── README.md
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-newsletter-v2
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Optional: Install in development mode**
```bash
pip install -e .
```

### Running the Streamlit App

```bash
streamlit run src/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### Using Scrapers Programmatically

```python
from ai_newsletter.scrapers import RedditScraper, RSSFeedScraper

# Reddit scraper
reddit = RedditScraper()
items = reddit.fetch_content(subreddit='AI_Agents', limit=10)

# RSS scraper
rss = RSSFeedScraper()
items = rss.fetch_content(
    feed_urls=['https://blog.openai.com/rss/'],
    limit=10
)

# Convert to DataFrame
df = reddit.to_dataframe(items)
print(df.head())
```

## 📊 Available Scrapers

### 1. Reddit Scraper
Fetches posts from Reddit subreddits.

```python
from ai_newsletter.scrapers import RedditScraper

scraper = RedditScraper()
items = scraper.fetch_content(
    subreddit='AI_Agents',
    limit=25,
    sort='hot'  # hot, new, top, rising
)
```

### 2. RSS Feed Scraper
Fetches entries from RSS/Atom feeds.

```python
from ai_newsletter.scrapers import RSSFeedScraper

scraper = RSSFeedScraper()
items = scraper.fetch_content(
    feed_urls=[
        'https://blog.openai.com/rss/',
        'https://ai.googleblog.com/feeds/posts/default'
    ],
    limit=10
)
```

### 3. Blog Scraper
Scrapes blog posts using CSS selectors.

```python
from ai_newsletter.scrapers import BlogScraper

scraper = BlogScraper()
items = scraper.fetch_with_template(
    url='https://blog.example.com',
    template_name='wordpress',  # wordpress, medium, ghost, substack
    limit=10
)
```

### 4. X (Twitter) Scraper
Fetches posts from X (requires API credentials).

```python
from ai_newsletter.scrapers.x_scraper import XScraper

scraper = XScraper(
    api_key='your_api_key',
    api_secret='your_api_secret',
    access_token='your_access_token',
    access_token_secret='your_access_token_secret'
)
items = scraper.fetch_content(query='#AI', limit=10)
```

## 🔧 Configuration

### Using config.json

Copy `config.example.json` to `config.json` and customize:

```json
{
  "reddit": {
    "enabled": true,
    "limit": 25,
    "subreddits": ["AI_Agents", "MachineLearning"],
    "sort": "hot"
  },
  "rss": {
    "enabled": true,
    "limit": 10,
    "feed_urls": [
      "https://blog.openai.com/rss/"
    ]
  }
}
```

### Using Environment Variables

```bash
export X_API_KEY=your_api_key
export X_API_SECRET=your_api_secret
export DEBUG=true
```

## 🧩 Creating a New Scraper

All scrapers must extend the `BaseScraper` class:

```python
from ai_newsletter.scrapers.base import BaseScraper
from ai_newsletter.models.content import ContentItem
from datetime import datetime

class MyCustomScraper(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(
            source_name="mycustom",
            source_type="custom",
            **kwargs
        )
    
    def fetch_content(self, limit=10, **kwargs):
        # Your fetching logic here
        items = []
        # ... fetch data ...
        for raw_item in data:
            item = self._parse_item(raw_item)
            items.append(item)
        return items
    
    def _parse_item(self, raw_item):
        return ContentItem(
            title=raw_item['title'],
            source=self.source_name,
            source_url=raw_item['url'],
            created_at=datetime.now(),
            # ... other fields ...
        )
```

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run only unit tests:
```bash
pytest tests/unit
```

Run only integration tests:
```bash
pytest -m integration
```

## 📚 Data Model

All content is standardized using the `ContentItem` model:

| Field | Type | Description |
|-------|------|-------------|
| `title` | str | Content title |
| `source` | str | Source identifier (reddit, rss, etc.) |
| `source_url` | str | URL to the original content |
| `created_at` | datetime | Publication date |
| `content` | str | Full content text |
| `summary` | str | Short summary |
| `author` | str | Author name |
| `score` | int | Engagement score |
| `comments_count` | int | Number of comments |
| `tags` | list | Content tags/categories |
| `metadata` | dict | Source-specific metadata |

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### Adding a New Scraper

1. Create a new file in `src/ai_newsletter/scrapers/`
2. Extend `BaseScraper` and implement required methods
3. Add configuration in `config/settings.py`
4. Add tests in `tests/`
5. Update documentation
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Reddit API for public JSON endpoints
- feedparser for RSS parsing
- BeautifulSoup for web scraping
- Streamlit for the beautiful UI framework

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Add support for more sources (Hacker News, Product Hunt, etc.)
- [ ] Implement caching mechanism
- [ ] Add sentiment analysis
- [ ] Create scheduled scraping with notifications
- [ ] Add database storage support
- [ ] Implement API endpoints
- [ ] Add content deduplication
- [ ] Create Docker deployment

## 📊 Example Output

The Streamlit app provides:
- **Summary Statistics**: Total items, sources, average scores
- **Source Distribution**: Visual breakdown of content by source
- **Filtering**: By source, score, comments, date
- **Sorting**: By multiple criteria
- **Detailed View**: Full content display with metadata
- **Export**: Download filtered results as CSV

---

**Built with ❤️ for the AI community**
