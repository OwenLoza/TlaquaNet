"""
routers/users.py — User management endpoints
=============================================
Handles user creation and listing.

Every user action is also logged to the 'events' table
for analytics purposes (event sourcing pattern).
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Event
from ..schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(
    prefix="/api/users",
    tags=["users"],  # Groups endpoints in Swagger docs
)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user profile",
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user profile.
    
    - **username**: Must be unique (3-50 characters)
    - **display_name**: The name shown in the UI
    
    Also logs a 'user_created' event to the events table.
    """
    # Check if username already exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.username}' already taken"
        )

    # Create the user
    db_user = User(username=user.username, display_name=user.display_name)
    db.add(db_user)
    db.flush()  # Flush to get the generated ID before committing

    # ── Analytics: Log the event ──────────────────────────────────
    event = Event(
        event_type="user_created",
        user_id=db_user.id,
        target_id=db_user.id,
        event_metadata=json.dumps({
            "username": user.username,
            "display_name": user.display_name,
        }),
    )
    db.add(event)
    # ──────────────────────────────────────────────────────────────

    db.commit()
    db.refresh(db_user)
    return db_user


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List all users",
)
def list_users(db: Session = Depends(get_db)):
    """
    Returns all registered users, ordered by creation date (newest first).
    
    In a production system, you'd add pagination here.
    For didactic purposes, we return all users.
    """
    return (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a single user by ID",
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a single user by their ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user's display name",
)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user's display name.
    
    - **display_name**: The new name to show in the UI
    
    Also logs a 'user_updated' event to the events table.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    old_display_name = db_user.display_name
    db_user.display_name = user_update.display_name

    # ── Analytics: Log the event ──────────────────────────────────
    event = Event(
        event_type="user_updated",
        user_id=db_user.id,
        target_id=db_user.id,
        event_metadata=json.dumps({
            "old_display_name": old_display_name,
            "new_display_name": user_update.display_name,
        }),
    )
    db.add(event)
    # ──────────────────────────────────────────────────────────────

    db.commit()
    db.refresh(db_user)
    return db_user
