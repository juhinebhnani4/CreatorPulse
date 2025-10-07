# Quick Start Guide

## Overview

This guide will help you get the AI Newsletter Scraper up and running quickly.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for Mac M1/M2 users**: If you encounter architecture issues with numpy/pandas, try:

```bash
# Use Rosetta or install ARM-compatible versions
arch -arm64 pip install -r requirements.txt

# Or create a new virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python quick_test.py
```

This will verify that the package structure is correct and all components can be imported.

## Running the Application

### Option 1: Use the Quick Start Script

```bash
python run.py
```

### Option 2: Run Streamlit Directly

```bash
streamlit run src/streamlit_app.py
```

### Option 3: Use Python API

```bash
python examples/basic_usage.py
```

The Streamlit app will open in your browser at `http://localhost:8501`

## Basic Usage

### 1. Using the Streamlit UI

1. Launch the app: `python run.py`
2. Select your data sources (Reddit, RSS, etc.)
3. Configure source-specific settings in the sidebar
4. Click "Fetch Content"
5. Filter, sort, and explore the results
6. Download as CSV if needed

### 2. Using in Python Code

```python
from ai_newsletter.scrapers import RedditScraper, RSSFeedScraper

# Fetch from Reddit
reddit = RedditScraper()
items = reddit.fetch_content(subreddit='AI_Agents', limit=10)

# Fetch from RSS feeds
rss = RSSFeedScraper()
items = rss.fetch_content(
    feed_urls=['https://blog.openai.com/rss/'],
    limit=10
)

# Convert to DataFrame
df = reddit.to_dataframe(items)
print(df.head())
```

## Configuration

### Basic Configuration

Copy the example configuration:

```bash
cp config.example.json config.json
```

Edit `config.json` to customize:

```json
{
  "reddit": {
    "enabled": true,
    "limit": 25,
    "subreddits": ["AI_Agents", "MachineLearning"]
  },
  "rss": {
    "enabled": true,
    "feed_urls": [
      "https://blog.openai.com/rss/"
    ]
  }
}
```

### Environment Variables

For sensitive data like API keys:

```bash
export X_API_KEY=your_key_here
export X_API_SECRET=your_secret_here
```

Or create a `.env` file:

```
X_API_KEY=your_key_here
X_API_SECRET=your_secret_here
DEBUG=false
```

## Available Scrapers

### Reddit
- ✅ Works out of the box
- ✅ No authentication required
- ✅ Multiple subreddits supported

### RSS Feeds
- ✅ Works out of the box
- ✅ Supports RSS and Atom
- ✅ Multiple feeds supported

### Blogs
- ✅ Works out of the box
- ⚠️ Requires CSS selector configuration
- ✅ Template support for popular platforms

### X (Twitter)
- ⚠️ Requires API credentials
- ⚠️ Rate limited
- ℹ️ See [X API documentation](https://developer.twitter.com/)

## Troubleshooting

### Common Issues

#### 1. Module Import Errors

```bash
# Make sure you're in the project root
cd /path/to/ai-newsletter-v2

# Install dependencies
pip install -r requirements.txt

# If using examples, run from project root
python examples/basic_usage.py
```

#### 2. Architecture Mismatch (Mac M1/M2)

```bash
# Create a fresh virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with ARM architecture
arch -arm64 pip install -r requirements.txt
```

#### 3. Streamlit Won't Start

```bash
# Check if streamlit is installed
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit

# Run with verbose output
streamlit run src/streamlit_app.py --logger.level=debug
```

#### 4. No Data Fetched

- Check your internet connection
- Verify the source is accessible
- Check rate limits
- Review logs for errors

### Getting Help

1. Check the [documentation](docs/)
2. Review [examples](examples/)
3. Open an issue on GitHub
4. Read the [Contributing Guide](docs/CONTRIBUTING.md)

## Next Steps

### Explore Examples

```bash
# Basic usage
python examples/basic_usage.py

# Create a custom scraper
python examples/custom_scraper.py
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=src/ai_newsletter
```

### Add a New Scraper

1. Read [CONTRIBUTING.md](docs/CONTRIBUTING.md)
2. Check [ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. Copy an existing scraper as a template
4. Implement required methods
5. Add tests
6. Submit a PR!

## Features Overview

### ✅ Current Features

- Multi-source content aggregation
- Unified data model
- Interactive web UI
- Filtering and sorting
- CSV export
- Extensible architecture
- Comprehensive tests

### 🚧 Planned Features

- Database storage
- Scheduled scraping
- Email notifications
- Content deduplication
- Sentiment analysis
- API endpoints
- Docker deployment

## Resources

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture
- [CONTRIBUTING.md](docs/CONTRIBUTING.md) - Contribution guidelines
- [config.example.json](config.example.json) - Configuration example

## Support

Need help? Here's how to get it:

1. **Documentation**: Check the `docs/` directory
2. **Examples**: Review `examples/` for code samples
3. **Issues**: Open a GitHub issue
4. **Community**: Join our discussions

---

**Happy scraping! 🤖**

