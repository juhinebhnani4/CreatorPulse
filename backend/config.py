"""
Configuration management for CreatorPulse Backend.
Uses pydantic-settings for environment variable management.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(
        # Look for .env in project root (parent of backend directory)
        env_file=str(Path(__file__).parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "CreatorPulse API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"  # development, production

    # API
    api_v1_prefix: str = "/api/v1"

    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:8501",  # Streamlit default
        "http://localhost:3000",  # Next.js default
        "http://localhost:3001",  # Next.js (alternate port)
        "http://localhost:3002",  # Next.js (alternate port)
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ]

    # Supabase
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_key: Optional[str] = None

    # OpenAI / OpenRouter
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    use_openrouter: bool = False
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    openai_model: str = "gpt-4-turbo-preview"

    # Email
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    use_sendgrid: bool = False

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

    # Railway (auto-detected)
    railway_public_domain: Optional[str] = None
    railway_environment: Optional[str] = None

    @property
    def backend_url(self) -> str:
        """Get backend URL (Railway or localhost)."""
        if self.railway_public_domain:
            return f"https://{self.railway_public_domain}"
        return "http://localhost:8000"


# Global settings instance
settings = Settings()
