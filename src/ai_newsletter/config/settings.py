"""
Settings and configuration management.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass


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
class YouTubeConfig(ScraperConfig):
    """YouTube-specific configuration."""
    api_key: Optional[str] = None
    channel_ids: list = field(default_factory=list)
    channel_usernames: list = field(default_factory=list)
    playlist_ids: list = field(default_factory=list)
    search_queries: list = field(default_factory=list)
    order: str = "date"
    max_results_per_request: int = 50


@dataclass
class NewsletterConfig:
    """Newsletter generation configuration."""
    openai_api_key: Optional[str] = None
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 2000
    template: str = "default"
    language: str = "en"
    tone: str = "professional"
    # OpenRouter configuration
    use_openrouter: bool = False
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "anthropic/claude-3.5-sonnet"


@dataclass
class EmailConfig:
    """Email delivery configuration."""
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    use_tls: bool = True
    from_email: Optional[str] = None
    from_name: str = "CreatorPulse"
    sendgrid_api_key: Optional[str] = None
    use_sendgrid: bool = False


@dataclass
class SchedulerConfig:
    """Scheduler configuration."""
    enabled: bool = True
    time: str = "08:00"
    timezone: str = "UTC"
    max_retries: int = 3
    retry_delay: int = 300  # seconds


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
    youtube: YouTubeConfig = field(default_factory=YouTubeConfig)
    
    # CreatorPulse configurations
    newsletter: NewsletterConfig = field(default_factory=NewsletterConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    
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
            if 'youtube' in data:
                data['youtube'] = YouTubeConfig(**data['youtube'])
            if 'newsletter' in data:
                data['newsletter'] = NewsletterConfig(**data['newsletter'])
            if 'email' in data:
                data['email'] = EmailConfig(**data['email'])
            if 'scheduler' in data:
                data['scheduler'] = SchedulerConfig(**data['scheduler'])
            
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
        
        # YouTube API credentials from env
        settings.youtube.api_key = os.getenv('YOUTUBE_API_KEY')
        
        # Newsletter configuration from env
        settings.newsletter.openai_api_key = os.getenv('OPENAI_API_KEY')
        settings.newsletter.model = os.getenv('NEWSLETTER_MODEL', 'gpt-4-turbo-preview')
        settings.newsletter.temperature = float(os.getenv('NEWSLETTER_TEMPERATURE', '0.7'))
        settings.newsletter.max_tokens = int(os.getenv('NEWSLETTER_MAX_TOKENS', '2000'))

        # OpenRouter configuration from env
        settings.newsletter.use_openrouter = os.getenv('USE_OPENROUTER', 'false').lower() == 'true'
        settings.newsletter.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        settings.newsletter.openrouter_model = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
        
        # Email configuration from env
        settings.email.smtp_server = os.getenv('SMTP_SERVER')
        settings.email.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        settings.email.smtp_username = os.getenv('SMTP_USERNAME')
        settings.email.smtp_password = os.getenv('SMTP_PASSWORD')
        settings.email.from_email = os.getenv('FROM_EMAIL')
        settings.email.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        settings.email.use_sendgrid = os.getenv('USE_SENDGRID', 'false').lower() == 'true'
        
        # Scheduler configuration from env
        settings.scheduler.enabled = os.getenv('SCHEDULER_ENABLED', 'true').lower() == 'true'
        settings.scheduler.time = os.getenv('SCHEDULER_TIME', '08:00')
        settings.scheduler.timezone = os.getenv('SCHEDULER_TIMEZONE', 'UTC')
        
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
    Environment variables take priority over file settings.
    
    Args:
        config_path: Optional path to config file
        use_env: Whether to load from environment variables
        
    Returns:
        Settings instance
    """
    global _settings
    
    if _settings is None:
        # Always start with environment variables if use_env=True
        if use_env:
            _settings = Settings.from_env()
        else:
            _settings = Settings()
        
        # Then override with file settings if config file exists
        if config_path and os.path.exists(config_path):
            file_settings = Settings.from_file(config_path)
            # Merge file settings with env settings (env takes priority)
            for field_name, field_value in asdict(file_settings).items():
                if hasattr(_settings, field_name):
                    env_value = getattr(_settings, field_name)
                    
                    # For nested config objects, merge at field level
                    if hasattr(env_value, '__dataclass_fields__'):
                        # This is a dataclass config object - merge individual fields
                        for sub_field in env_value.__dataclass_fields__:
                            env_sub_value = getattr(env_value, sub_field)
                            file_sub_value = getattr(field_value, sub_field, None)
                            
                            # Only use file value if env value is None or empty string
                            if env_sub_value is None or (isinstance(env_sub_value, str) and not env_sub_value):
                                if file_sub_value is not None:
                                    setattr(env_value, sub_field, file_sub_value)
                    else:
                        # Simple field - only overwrite if env value is None/empty
                        if env_value is None or (isinstance(env_value, str) and not env_value):
                            setattr(_settings, field_name, field_value)
    
    return _settings


def reset_settings():
    """Reset the global settings instance."""
    global _settings
    _settings = None

