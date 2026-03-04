"""
schemas.py — Pydantic Schemas for TlaquaNet
============================================
Pydantic models define the shape of data for:
- Request bodies (what the client sends)
- Response bodies (what the API returns)

Key design principle: SEPARATE input schemas from output schemas.
- *Create schemas: What the client sends (no id, no timestamps)
- *Response schemas: What the API returns (includes id, timestamps)

This separation ensures:
1. Clients can't set their own IDs or timestamps
2. API responses are consistent and predictable
3. Validation is strict and explicit
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ==========================================================================
# USER SCHEMAS
# ==========================================================================

class UserCreate(BaseModel):
    """Schema for creating a new user. Only username and display_name needed."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (3-50 characters)"
    )
    display_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name shown in the UI"
    )


class UserUpdate(BaseModel):
    """Schema for updating user data."""
    display_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Updated display name"
    )


class UserResponse(BaseModel):
    """Schema for returning user data. Includes server-generated fields."""
    id: int
    username: str
    display_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ==========================================================================
# POST SCHEMAS
# ==========================================================================

class PostCreate(BaseModel):
    """Schema for creating a new post. Requires author_id and content."""
    content: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Post content (1-500 characters)"
    )
    author_id: int = Field(
        ...,
        description="ID of the user creating the post"
    )


class PostResponse(BaseModel):
    """
    Schema for returning post data.
    Includes computed fields like like_count and nested comments.
    """
    id: int
    content: str
    author_id: int
    author: Optional[UserResponse] = None
    created_at: datetime
    like_count: int = 0
    comment_count: int = 0
    comments: list["CommentResponse"] = []
    liked_by: list[int] = []  # List of user IDs who liked this post

    model_config = {"from_attributes": True}


# ==========================================================================
# LIKE SCHEMAS
# ==========================================================================

class LikeCreate(BaseModel):
    """Schema for liking a post. Just need the user_id."""
    user_id: int = Field(
        ...,
        description="ID of the user liking the post"
    )


class LikeResponse(BaseModel):
    """Schema for returning like data."""
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ==========================================================================
# COMMENT SCHEMAS
# ==========================================================================

class CommentCreate(BaseModel):
    """Schema for creating a comment on a post."""
    content: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Comment content (1-300 characters)"
    )
    author_id: int = Field(
        ...,
        description="ID of the user creating the comment"
    )


class CommentResponse(BaseModel):
    """Schema for returning comment data."""
    id: int
    content: str
    author_id: int
    post_id: int
    author: Optional[UserResponse] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ==========================================================================
# EVENT SCHEMAS (for the analytics endpoint)
# ==========================================================================

class EventResponse(BaseModel):
    """Schema for returning event log entries."""
    id: int
    event_type: str
    user_id: int
    target_id: Optional[int] = None
    event_metadata: Optional[str] = Field(None, alias="event_metadata")
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


# Rebuild models to resolve forward references (PostResponse ↔ CommentResponse)
PostResponse.model_rebuild()
