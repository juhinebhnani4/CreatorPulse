"""
Scraper registry for managing and discovering available scrapers.
"""

from typing import Dict, Type, List, Optional
import importlib
import inspect

from ..scrapers.base import BaseScraper


class ScraperRegistry:
    """
    Registry for managing available scrapers.
    
    This class provides a central place to register and discover scrapers,
    making it easy to add new scrapers without modifying existing code.
    
    Example:
        # Get all available scrapers
        registry = ScraperRegistry()
        scrapers = registry.get_all_scrapers()
        
        # Get a specific scraper
        reddit_scraper = registry.get_scraper('reddit')()
    """
    
    _scrapers: Dict[str, Type[BaseScraper]] = {}
    
    @classmethod
    def register(cls, name: str, scraper_class: Type[BaseScraper]):
        """
        Register a scraper class.
        
        Args:
            name: Unique identifier for the scraper
            scraper_class: Scraper class (must inherit from BaseScraper)
        """
        if not issubclass(scraper_class, BaseScraper):
            raise ValueError(f"{scraper_class} must inherit from BaseScraper")
        
        cls._scrapers[name] = scraper_class
    
    @classmethod
    def get_scraper(cls, name: str) -> Optional[Type[BaseScraper]]:
        """
        Get a scraper class by name.
        
        Args:
            name: Scraper identifier
            
        Returns:
            Scraper class or None if not found
        """
        return cls._scrapers.get(name)
    
    @classmethod
    def get_all_scrapers(cls) -> Dict[str, Type[BaseScraper]]:
        """
        Get all registered scrapers.
        
        Returns:
            Dictionary mapping scraper names to classes
        """
        return cls._scrapers.copy()
    
    @classmethod
    def list_scrapers(cls) -> List[str]:
        """
        List all registered scraper names.
        
        Returns:
            List of scraper names
        """
        return list(cls._scrapers.keys())
    
    @classmethod
    def auto_discover(cls):
        """
        Automatically discover and register scrapers from the scrapers package.
        """
        from .. import scrapers
        
        # Get all classes from the scrapers module
        for name, obj in inspect.getmembers(scrapers):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseScraper) and 
                obj is not BaseScraper):
                # Register using lowercase source_name if available
                scraper_name = name.replace('Scraper', '').lower()
                cls.register(scraper_name, obj)


# Auto-discover scrapers on import
ScraperRegistry.auto_discover()

