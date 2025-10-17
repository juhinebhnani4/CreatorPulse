"""
Authentication models (request/response schemas).
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class SignupRequest(BaseModel):
    """Signup request schema."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    username: str = Field(min_length=3, max_length=50)


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Authentication response schema."""
    user_id: str
    email: str
    username: str
    token: str
    expires_at: datetime


class UserResponse(BaseModel):
    """User information response."""
    user_id: str
    email: str
    username: str
    created_at: datetime
