"""
Pydantic models for subscriber and delivery endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========================================
# SUBSCRIBER MODELS
# ========================================

class SubscriberCreate(BaseModel):
    """Request model for creating a subscriber."""
    workspace_id: str = Field(..., description="Workspace ID (UUID format)")
    email: EmailStr = Field(..., description="Subscriber email address")
    name: Optional[str] = Field(None, description="Subscriber name")
    source: str = Field(default="manual", description="How subscriber was added (manual, api, import)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the subscriber")

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "1839de43-ebf1-4cc0-bcb4-3f7a2cb37a7b",
                "email": "subscriber@example.com",
                "name": "John Doe",
                "source": "manual",
                "metadata": {"subscription_type": "premium"}
            }
        }


class SubscriberBulkCreate(BaseModel):
    """Request model for bulk subscriber creation."""
    workspace_id: str = Field(..., description="Workspace ID (UUID format)")
    subscribers: List[Dict[str, Any]] = Field(..., description="List of subscriber data (email, name, metadata)")

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "1839de43-ebf1-4cc0-bcb4-3f7a2cb37a7b",
                "subscribers": [
                    {
                        "email": "user1@example.com",
                        "name": "Alice Smith",
                        "metadata": {"source": "import", "campaign": "winter2024"}
                    },
                    {
                        "email": "user2@example.com",
                        "name": "Bob Johnson",
                        "metadata": {"source": "import", "campaign": "winter2024"}
                    }
                ]
            }
        }


class SubscriberUpdate(BaseModel):
    """Request model for updating a subscriber."""
    name: Optional[str] = None
    status: Optional[str] = Field(None, description="Subscriber status: active, unsubscribed, bounced")
    metadata: Optional[Dict[str, Any]] = None


class SubscriberResponse(BaseModel):
    """Response model for a subscriber."""
    id: str
    workspace_id: str
    email: str
    name: Optional[str]
    status: str
    source: Optional[str]
    subscribed_at: datetime
    unsubscribed_at: Optional[datetime]
    last_sent_at: Optional[datetime]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class SubscriberListResponse(BaseModel):
    """Response model for list of subscribers."""
    subscribers: List[SubscriberResponse]
    count: int
    workspace_id: str


class SubscriberStatsResponse(BaseModel):
    """Response model for subscriber statistics."""
    workspace_id: str
    total_subscribers: int
    active_subscribers: int
    unsubscribed: int
    bounced: int


# ========================================
# DELIVERY MODELS
# ========================================

class DeliveryRequest(BaseModel):
    """Request model for sending a newsletter."""
    newsletter_id: str = Field(..., description="Newsletter ID to send (UUID format)")
    workspace_id: str = Field(..., description="Workspace ID (UUID format)")
    test_email: Optional[EmailStr] = Field(None, description="Send to test email instead of all subscribers")

    class Config:
        json_schema_extra = {
            "example": {
                "newsletter_id": "a8b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6",
                "workspace_id": "1839de43-ebf1-4cc0-bcb4-3f7a2cb37a7b",
                "test_email": "test@example.com"
            }
        }


class DeliveryResponse(BaseModel):
    """Response model for a delivery."""
    id: str
    newsletter_id: str
    workspace_id: str
    total_subscribers: int
    sent_count: int
    failed_count: int
    status: str  # pending, sending, completed, failed
    started_at: datetime
    completed_at: Optional[datetime]
    errors: List[str]
    created_at: datetime


class DeliveryListResponse(BaseModel):
    """Response model for list of deliveries."""
    deliveries: List[DeliveryResponse]
    count: int
    workspace_id: str
