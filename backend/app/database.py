"""
database.py — Database configuration for TlaquaNet
===================================================
This module sets up the SQLAlchemy engine, session factory, and Base class.

Key concepts for data engineering students:
- We use a sessionmaker to create database sessions on demand.
- The 'get_db' dependency ensures each request gets its own session
  and that the session is properly closed after the request.
- DATABASE_URL follows the standard format:
  postgresql://user:password@host:port/dbname
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file (for local development)
load_dotenv()

# --------------------------------------------------------------------------
# DATABASE_URL: Connection string for PostgreSQL
# For local dev: postgresql://postgres:postgres@localhost:5432/tlaquanet
# For production: Set this environment variable in your hosting service
# --------------------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/tlaquanet"
)

# Some hosting services (like Render) provide URLs starting with
# "postgres://" instead of "postgresql://". SQLAlchemy requires the latter.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --------------------------------------------------------------------------
# Engine: The core interface to the database.
# - pool_pre_ping=True: Tests connections before using them (resilience)
# - echo=False: Set to True to see all SQL queries in the console (debugging)
# --------------------------------------------------------------------------
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

# --------------------------------------------------------------------------
# SessionLocal: Factory for creating new database sessions.
# - autocommit=False: We control when to commit transactions
# - autoflush=False: We control when to flush changes to the DB
# --------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --------------------------------------------------------------------------
# Base: All ORM models will inherit from this class.
# It provides the mapping between Python classes and database tables.
# --------------------------------------------------------------------------
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session to each request.
    
    Usage in FastAPI:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    
    The 'yield' keyword makes this a generator-based dependency:
    - Code before yield runs BEFORE the request handler
    - Code after yield runs AFTER the request handler (cleanup)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
