"""
Standardized API response models.
Ensures consistent response format across all endpoints.
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail structure."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None

    @classmethod
    def success_response(cls, data: Any) -> "APIResponse":
        """Create a success response."""
        return cls(success=True, data=data, error=None)

    @classmethod
    def error_response(cls, code: str, message: str, details: Optional[Dict[str, Any]] = None) -> "APIResponse":
        """Create an error response."""
        return cls(
            success=False,
            data=None,
            error=ErrorDetail(code=code, message=message, details=details)
        )


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: list[Any]
    total: int
    page: int
    page_size: int
    has_more: bool

    @classmethod
    def create(cls, items: list[Any], total: int, page: int, page_size: int) -> "PaginatedResponse":
        """Create a paginated response."""
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(page * page_size) < total
        )
