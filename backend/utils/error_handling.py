"""
Error handling utilities for consistent service error management.

Provides decorators and utilities for standardized error handling across
all backend services.
"""

from typing import Callable, Any, TypeVar, Optional
from functools import wraps
import logging
import asyncio

T = TypeVar('T')

# Configure logger
logger = logging.getLogger(__name__)


def handle_service_errors(
    default_return: Any = None,
    log_errors: bool = True,
    raise_on_error: bool = False
):
    """
    Decorator for consistent error handling in service methods.

    Usage:
        @handle_service_errors(default_return=[], raise_on_error=False)
        async def my_service_method(self):
            # Method implementation
            ...

    Args:
        default_return: Value to return on error (if not raising)
        log_errors: Whether to log errors to console
        raise_on_error: Whether to re-raise exceptions after logging

    Returns:
        Decorator function that wraps service methods
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            """Wrapper for async functions."""
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Error in {func.__module__}.{func.__qualname__}: {str(e)}",
                        exc_info=True,
                        extra={
                            'function': func.__name__,
                            'args': str(args)[:200],  # Limit arg logging
                            'kwargs': str(kwargs)[:200]
                        }
                    )

                if raise_on_error:
                    raise

                return default_return

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            """Wrapper for sync functions."""
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Error in {func.__module__}.{func.__qualname__}: {str(e)}",
                        exc_info=True,
                        extra={
                            'function': func.__name__,
                            'args': str(args)[:200],
                            'kwargs': str(kwargs)[:200]
                        }
                    )

                if raise_on_error:
                    raise

                return default_return

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class ServiceError(Exception):
    """Base exception for service-level errors."""
    pass


class DatabaseError(ServiceError):
    """Raised when database operations fail."""
    pass


class ValidationError(ServiceError):
    """Raised when input validation fails."""
    pass


class AuthenticationError(ServiceError):
    """Raised when authentication fails."""
    pass


class NotFoundError(ServiceError):
    """Raised when requested resource is not found."""
    pass


class RateLimitError(ServiceError):
    """Raised when rate limit is exceeded."""
    pass


def format_error_response(error: Exception) -> dict:
    """
    Format exception into standardized error response.

    Args:
        error: Exception to format

    Returns:
        Dictionary with error details
    """
    error_type = type(error).__name__
    error_message = str(error)

    return {
        'error': error_type,
        'message': error_message,
        'success': False
    }


def log_service_call(
    service_name: str,
    method_name: str,
    params: Optional[dict] = None
):
    """
    Log service method calls for debugging.

    Args:
        service_name: Name of the service
        method_name: Name of the method being called
        params: Optional parameters passed to method
    """
    params_str = str(params)[:200] if params else "None"
    logger.info(
        f"[{service_name}] Calling {method_name} with params: {params_str}"
    )
