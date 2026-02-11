"""
routers/analytics.py — Analytics endpoints
==========================================
Exposes the event log for analytics queries.

In a real data engineering pipeline, this data would be:
1. Extracted via CDC (Change Data Capture) or batch queries
2. Loaded into a data warehouse (BigQuery, Snowflake, Redshift)
3. Transformed with dbt into dimensional models

For didactic purposes, we provide a simple REST endpoint
that returns the raw event log with optional filtering.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Event
from ..schemas import EventResponse

router = APIRouter(
    prefix="/api/analytics",
    tags=["analytics"],
)


@router.get(
    "/events",
    response_model=list[EventResponse],
    summary="Get the event log",
)
def get_events(
    event_type: str | None = Query(
        None,
        description="Filter by event type (e.g., 'post_created', 'post_liked')"
    ),
    user_id: int | None = Query(
        None,
        description="Filter by user ID"
    ),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Returns raw events from the event log.
    
    This is the data you'd use to build:
    - Fact tables (fact_events)
    - Activity dashboards
    - User engagement metrics
    
    Supports filtering by event_type and user_id.
    """
    query = db.query(Event)

    if event_type:
        query = query.filter(Event.event_type == event_type)
    if user_id:
        query = query.filter(Event.user_id == user_id)

    return (
        query
        .order_by(Event.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get(
    "/summary",
    summary="Get a summary of platform activity",
)
def get_summary(db: Session = Depends(get_db)):
    """
    Returns aggregate counts by event type.
    
    Example response:
    {
        "user_created": 10,
        "post_created": 25,
        "post_liked": 42,
        "comment_created": 18,
        "total_events": 95
    }
    
    This is equivalent to:
    SELECT event_type, COUNT(*) FROM events GROUP BY event_type;
    """
    results = (
        db.query(Event.event_type, func.count(Event.id))
        .group_by(Event.event_type)
        .all()
    )

    summary = {event_type: count for event_type, count in results}
    summary["total_events"] = sum(summary.values())
    return summary
