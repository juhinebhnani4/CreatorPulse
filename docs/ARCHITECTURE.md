# Architecture Overview

## Design Philosophy

The AI Newsletter Scraper is built with these core principles:

1. **Extensibility**: Easy to add new content sources
2. **Modularity**: Each component has a single responsibility
3. **Consistency**: Unified interface across all scrapers
4. **Testability**: Comprehensive test coverage
5. **Configurability**: Flexible configuration system

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit UI Layer                     │
│                  (streamlit_app.py)                      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                  Scraper Registry                        │
│              (utils/scraper_registry.py)                 │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐  ┌────▼────┐  ┌──────▼───────┐
│   Reddit     │  │   RSS   │  │  Blog/X/...  │
│   Scraper    │  │ Scraper │  │   Scrapers   │
└───────┬──────┘  └────┬────┘  └──────┬───────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
                ┌───────▼────────┐
                │  BaseScraper   │
                │  (base.py)     │
                └───────┬────────┘
                        │
                ┌───────▼────────┐
                │  ContentItem   │
                │  (models/)     │
                └────────────────┘
```

## Core Components

### 1. Data Model (`models/content.py`)

**ContentItem** is the unified data structure for all content:

```python
@dataclass
class ContentItem:
    # Required fields
    title: str
    source: str
    source_url: str
    created_at: datetime
    
    # Optional fields
    content: Optional[str]
    author: Optional[str]
    score: int
    comments_count: int
    # ... and more
```

**Key Features:**
- Standardized interface across all sources
- Easy serialization to/from dict
- Built-in validation

### 2. Base Scraper (`scrapers/base.py`)

**BaseScraper** is an abstract base class that all scrapers extend:

```python
class BaseScraper(ABC):
    @abstractmethod
    def fetch_content(self, limit: int, **kwargs) -> List[ContentItem]:
        """Fetch content from source"""
        
    @abstractmethod
    def _parse_item(self, raw_item: Any) -> ContentItem:
        """Parse raw item to ContentItem"""
```

**Provides:**
- Common functionality (filtering, validation, DataFrame conversion)
- Logging infrastructure
- Consistent error handling
- Standard interface

### 3. Concrete Scrapers

Each scraper implements the abstract methods:

#### RedditScraper
- Uses Reddit's public JSON API
- No authentication required
- Supports multiple subreddits
- Configurable sort methods

#### RSSFeedScraper
- Uses feedparser library
- Handles RSS and Atom feeds
- Supports multiple feeds
- Robust date parsing

#### BlogScraper
- Uses BeautifulSoup for parsing
- Configurable CSS selectors
- Template support for popular platforms
- Flexible content extraction

#### XScraper
- Uses tweepy library (optional)
- Requires API credentials
- Search and timeline support
- Rate limit handling

### 4. Scraper Registry (`utils/scraper_registry.py`)

**ScraperRegistry** manages scraper discovery and access:

```python
class ScraperRegistry:
    @classmethod
    def register(cls, name: str, scraper_class: Type[BaseScraper]):
        """Register a scraper"""
    
    @classmethod
    def get_scraper(cls, name: str) -> Type[BaseScraper]:
        """Get scraper by name"""
```

**Features:**
- Auto-discovery of scrapers
- Central scraper management
- Easy scraper lookup

### 5. Configuration System (`config/settings.py`)

**Settings** class manages configuration:

```python
@dataclass
class Settings:
    reddit: RedditConfig
    rss: RSSConfig
    blog: BlogConfig
    x: XConfig
```

**Supports:**
- JSON file configuration
- Environment variables
- Default values
- Type-safe configs

### 6. UI Layer (`streamlit_app.py`)

**Streamlit app** provides the user interface:

**Features:**
- Multi-source selection
- Source-specific configuration
- Real-time filtering and sorting
- Data export
- Detailed content view

## Data Flow

### 1. Fetching Content

```
User Request
    ↓
Streamlit UI
    ↓
Scraper Instance
    ↓
fetch_content()
    ↓
API/Web Request
    ↓
_parse_item() for each result
    ↓
ContentItem objects
    ↓
Validation
    ↓
Return List[ContentItem]
```

### 2. Display Pipeline

```
List[ContentItem]
    ↓
to_dataframe()
    ↓
pandas DataFrame
    ↓
Filtering/Sorting
    ↓
Display in UI
```

## Extension Points

### Adding a New Scraper

1. **Create scraper class** in `scrapers/`
2. **Extend BaseScraper**
3. **Implement required methods**
4. **Add configuration** in `config/settings.py`
5. **Register in** `scrapers/__init__.py`
6. **Add tests**
7. **Update documentation**

### Adding a New Data Field

1. **Update ContentItem** model
2. **Update scraper** `_parse_item()` methods
3. **Update UI** display logic
4. **Update tests**

### Adding Configuration Options

1. **Update Settings** dataclass
2. **Update config.example.json**
3. **Update scraper** to use config
4. **Update documentation**

## Error Handling Strategy

### Scraper Level
- Catch and log all exceptions
- Return empty list on error
- Continue processing valid items
- Use appropriate log levels

### Item Level
- Skip invalid items
- Log warnings for parse errors
- Validate all items before return
- Maintain partial success

### UI Level
- Display user-friendly errors
- Allow partial results
- Show detailed error messages in sidebar
- Continue with available data

## Performance Considerations

### Caching
- Session state for UI data
- Configurable cache TTL
- Future: Redis/database caching

### Rate Limiting
- Respect API rate limits
- Add delays between requests
- Handle 429 responses
- Exponential backoff

### Pagination
- Fetch in batches
- Progress indicators
- Configurable limits
- Memory-efficient processing

## Security Considerations

### API Keys
- Never commit keys to repo
- Use environment variables
- Support .env files
- Config files in .gitignore

### Input Validation
- Validate user inputs
- Sanitize URLs
- Limit request sizes
- Timeout protection

### Data Handling
- No persistent storage of sensitive data
- Clean temporary data
- Respect robots.txt
- Follow ToS of sources

## Testing Strategy

### Unit Tests
- Test individual methods
- Mock external dependencies
- Test edge cases
- Fast execution

### Integration Tests
- Test real API calls
- Mark with @pytest.mark.integration
- Test end-to-end flows
- Slower execution

### Test Coverage
- Aim for >80% coverage
- Cover error paths
- Test validation logic
- Test data transformations

## Future Enhancements

### Planned Features
- [ ] Database storage
- [ ] Scheduled scraping
- [ ] Content deduplication
- [ ] Sentiment analysis
- [ ] Email notifications
- [ ] API endpoints
- [ ] Docker deployment
- [ ] Horizontal scaling

### Potential Scrapers
- [ ] Hacker News
- [ ] Product Hunt
- [ ] GitHub Trending
- [ ] Medium
- [ ] Dev.to
- [ ] YouTube
- [ ] Podcasts

## Dependencies

### Core
- **requests**: HTTP library
- **pandas**: Data manipulation
- **streamlit**: UI framework

### Parsing
- **feedparser**: RSS parsing
- **beautifulsoup4**: HTML parsing
- **lxml**: XML/HTML parser

### Optional
- **tweepy**: Twitter/X API
- **pytest**: Testing
- **black**: Code formatting

## Deployment

### Local Development
```bash
pip install -r requirements.txt
streamlit run src/streamlit_app.py
```

### Production
- Use Docker container
- Environment-based config
- Reverse proxy (nginx)
- SSL/TLS encryption
- Rate limiting
- Monitoring and logging

## Monitoring

### Logging
- Structured logging
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Scraper-specific loggers
- Centralized log collection

### Metrics
- Scraping success rate
- Response times
- Error rates
- Item counts
- User engagement

## Conclusion

This architecture provides:
- ✅ Easy extensibility
- ✅ Clear separation of concerns
- ✅ Consistent interfaces
- ✅ Robust error handling
- ✅ Comprehensive testing
- ✅ Flexible configuration

The modular design allows contributors to easily add new scrapers without understanding the entire codebase, making the project truly community-driven.

