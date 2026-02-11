"""
models.py — SQLAlchemy ORM Models for TlaquaNet
================================================
This module defines the database schema using SQLAlchemy ORM.

ANALYTICS DESIGN NOTES (important for data engineering students):
-----------------------------------------------------------------
1. Every transactional table has a 'created_at' timestamp.
   This makes it trivial to build time-series analytics.

2. The 'events' table is an append-only EVENT LOG that records
   every significant action. This is the foundation for:
   - Building FACT TABLES in a data warehouse
   - Event sourcing patterns
   - Real-time analytics pipelines (e.g., Kafka consumers)

3. The event types tracked are:
   - post_created: When a user creates a new post
   - post_liked: When a user likes a post
   - comment_created: When a user comments on a post
   - user_created: When a new user registers

4. Think of 'events' as a raw log. In a real data warehouse,
   you would ETL this into dimensional models (star schema).
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """
    Dimension: Users
    ----------------
    Represents a user profile in TlaquaNet.
    No authentication required — just a username and display name.
    
    In a star schema, this would be a DIMENSION TABLE (dim_users).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships (for ORM convenience, not stored in DB)
    posts = relationship("Post", back_populates="author")
    likes = relationship("Like", back_populates="user")
    comments = relationship("Comment", back_populates="author")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Post(Base):
    """
    Fact/Transaction: Posts
    -----------------------
    Each row represents a post creation event.
    The 'created_at' column is critical for time-based analytics.
    
    In a star schema, posts can be both:
    - A FACT TABLE (fact_posts) with metrics like like_count
    - A DIMENSION for comments and likes
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True  # Indexed for time-range queries!
    )

    # Relationships
    author = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post(id={self.id}, author_id={self.author_id})>"


class Like(Base):
    """
    Fact/Transaction: Likes
    -----------------------
    Records each like event. The unique constraint prevents
    a user from liking the same post twice.
    
    'created_at' enables analytics like:
    - Likes per hour/day
    - Time between post creation and first like
    - User engagement patterns
    """
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Prevent duplicate likes
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_user_post_like"),
    )

    # Relationships
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

    def __repr__(self):
        return f"<Like(user_id={self.user_id}, post_id={self.post_id})>"


class Comment(Base):
    """
    Fact/Transaction: Comments
    --------------------------
    Each comment is a timestamped event tied to a user and a post.
    
    Analytics possibilities:
    - Comments per post (engagement metric)
    - Average time to first comment
    - Most active commenters
    """
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id})>"


class Event(Base):
    """
    EVENT LOG TABLE — The heart of the analytics design
    ======================================================
    This is an APPEND-ONLY log of all significant actions.
    
    Why this matters for data engineering:
    1. It's a denormalized record of "what happened, when, and by whom"
    2. It can be consumed by:
       - Batch ETL pipelines (e.g., Airflow → dbt → BigQuery)
       - Stream processors (e.g., Debezium CDC → Kafka → Flink)
       - Simple SQL analytics queries
    3. It follows the EVENT SOURCING pattern:
       You can reconstruct the state of the system from events alone.
    
    Event types:
    - 'user_created'    → A new user registered
    - 'post_created'    → A user created a post
    - 'post_liked'      → A user liked a post
    - 'comment_created' → A user commented on a post
    
    The 'event_metadata' column stores JSON-like context (as text for simplicity).
    In production, you'd use JSONB for efficient querying.
    
    NOTE: We use 'event_metadata' as the Python attribute name because
    'metadata' is RESERVED by SQLAlchemy's Declarative API.
    The DB column is still named 'metadata' via the first Column argument.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    target_id = Column(Integer, nullable=True)  # post_id or comment_id
    event_metadata = Column("metadata", Text, nullable=True)  # Extra context as JSON string
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True  # Critical for time-range queries!
    )

    def __repr__(self):
        return f"<Event(type='{self.event_type}', user={self.user_id})>"
