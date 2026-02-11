"""
routers/posts.py — Post, Like, and Comment endpoints
=====================================================
Handles the core social network interactions:
- Creating posts
- Listing posts (the "feed")
- Liking and unliking posts
- Commenting on posts

Every action is logged to the 'events' table for analytics.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Post, Like, Comment, User, Event
from ..schemas import (
    PostCreate, PostResponse,
    LikeCreate, LikeResponse,
    CommentCreate, CommentResponse,
)

router = APIRouter(
    prefix="/api/posts",
    tags=["posts"],
)


# --------------------------------------------------------------------------
# POSTS
# --------------------------------------------------------------------------

@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """
    Create a new text post.
    
    - **content**: The post text (1-500 characters)
    - **author_id**: ID of the user creating the post
    
    Logs a 'post_created' event for analytics.
    """
    # Verify the author exists
    author = db.query(User).filter(User.id == post.author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {post.author_id} not found"
        )

    # Create the post
    db_post = Post(content=post.content, author_id=post.author_id)
    db.add(db_post)
    db.flush()

    # ── Analytics: Log the event ──────────────────────────────────
    event = Event(
        event_type="post_created",
        user_id=post.author_id,
        target_id=db_post.id,
        event_metadata=json.dumps({
            "content_length": len(post.content),
            "preview": post.content[:100],
        }),
    )
    db.add(event)
    # ──────────────────────────────────────────────────────────────

    db.commit()
    db.refresh(db_post)

    return _build_post_response(db_post)


@router.get(
    "/",
    response_model=list[PostResponse],
    summary="List all posts (feed)",
)
def list_posts(
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max posts to return"),
    db: Session = Depends(get_db),
):
    """
    Returns the post feed, ordered by newest first.
    
    Includes:
    - Author information
    - Like count and list of user IDs who liked
    - Comment count and list of comments
    
    Supports basic pagination with skip/limit parameters.
    """
    posts = (
        db.query(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.likes),
            joinedload(Post.comments).joinedload(Comment.author),
        )
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .distinct()
        .all()
    )

    return [_build_post_response(p) for p in posts]


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get a single post by ID",
)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Retrieve a single post with all its likes and comments."""
    post = (
        db.query(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.likes),
            joinedload(Post.comments).joinedload(Comment.author),
        )
        .filter(Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found"
        )
    return _build_post_response(post)


# --------------------------------------------------------------------------
# LIKES
# --------------------------------------------------------------------------

@router.post(
    "/{post_id}/like",
    response_model=LikeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Like a post",
)
def like_post(post_id: int, like: LikeCreate, db: Session = Depends(get_db)):
    """
    Like a post. A user can only like a post once.
    
    Logs a 'post_liked' event for analytics.
    """
    # Verify post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found"
        )

    # Verify user exists
    user = db.query(User).filter(User.id == like.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {like.user_id} not found"
        )

    # Check for duplicate like
    existing_like = (
        db.query(Like)
        .filter(Like.user_id == like.user_id, Like.post_id == post_id)
        .first()
    )
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already liked this post"
        )

    # Create the like
    db_like = Like(user_id=like.user_id, post_id=post_id)
    db.add(db_like)
    db.flush()

    # ── Analytics: Log the event ──────────────────────────────────
    event = Event(
        event_type="post_liked",
        user_id=like.user_id,
        target_id=post_id,
        event_metadata=json.dumps({
            "post_author_id": post.author_id,
        }),
    )
    db.add(event)
    # ──────────────────────────────────────────────────────────────

    db.commit()
    db.refresh(db_like)
    return db_like


@router.delete(
    "/{post_id}/like/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlike a post",
)
def unlike_post(post_id: int, user_id: int, db: Session = Depends(get_db)):
    """Remove a like from a post."""
    like = (
        db.query(Like)
        .filter(Like.user_id == user_id, Like.post_id == post_id)
        .first()
    )
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )
    db.delete(like)
    db.commit()


# --------------------------------------------------------------------------
# COMMENTS
# --------------------------------------------------------------------------

@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Comment on a post",
)
def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
):
    """
    Add a comment to a post.
    
    Logs a 'comment_created' event for analytics.
    """
    # Verify post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found"
        )

    # Verify user exists
    user = db.query(User).filter(User.id == comment.author_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {comment.author_id} not found"
        )

    # Create the comment
    db_comment = Comment(
        content=comment.content,
        author_id=comment.author_id,
        post_id=post_id,
    )
    db.add(db_comment)
    db.flush()

    # ── Analytics: Log the event ──────────────────────────────────
    event = Event(
        event_type="comment_created",
        user_id=comment.author_id,
        target_id=post_id,
        event_metadata=json.dumps({
            "comment_id": db_comment.id,
            "post_author_id": post.author_id,
            "content_length": len(comment.content),
        }),
    )
    db.add(event)
    # ──────────────────────────────────────────────────────────────

    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.get(
    "/{post_id}/comments",
    response_model=list[CommentResponse],
    summary="List comments for a post",
)
def list_comments(post_id: int, db: Session = Depends(get_db)):
    """Returns all comments for a specific post, oldest first."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found"
        )
    return (
        db.query(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )


# --------------------------------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------------------------------

def _build_post_response(post: Post) -> PostResponse:
    """
    Constructs a PostResponse from a Post ORM object.
    
    This manually maps ORM relationships to the Pydantic response
    schema, including computed fields like like_count.
    """
    return PostResponse(
        id=post.id,
        content=post.content,
        author_id=post.author_id,
        author=post.author,
        created_at=post.created_at,
        like_count=len(post.likes),
        comment_count=len(post.comments),
        liked_by=[like.user_id for like in post.likes],
        comments=post.comments,
    )
