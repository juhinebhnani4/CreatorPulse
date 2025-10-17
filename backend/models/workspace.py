"""
Workspace models (request/response schemas).
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class CreateWorkspaceRequest(BaseModel):
    """Create workspace request."""
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = ""


class UpdateWorkspaceRequest(BaseModel):
    """Update workspace request."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class WorkspaceResponse(BaseModel):
    """Workspace response schema."""
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: datetime
    updated_at: datetime
    role: Optional[str] = None  # User's role in this workspace


class WorkspaceConfigRequest(BaseModel):
    """Update workspace config request."""
    config: Dict[str, Any]


class WorkspaceConfigResponse(BaseModel):
    """Workspace config response."""
    workspace_id: str
    config: Dict[str, Any]
    version: int
    updated_at: datetime
    updated_by: str
