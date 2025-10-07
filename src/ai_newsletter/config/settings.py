"""
Settings and configuration management.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ScraperConfig:
    """Configuration for a specific scraper."""
    enabled: bool = True
    limit: int = 25
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RedditConfig(ScraperConfig):
    """Reddit-specific configuration."""
    subreddits: list = field(default_factory=lambda: ["AI_Agents"])
    sort: str = "hot"
    time_filter: str = "all"


@dataclass
class RSSConfig(ScraperConfig):
    """RSS-specific configuration."""
    feed_urls: list = field(default_factory=list)


@dataclass
class BlogConfig(ScraperConfig):
    """Blog-specific configuration."""
    urls: list = field(default_factory=list)
    template: str = "wordpress"


@dataclass
class XConfig(ScraperConfig):
    """X (Twitter)-specific configuration."""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    bearer_token: Optional[str] = None
    queries: list = field(default_factory=list)


@dataclass
class Settings:
    """
    Application settings.
    
    Settings can be loaded from:
    1. Environment variables (highest priority)
    2. config.json file
    3. Default values (lowest priority)
    """
    
    # General settings
    app_name: str = "AI Newsletter Scraper"
    debug: bool = False
    log_level: str = "INFO"
    
    # Scraper configurations
    reddit: RedditConfig = field(default_factory=RedditConfig)
    rss: RSSConfig = field(default_factory=RSSConfig)
    blog: BlogConfig = field(default_factory=BlogConfig)
    x: XConfig = field(default_factory=XConfig)
    
    # Data settings
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Settings':
        """
        Load settings from a JSON config file.
        
        Args:
            config_path: Path to config.json file
            
        Returns:
            Settings instance
        """
        path = Path(config_path)
        
        if not path.exists():
            return cls()
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Parse nested configs
            if 'reddit' in data:
                data['reddit'] = RedditConfig(**data['reddit'])
            if 'rss' in data:
                data['rss'] = RSSConfig(**data['rss'])
            if 'blog' in data:
                data['blog'] = BlogConfig(**data['blog'])
            if 'x' in data:
                data['x'] = XConfig(**data['x'])
            
            return cls(**data)
            
        except Exception as e:
            print(f"Error loading config file: {e}")
            return cls()
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """
        Load settings from environment variables.
        
        Returns:
            Settings instance
        """
        settings = cls()
        
        # General settings
        settings.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        settings.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # X API credentials from env
        settings.x.api_key = os.getenv('X_API_KEY')
        settings.x.api_secret = os.getenv('X_API_SECRET')
        settings.x.access_token = os.getenv('X_ACCESS_TOKEN')
        settings.x.access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')
        settings.x.bearer_token = os.getenv('X_BEARER_TOKEN')
        
        return settings
    
    def to_file(self, config_path: str):
        """
        Save settings to a JSON config file.
        
        Args:
            config_path: Path to save config.json
        """
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = asdict(self)
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_scraper_config(self, scraper_name: str) -> Optional[ScraperConfig]:
        """
        Get configuration for a specific scraper.
        
        Args:
            scraper_name: Name of the scraper ('reddit', 'rss', etc.)
            
        Returns:
            ScraperConfig instance or None
        """
        return getattr(self, scraper_name, None)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings(config_path: Optional[str] = None, use_env: bool = True) -> Settings:
    """
    Get application settings.
    
    This function implements a singleton pattern for settings.
    
    Args:
        config_path: Optional path to config file
        use_env: Whether to load from environment variables
        
    Returns:
        Settings instance
    """
    global _settings
    
    if _settings is None:
        if config_path and os.path.exists(config_path):
            _settings = Settings.from_file(config_path)
        elif use_env:
            _settings = Settings.from_env()
        else:
            _settings = Settings()
    
    return _settings


def reset_settings():
    """Reset the global settings instance."""
    global _settings
    _settings = None

