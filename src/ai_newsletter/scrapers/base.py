"""
Base scraper class providing a template for all content scrapers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
import logging

from ..models.content import ContentItem


class BaseScraper(ABC):
    """
    Abstract base class for all content scrapers.
    
    All scraper implementations should inherit from this class and implement
    the required abstract methods. This ensures a consistent interface across
    all scrapers and makes it easy to add new sources.
    
    Example:
        class MyCustomScraper(BaseScraper):
            def __init__(self):
                super().__init__(source_name="mycustom", source_type="custom")
            
            def fetch_content(self, limit=10, **kwargs):
                # Implementation here
                pass
            
            def _parse_item(self, raw_item):
                # Implementation here
                pass
    """
    
    def __init__(self, source_name: str, source_type: str, **kwargs):
        """
        Initialize the base scraper.
        
        Args:
            source_name: Unique identifier for this source (e.g., 'reddit', 'rss')
            source_type: Type of source (e.g., 'social', 'feed', 'blog')
            **kwargs: Additional configuration options
        """
        self.source_name = source_name
        self.source_type = source_type
        self.config = kwargs
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logger for the scraper."""
        logger = logging.getLogger(f"{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    @abstractmethod
    def fetch_content(self, limit: int = 10, **kwargs) -> List[ContentItem]:
        """
        Fetch content from the source.
        
        This is the main method that scraper implementations must provide.
        It should fetch data from the source and return a list of ContentItem objects.
        
        Args:
            limit: Maximum number of items to fetch
            **kwargs: Additional source-specific parameters
            
        Returns:
            List of ContentItem objects
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement fetch_content()")
    
    @abstractmethod
    def _parse_item(self, raw_item: Any) -> ContentItem:
        """
        Parse a raw item from the source into a ContentItem.
        
        This method should handle the source-specific data format and
        convert it into the standardized ContentItem format.
        
        Args:
            raw_item: Raw data item from the source
            
        Returns:
            ContentItem object
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _parse_item()")
    
    def to_dataframe(self, items: List[ContentItem]) -> pd.DataFrame:
        """
        Convert a list of ContentItems to a pandas DataFrame.
        
        Args:
            items: List of ContentItem objects
            
        Returns:
            pandas DataFrame
        """
        if not items:
            return pd.DataFrame()
        
        data = [item.to_dict() for item in items]
        df = pd.DataFrame(data)
        
        # Convert datetime columns
        datetime_cols = ['created_at', 'scraped_at']
        for col in datetime_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        return df
    
    def validate_item(self, item: ContentItem) -> bool:
        """
        Validate a ContentItem to ensure it has required fields.
        
        Args:
            item: ContentItem to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['title', 'source', 'source_url', 'created_at']
        
        for field in required_fields:
            value = getattr(item, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                self.logger.warning(f"Item missing required field: {field}")
                return False
        
        return True
    
    def filter_items(
        self,
        items: List[ContentItem],
        min_score: int = 0,
        min_comments: int = 0,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[ContentItem]:
        """
        Filter items based on various criteria.
        
        Args:
            items: List of ContentItem objects to filter
            min_score: Minimum score threshold
            min_comments: Minimum comments threshold
            tags: List of tags to filter by (any match)
            start_date: Filter items after this date
            end_date: Filter items before this date
            
        Returns:
            Filtered list of ContentItem objects
        """
        filtered = items
        
        if min_score > 0:
            filtered = [item for item in filtered if item.score >= min_score]
        
        if min_comments > 0:
            filtered = [item for item in filtered if item.comments_count >= min_comments]
        
        if tags:
            filtered = [
                item for item in filtered
                if any(tag in item.tags for tag in tags)
            ]
        
        if start_date:
            filtered = [item for item in filtered if item.created_at >= start_date]
        
        if end_date:
            filtered = [item for item in filtered if item.created_at <= end_date]
        
        return filtered
    
    def get_source_info(self) -> Dict[str, str]:
        """
        Get information about this scraper source.
        
        Returns:
            Dictionary with source information
        """
        return {
            'name': self.source_name,
            'type': self.source_type,
            'class': self.__class__.__name__,
        }
    
    def __repr__(self) -> str:
        """String representation of the scraper."""
        return f"{self.__class__.__name__}(source='{self.source_name}')"

