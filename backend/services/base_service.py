"""
Base service class for standardized service implementation.

Provides common functionality for all services including:
- Database connection management
- Error handling
- Logging
"""

from typing import Optional
import logging

from src.ai_newsletter.database.supabase_client import SupabaseManager


class BaseService:
    """
    Base class for all backend services.

    Provides standardized database connection management using dependency injection.
    All services should inherit from this class.

    Example:
        class MyService(BaseService):
            async def my_method(self):
                # Access database via self.db
                data = self.db.get_workspace(workspace_id)
    """

    def __init__(self, db: Optional[SupabaseManager] = None):
        """
        Initialize base service.

        Args:
            db: Optional SupabaseManager instance for dependency injection.
                If not provided, creates a new instance.
        """
        self._db = db
        self._logger = self._setup_logger()

    @property
    def db(self) -> SupabaseManager:
        """
        Get database manager instance.

        Uses lazy loading if not provided during initialization.

        Returns:
            SupabaseManager instance
        """
        if self._db is None:
            self._db = SupabaseManager()
        return self._db

    @property
    def logger(self) -> logging.Logger:
        """
        Get service logger instance.

        Returns:
            Logger configured for this service
        """
        return self._logger

    def _setup_logger(self) -> logging.Logger:
        """
        Set up logger for this service.

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

        # Only add handler if not already configured
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger
