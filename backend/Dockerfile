# ============================================================
# TlaquaNet Backend — Dockerfile
# ============================================================
# Multi-purpose Dockerfile for both local Docker and cloud deploy.
#
# Build:   docker build -t tlaquanet-api .
# Run:     docker run -p 8000:8000 -e DATABASE_URL=... tlaquanet-api
# ============================================================

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with gunicorn for production (uvicorn worker)
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "1"]
