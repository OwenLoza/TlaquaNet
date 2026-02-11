"""
main.py — FastAPI Application Entry Point for TlaquaNet
=======================================================
This is the main file that:
1. Creates the FastAPI application
2. Configures CORS (Cross-Origin Resource Sharing)
3. Registers all routers
4. Creates database tables on startup

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import users, posts, analytics


# --------------------------------------------------------------------------
# Lifespan: Runs code on startup and shutdown
# --------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup: Create all database tables if they don't exist.
    
    This uses SQLAlchemy's create_all() which is safe to call
    multiple times — it only creates tables that don't exist yet.
    
    In production, you'd use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")
    yield
    print("Shutting down TlaquaNet")


# --------------------------------------------------------------------------
# FastAPI App
# --------------------------------------------------------------------------
app = FastAPI(
    title="TlaquaNet API",
    description=(
        "A didactic social network API for data engineering students. "
        "Designed to demonstrate event-driven architectures and "
        "analytics-ready database schemas."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# --------------------------------------------------------------------------
# CORS Configuration
# --------------------------------------------------------------------------
# Allow all origins for development. In production, restrict this
# to your frontend domain (e.g., https://tlaquanet.vercel.app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------
# Register Routers
# --------------------------------------------------------------------------
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(analytics.router)


# --------------------------------------------------------------------------
# Health Check
# --------------------------------------------------------------------------
@app.get("/", tags=["health"])
def health_check():
    """
    Health check endpoint.
    Returns a simple message confirming the API is running.
    Useful for monitoring tools and deployment health checks.
    """
    return {
        "status": "healthy",
        "app": "TlaquaNet",
        "version": "1.0.0",
        "docs": "/docs",
    }
