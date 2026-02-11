-- ============================================================
-- TlaquaNet — SQL Schema
-- ============================================================
-- This file creates the complete database schema.
-- Run it manually if you don't want SQLAlchemy to auto-create tables.
--
-- Usage:
--   psql -U postgres -d tlaquanet -f schema.sql
--
-- ANALYTICS DESIGN NOTES:
-- ────────────────────────
-- 1. All tables have 'created_at' with timezone for time-series queries
-- 2. The 'events' table is the CENTRAL FACT TABLE for analytics
-- 3. Users, Posts are DIMENSION TABLES in a star schema
-- 4. Likes and Comments are TRANSACTIONAL FACT TABLES
-- ============================================================

-- Create the database (run this separately if needed)
-- CREATE DATABASE tlaquanet;

-- ────────────────────────────────────────────────────────────
-- DIMENSION: Users
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) NOT NULL UNIQUE,
    display_name  VARCHAR(100) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for quick username lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ────────────────────────────────────────────────────────────
-- FACT: Posts
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS posts (
    id          SERIAL PRIMARY KEY,
    content     TEXT NOT NULL,
    author_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_posts_author_id ON posts(author_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);

-- ────────────────────────────────────────────────────────────
-- FACT: Likes
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS likes (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id     INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- A user can only like a post once
    CONSTRAINT uq_user_post_like UNIQUE (user_id, post_id)
);

CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);
CREATE INDEX IF NOT EXISTS idx_likes_post_id ON likes(post_id);

-- ────────────────────────────────────────────────────────────
-- FACT: Comments
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comments (
    id          SERIAL PRIMARY KEY,
    content     TEXT NOT NULL,
    author_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id     INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comments_author_id ON comments(author_id);
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);

-- ────────────────────────────────────────────────────────────
-- 📊 CENTRAL FACT TABLE: Events (Event Log)
-- ────────────────────────────────────────────────────────────
-- This is the MOST IMPORTANT table for data engineering.
-- It records every significant action as an append-only log.
--
-- Event types:
--   • user_created    → A new user registered
--   • post_created    → A user created a post
--   • post_liked      → A user liked a post
--   • comment_created → A user commented on a post
--
-- In a data warehouse, you would:
--   1. Extract this table via CDC or batch queries
--   2. Load it into your warehouse (BigQuery, Snowflake)
--   3. Transform it with dbt into dimensional models
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS events (
    id          SERIAL PRIMARY KEY,
    event_type  VARCHAR(50) NOT NULL,
    user_id     INTEGER NOT NULL,
    target_id   INTEGER,          -- ID of the affected entity (post, comment)
    metadata    TEXT,             -- JSON string with extra context
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC);

-- ────────────────────────────────────────────────────────────
-- 📊 EXAMPLE ANALYTICS QUERIES
-- ────────────────────────────────────────────────────────────

-- 1. Events per day (activity timeline)
-- SELECT
--     DATE(created_at) AS event_date,
--     event_type,
--     COUNT(*) AS event_count
-- FROM events
-- GROUP BY DATE(created_at), event_type
-- ORDER BY event_date DESC;

-- 2. Most active users
-- SELECT
--     u.username,
--     u.display_name,
--     COUNT(e.id) AS total_actions
-- FROM events e
-- JOIN users u ON u.id = e.user_id
-- GROUP BY u.id, u.username, u.display_name
-- ORDER BY total_actions DESC
-- LIMIT 10;

-- 3. Most liked posts
-- SELECT
--     p.id,
--     p.content,
--     u.username AS author,
--     COUNT(l.id) AS like_count
-- FROM posts p
-- JOIN users u ON u.id = p.author_id
-- LEFT JOIN likes l ON l.post_id = p.id
-- GROUP BY p.id, p.content, u.username
-- ORDER BY like_count DESC
-- LIMIT 10;

-- 4. Average time to first like (engagement speed)
-- SELECT
--     p.id AS post_id,
--     p.created_at AS post_time,
--     MIN(l.created_at) AS first_like_time,
--     MIN(l.created_at) - p.created_at AS time_to_first_like
-- FROM posts p
-- JOIN likes l ON l.post_id = p.id
-- GROUP BY p.id, p.created_at
-- ORDER BY time_to_first_like ASC;

-- 5. Hourly activity pattern
-- SELECT
--     EXTRACT(HOUR FROM created_at) AS hour_of_day,
--     event_type,
--     COUNT(*) AS event_count
-- FROM events
-- GROUP BY hour_of_day, event_type
-- ORDER BY hour_of_day;
