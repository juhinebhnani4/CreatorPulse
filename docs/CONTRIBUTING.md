# Contributing to AI Newsletter Scraper

Thank you for your interest in contributing! This document provides guidelines for adding new scrapers and contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Adding a New Scraper](#adding-a-new-scraper)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a feature branch: `git checkout -b feature/my-new-scraper`
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Install in editable mode
pip install -e .
```

## Adding a New Scraper

### Step 1: Create the Scraper Class

Create a new file in `src/ai_newsletter/scrapers/` (e.g., `hackernews_scraper.py`):

```python
"""
Hacker News scraper implementation.
"""

from datetime import datetime
from typing import List, Dict, Any

from .base import BaseScraper
from ..models.content import ContentItem


class HackerNewsScraper(BaseScraper):
    """
    Scraper for Hacker News.
    
    Fetches stories from Hacker News using their API.
    
    Example:
        scraper = HackerNewsScraper()
        items = scraper.fetch_content(limit=10)
        df = scraper.to_dataframe(items)
    """
    
    def __init__(self, **kwargs):
        """Initialize the Hacker News scraper."""
        super().__init__(
            source_name="hackernews",
            source_type="news",
            **kwargs
        )
        self.api_base = "https://hacker-news.firebaseio.com/v0"
    
    def fetch_content(
        self,
        limit: int = 10,
        story_type: str = "top",  # top, best, new
        **kwargs
    ) -> List[ContentItem]:
        """
        Fetch stories from Hacker News.
        
        Args:
            limit: Number of stories to fetch
            story_type: Type of stories (top, best, new)
            **kwargs: Additional parameters
            
        Returns:
            List of ContentItem objects
        """
        # Implementation here
        pass
    
    def _parse_item(self, raw_item: Dict[str, Any]) -> ContentItem:
        """
        Parse a Hacker News story into a ContentItem.
        
        Args:
            raw_item: Raw story data from HN API
            
        Returns:
            ContentItem object
        """
        # Implementation here
        pass
```

### Step 2: Required Methods

Every scraper MUST implement:

#### `__init__(self, **kwargs)`
- Call `super().__init__()` with `source_name` and `source_type`
- Initialize any API clients or session objects
- Set up necessary configuration

#### `fetch_content(self, limit: int = 10, **kwargs) -> List[ContentItem]`
- Fetch data from the source
- Call `_parse_item()` for each raw item
- Use `validate_item()` to ensure data quality
- Return list of ContentItem objects
- Handle errors gracefully with logging

#### `_parse_item(self, raw_item: Any) -> ContentItem`
- Convert source-specific data to ContentItem
- Map all available fields
- Use source-specific data in `metadata` dict
- Return a ContentItem instance

### Step 3: Add Configuration Support

Add configuration in `src/ai_newsletter/config/settings.py`:

```python
@dataclass
class HackerNewsConfig(ScraperConfig):
    """Hacker News-specific configuration."""
    story_type: str = "top"
    min_score: int = 10
```

Then add to Settings class:
```python
@dataclass
class Settings:
    # ... existing fields ...
    hackernews: HackerNewsConfig = field(default_factory=HackerNewsConfig)
```

### Step 4: Update Package Exports

Add to `src/ai_newsletter/scrapers/__init__.py`:

```python
from .hackernews_scraper import HackerNewsScraper

__all__ = [
    # ... existing exports ...
    "HackerNewsScraper",
]
```

### Step 5: Write Tests

Create `tests/unit/test_hackernews_scraper.py`:

```python
import pytest
from src.ai_newsletter.scrapers.hackernews_scraper import HackerNewsScraper


class TestHackerNewsScraper:
    def test_initialization(self):
        scraper = HackerNewsScraper()
        assert scraper.source_name == "hackernews"
        assert scraper.source_type == "news"
    
    # Add more tests...
```

Create `tests/integration/test_hackernews_scraper.py`:

```python
import pytest
from src.ai_newsletter.scrapers.hackernews_scraper import HackerNewsScraper


@pytest.mark.integration
class TestHackerNewsScraperIntegration:
    def test_fetch_content(self):
        scraper = HackerNewsScraper()
        items = scraper.fetch_content(limit=5)
        
        assert len(items) > 0
        assert all(item.source == "hackernews" for item in items)
    
    # Add more integration tests...
```

### Step 6: Add Documentation

Update `docs/scrapers/hackernews.md` with:
- Overview of the scraper
- Configuration options
- Usage examples
- Rate limits and best practices
- Known limitations

### Step 7: Update Requirements

If your scraper needs additional dependencies:

```bash
# Add to requirements.txt
new-package==1.0.0
```

## Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use docstrings for all classes and methods

### Docstring Format

```python
def fetch_content(self, limit: int = 10, **kwargs) -> List[ContentItem]:
    """
    Fetch content from the source.
    
    This method retrieves content items from the source API and converts
    them to the standardized ContentItem format.
    
    Args:
        limit: Maximum number of items to fetch
        **kwargs: Additional source-specific parameters
        
    Returns:
        List of ContentItem objects
        
    Raises:
        ValueError: If limit is invalid
        RequestException: If API request fails
        
    Example:
        >>> scraper = MyScraper()
        >>> items = scraper.fetch_content(limit=10)
        >>> print(len(items))
        10
    """
    pass
```

### Formatting

Use `black` for code formatting:

```bash
black src/ tests/
```

### Linting

Run linters before committing:

```bash
flake8 src/ tests/
mypy src/
```

## Testing

### Test Requirements

- **Unit tests**: Test individual methods in isolation
- **Integration tests**: Test actual API calls (mark with `@pytest.mark.integration`)
- **Coverage**: Aim for >80% code coverage

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit

# Integration tests only
pytest -m integration

# With coverage
pytest --cov=src/ai_newsletter --cov-report=html
```

### Test Structure

```python
class TestMyScraper:
    """Tests for MyScraper class."""
    
    def test_initialization(self):
        """Test scraper initialization."""
        scraper = MyScraper()
        assert scraper.source_name == "mysource"
    
    def test_parse_item(self):
        """Test parsing a single item."""
        scraper = MyScraper()
        raw_item = {"title": "Test", "url": "https://example.com"}
        item = scraper._parse_item(raw_item)
        
        assert isinstance(item, ContentItem)
        assert item.title == "Test"
    
    @pytest.mark.integration
    def test_fetch_real_data(self):
        """Test fetching real data from API."""
        scraper = MyScraper()
        items = scraper.fetch_content(limit=5)
        
        assert len(items) > 0
```

## Documentation

### Required Documentation

1. **Inline comments**: For complex logic
2. **Docstrings**: For all public classes and methods
3. **README section**: Add usage example to main README
4. **Scraper guide**: Create detailed guide in `docs/scrapers/`

### Documentation Template

Create `docs/scrapers/mysource.md`:

```markdown
# MySource Scraper

## Overview
Brief description of the source and what it provides.

## Configuration
```json
{
  "mysource": {
    "enabled": true,
    "limit": 10,
    "api_key": "your_key"
  }
}
```

## Usage
```python
from ai_newsletter.scrapers import MySourceScraper

scraper = MySourceScraper()
items = scraper.fetch_content(limit=10)
```

## Rate Limits
- API allows X requests per hour
- Recommended: Use limit <= 100

## Known Issues
- List any known issues or limitations
```

## Pull Request Process

1. **Update documentation**: Ensure all docs are current
2. **Add tests**: Include both unit and integration tests
3. **Run tests**: Ensure all tests pass
4. **Update CHANGELOG**: Add entry for your changes
5. **Create PR**: Use descriptive title and description

### PR Title Format

```
[Type] Brief description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- test: Adding tests
- refactor: Code refactoring
- perf: Performance improvement
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New scraper
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance improvement

## Checklist
- [ ] Code follows style guidelines
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Updated documentation
- [ ] All tests pass
- [ ] No linting errors

## Testing
Describe how you tested your changes

## Screenshots (if applicable)
Add screenshots for UI changes
```

## Best Practices

### Error Handling

```python
def fetch_content(self, limit: int = 10, **kwargs):
    try:
        response = self.session.get(url)
        response.raise_for_status()
        # ... process response ...
    except requests.RequestException as e:
        self.logger.error(f"Failed to fetch: {e}")
        return []
    except ValueError as e:
        self.logger.error(f"Invalid data: {e}")
        return []
```

### Logging

```python
# Use appropriate log levels
self.logger.debug("Detailed information")
self.logger.info("General information")
self.logger.warning("Warning message")
self.logger.error("Error message")
```

### Rate Limiting

```python
import time

def fetch_content(self, limit: int = 10, **kwargs):
    items = []
    for i in range(limit):
        # Respect rate limits
        time.sleep(0.1)  # 100ms delay
        item = self._fetch_single_item(i)
        items.append(item)
    return items
```

### Type Hints

```python
from typing import List, Dict, Optional, Any

def fetch_content(
    self,
    limit: int = 10,
    options: Optional[Dict[str, Any]] = None
) -> List[ContentItem]:
    pass
```

## Questions?

- Open an issue for questions
- Join our Discord community (link)
- Email: support@ainewsletter.dev

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

