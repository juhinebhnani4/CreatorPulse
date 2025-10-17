# CreatorPulse - AI Newsletter Generator

Transform your content aggregation into automated newsletters. Scrape from multiple sources, generate AI-powered newsletters, and deliver them automatically.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

### 📡 Multi-Source Content Aggregation
- **Reddit**: Scrape posts from AI-related subreddits
- **RSS Feeds**: Aggregate content from AI blogs and news sites
- **YouTube**: Fetch videos from AI channels and search results
- **X (Twitter)**: Collect posts with AI hashtags and keywords
- **Blogs**: Scrape content from any website with CSS selectors

### 🤖 AI-Powered Newsletter Generation
- **OpenAI Integration**: Generate engaging newsletters using GPT-4
- **Customizable Templates**: Professional HTML newsletter templates
- **Smart Content Curation**: AI selects and summarizes the best content
- **Multiple Tones**: Professional, casual, technical, or friendly
- **Multi-language Support**: Generate newsletters in different languages

### 📧 Automated Email Delivery
- **SMTP Support**: Send via Gmail, Outlook, or any SMTP server
- **SendGrid Integration**: Professional email delivery service
- **Bulk Sending**: Send newsletters to multiple recipients
- **Email Validation**: Built-in email address validation
- **Delivery Tracking**: Monitor email delivery status

### ⏰ Intelligent Scheduling
- **Daily Automation**: Schedule newsletters for any time
- **Timezone Support**: Global timezone compatibility
- **Retry Logic**: Automatic retry on failures
- **Job Management**: Start, stop, pause, and resume jobs
- **Status Monitoring**: Real-time job status tracking

### 🎨 Beautiful Web Interface
- **Streamlit UI**: Modern, responsive web interface
- **Newsletter Preview**: Preview newsletters before sending
- **Configuration Management**: Easy setup and configuration
- **Real-time Status**: Monitor all components and services
- **Export Capabilities**: Download content and newsletters

## 📁 Project Structure

```
creatorpulse/
├── src/
│   └── ai_newsletter/
│       ├── __init__.py
│       ├── scrapers/           # Content scrapers
│       │   ├── base.py          # Abstract base scraper
│       │   ├── reddit_scraper.py
│       │   ├── rss_scraper.py
│       │   ├── blog_scraper.py
│       │   ├── x_scraper.py
│       │   └── youtube_scraper.py
│       ├── generators/          # Newsletter generation
│       │   ├── newsletter_generator.py
│       │   └── templates/
│       │       └── default.html
│       ├── delivery/            # Email delivery
│       │   └── email_sender.py
│       ├── scheduler/           # Automation
│       │   └── daily_scheduler.py
│       ├── orchestrator/        # Pipeline coordination
│       │   └── pipeline.py
│       ├── models/              # Data models
│       │   └── content.py
│       ├── utils/               # Utility functions
│       │   └── scraper_registry.py
│       └── config/              # Configuration management
│           └── settings.py
│   └── streamlit_app.py        # Web interface
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── examples/                   # Example scripts
│   ├── creatorpulse_example.py
│   ├── generate_newsletter.py
│   └── scheduled_newsletter.py
├── config.example.json         # Configuration template
├── .env.example                # Environment variables template
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/creatorpulse.git
   cd creatorpulse
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**
   ```bash
   cp config.example.json config.json
   cp env.example .env
   ```

5. **Configure your settings**
   - Edit `config.json` with your preferences
   - Add API keys to `.env`:
     ```
     # Required for newsletter generation
     OPENAI_API_KEY=your_openai_api_key_here
     
     # Required for email delivery (choose one)
     SMTP_SERVER=smtp.gmail.com
     SMTP_USERNAME=your_email@gmail.com
     SMTP_PASSWORD=your_app_password_here
     FROM_EMAIL=your_email@gmail.com
     
     # OR use SendGrid instead
     SENDGRID_API_KEY=your_sendgrid_api_key_here
     USE_SENDGRID=true
     
     # Optional: For content sources
     YOUTUBE_API_KEY=your_youtube_api_key_here
     X_API_KEY=your_x_api_key_here
     X_API_SECRET=your_x_api_secret_here
     X_ACCESS_TOKEN=your_x_access_token_here
     X_ACCESS_TOKEN_SECRET=your_x_access_token_secret_here
     X_BEARER_TOKEN=your_x_bearer_token_here
     ```

6. **Run the Streamlit app**
   ```bash
   streamlit run src/streamlit_app.py
   ```

The app will open in your browser at `http://localhost:8501`

### Using CreatorPulse Programmatically

```python
from src.ai_newsletter.orchestrator.pipeline import NewsletterPipeline
from src.ai_newsletter.config.settings import Settings

# Load configuration
settings = Settings.from_json("config.json")

# Create pipeline
pipeline = NewsletterPipeline(settings)

# Generate and send newsletter
pipeline.run_pipeline()
```

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

### 4. YouTube Scraper
Fetches videos from YouTube channels, playlists, or search queries.

```python
from ai_newsletter.scrapers import YouTubeScraper

scraper = YouTubeScraper(api_key='your_youtube_api_key')
items = scraper.fetch_content(
    channel_id='UC_x5XG1OV2P6uZZ5FSM9Ttw',  # Google Developers
    limit=10,
    order='relevance'  # relevance, date, rating, viewCount
)
```

### 5. X (Twitter) Scraper
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

## 🤖 CreatorPulse Features

### Newsletter Generation
Generate AI-powered newsletters from your scraped content:

```python
from ai_newsletter.generators import NewsletterGenerator

generator = NewsletterGenerator(api_key='your_openai_key')
newsletter = generator.generate_newsletter(
    content_items=items,
    tone='professional',
    language='en',
    max_items=10
)
```

### Email Delivery
Send newsletters via SMTP or SendGrid:

```python
from ai_newsletter.delivery import EmailSender

sender = EmailSender(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    username='your_email@gmail.com',
    password='your_app_password'
)

sender.send_newsletter(
    newsletter=newsletter,
    recipients=['subscriber@example.com'],
    subject='Your Weekly AI Newsletter'
)
```

### Automated Scheduling
Schedule daily newsletter generation and delivery:

```python
from ai_newsletter.scheduler import DailyScheduler

scheduler = DailyScheduler()
scheduler.schedule_daily_newsletter(
    hour=9,
    minute=0,
    timezone='America/New_York'
)
scheduler.start()
```

### Complete Pipeline
Run the entire workflow with one command:

```python
from ai_newsletter.orchestrator import NewsletterPipeline

pipeline = NewsletterPipeline()
result = pipeline.run_pipeline()
print(f"Newsletter sent to {result['recipients_count']} recipients")
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
  },
  "youtube": {
    "enabled": true,
    "limit": 10,
    "channels": ["UC_x5XG1OV2P6uZZ5FSM9Ttw"],
    "order": "relevance"
  },
  "newsletter": {
    "tone": "professional",
    "language": "en",
    "max_items": 10,
    "template": "default"
  },
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your_email@gmail.com",
    "use_sendgrid": false
  },
  "scheduler": {
    "enabled": true,
    "hour": 9,
    "minute": 0,
    "timezone": "America/New_York"
  }
}
```

### Using Environment Variables

```bash
# Required for newsletter generation
export OPENAI_API_KEY=your_openai_api_key_here

# Required for email delivery (choose one)
export SMTP_SERVER=smtp.gmail.com
export SMTP_USERNAME=your_email@gmail.com
export SMTP_PASSWORD=your_app_password_here
export FROM_EMAIL=your_email@gmail.com

# OR use SendGrid instead
export SENDGRID_API_KEY=your_sendgrid_api_key_here
export USE_SENDGRID=true

# Optional: For content sources
export YOUTUBE_API_KEY=your_youtube_api_key_here
export X_API_KEY=your_x_api_key_here
export X_API_SECRET=your_x_api_secret_here
export X_ACCESS_TOKEN=your_x_access_token_here
export X_ACCESS_TOKEN_SECRET=your_x_access_token_secret_here
export X_BEARER_TOKEN=your_x_bearer_token_here

# General Settings
export DEBUG=false
export LOG_LEVEL=INFO
export SCHEDULER_ENABLED=true
export SCHEDULER_TIME=08:00
export SCHEDULER_TIMEZONE=UTC
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

- **Reddit API** for public JSON endpoints
- **YouTube Data API v3** for video content access
- **OpenAI API** for AI-powered newsletter generation
- **SendGrid** for professional email delivery
- **feedparser** for RSS parsing
- **BeautifulSoup** for web scraping
- **APScheduler** for job scheduling
- **Streamlit** for the beautiful UI framework

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🗺️ Roadmap

### ✅ Completed Features
- [x] Multi-source content aggregation (Reddit, RSS, YouTube, X, Blogs)
- [x] AI-powered newsletter generation with OpenAI
- [x] Automated email delivery (SMTP & SendGrid)
- [x] Daily scheduling with APScheduler
- [x] Complete pipeline orchestration
- [x] Streamlit web interface
- [x] Comprehensive configuration management
- [x] Unit and integration testing

### 🚀 Future Enhancements
- [ ] Add support for more sources (Hacker News, Product Hunt, LinkedIn)
- [ ] Implement caching mechanism for better performance
- [ ] Add sentiment analysis for content filtering
- [ ] Create advanced newsletter templates
- [ ] Add database storage support
- [ ] Implement REST API endpoints
- [ ] Add content deduplication across sources
- [ ] Create Docker deployment configuration
- [ ] Add analytics and reporting dashboard
- [ ] Implement A/B testing for newsletter formats

## 📊 Example Output

The Streamlit app provides:

### Content Scraping
- **Summary Statistics**: Total items, sources, average scores
- **Source Distribution**: Visual breakdown of content by source
- **Filtering**: By source, score, comments, date
- **Sorting**: By multiple criteria
- **Detailed View**: Full content display with metadata
- **Export**: Download filtered results as CSV

### Newsletter Generation
- **AI-Powered Content**: Generate engaging newsletters from scraped content
- **Preview Mode**: See newsletters before sending
- **Template Selection**: Choose from multiple newsletter templates
- **Tone Customization**: Professional, casual, technical, or friendly
- **Multi-language Support**: Generate in different languages

### Email Delivery
- **Recipient Management**: Add, edit, and manage subscriber lists
- **Delivery Testing**: Send test emails before bulk delivery
- **Delivery Status**: Track email delivery success and failures
- **Bulk Operations**: Send newsletters to multiple recipients

### Scheduling
- **Daily Automation**: Set up recurring newsletter delivery
- **Timezone Support**: Schedule for any timezone
- **Job Management**: Start, stop, pause, and resume scheduled jobs
- **Status Monitoring**: Real-time monitoring of scheduled tasks

---

**Built with ❤️ for the AI community**
