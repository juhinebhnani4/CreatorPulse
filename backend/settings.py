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
    # CRITICAL: secret_key MUST be set via SECRET_KEY environment variable
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    secret_key: str  # No default - must be provided via environment
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

    # AI Providers (Anthropic/Claude, OpenAI, OpenRouter)
    # Anthropic (Claude) - PRIMARY
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    anthropic_max_tokens: int = 4096

    # OpenAI - DISABLED (using Claude)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"

    # OpenRouter - PRIMARY (for Claude access)
    openrouter_api_key: Optional[str] = None
    use_openrouter: bool = False
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    openrouter_max_tokens: int = 4096

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

    def validate_required_settings(self) -> None:
        """Validate that all critical settings are properly configured."""
        errors = []

        # Critical security settings
        if not self.secret_key:
            errors.append("SECRET_KEY environment variable is required")
        elif self.secret_key == "your-secret-key-change-this-in-production":
            errors.append("SECRET_KEY must be changed from default value")
        elif len(self.secret_key) < 32:
            errors.append("SECRET_KEY must be at least 32 characters long")

        # Critical database settings
        if not self.supabase_url:
            errors.append("SUPABASE_URL environment variable is required")
        if not self.supabase_key:
            errors.append("SUPABASE_KEY environment variable is required")

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)


# Global settings instance
settings = Settings()

# Validate settings on import (will fail fast if misconfigured)
try:
    settings.validate_required_settings()
except ValueError as e:
    # In development, warn but don't crash
    if settings.environment == "development":
        print(f"WARNING: {e}")
        print("This is acceptable in development but MUST be fixed for production")
    else:
        # In production, crash immediately
        raise
