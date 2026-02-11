# 🌊 TlaquaNet

> A didactic social network for **data engineering students**.  
> Designed to teach event-driven architectures, analytics-ready schemas, and full-stack development.

---

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Database Schema (Analytics Focus)](#-database-schema-analytics-focus)
- [Run Locally](#-run-locally)
- [Deploy for Free](#-deploy-for-free)
- [API Reference](#-api-reference)
- [Analytics Queries](#-analytics-queries)

---

## 🏗 Architecture

```
┌─────────────────┐     HTTP/JSON     ┌─────────────────┐     SQL     ┌──────────────┐
│                 │ ←───────────────→ │                 │ ←──────────→ │              │
│   React + Vite  │                   │  FastAPI (REST) │              │  PostgreSQL  │
│   (Frontend)    │                   │  (Backend)      │              │  (Database)  │
│                 │                   │                 │              │              │
└─────────────────┘                   └─────────────────┘              └──────────────┘
   Vercel / Netlify                    Render / Railway                  Neon / Supabase
```

### Project Structure

```
tlaquaNet/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app + CORS + lifespan
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   ├── models.py        # ORM models (User, Post, Like, Comment, Event)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   └── routers/
│   │       ├── users.py     # User CRUD endpoints
│   │       ├── posts.py     # Post, Like, Comment endpoints
│   │       └── analytics.py # Event log + summary endpoints
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx         # React entry point
│   │   ├── App.jsx          # Main app with tabs & state
│   │   ├── api.js           # API client
│   │   ├── index.css        # Design system (dark theme)
│   │   └── components/
│   │       ├── CreateUserForm.jsx
│   │       ├── CreatePostForm.jsx
│   │       ├── PostCard.jsx
│   │       ├── AnalyticsPanel.jsx
│   │       └── Toast.jsx
│   ├── vite.config.js
│   └── package.json
├── sql/
│   └── schema.sql           # Full DDL + example analytics queries
├── docker-compose.yml        # Local dev with PostgreSQL
└── README.md
```

---

## 🛠 Tech Stack

| Layer      | Technology         | Why                                      |
|------------|--------------------|------------------------------------------|
| Frontend   | React + Vite       | Fast dev server, easy to deploy static   |
| Backend    | FastAPI (Python)   | Modern, fast, auto-generates API docs    |
| ORM        | SQLAlchemy         | Industry standard, clear model mapping   |
| Database   | PostgreSQL         | The gold standard for analytics          |
| Validation | Pydantic           | Type-safe request/response schemas       |

---

## 📊 Database Schema (Analytics Focus)

### Entity Relationship Diagram

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│  users   │──1:N──│  posts   │──1:N──│ comments │
│          │       │          │       │          │
│ id (PK)  │       │ id (PK)  │       │ id (PK)  │
│ username │       │ content  │       │ content  │
│ display  │       │ author_id│◄──FK──│ author_id│
│ created  │       │ created  │       │ post_id  │
└──────────┘       └──────────┘       │ created  │
      │                  │            └──────────┘
      │            ┌──────────┐
      └────1:N─────│  likes   │
                   │          │
                   │ id (PK)  │
                   │ user_id  │
                   │ post_id  │
                   │ created  │ ← UNIQUE(user_id, post_id)
                   └──────────┘

┌──────────────────────────────────┐
│  📊 events (CENTRAL FACT TABLE) │
│                                  │
│  id         SERIAL PK            │
│  event_type VARCHAR(50)          │  ← 'user_created', 'post_created',
│  user_id    INTEGER              │     'post_liked', 'comment_created'
│  target_id  INTEGER              │  ← ID of affected entity
│  metadata   TEXT (JSON)          │  ← Extra context
│  created_at TIMESTAMPTZ          │  ← Critical for time-series!
└──────────────────────────────────┘
```

### Why this design matters

1. **Every table has `created_at`** → Enables time-series analytics
2. **The `events` table is append-only** → Event sourcing pattern
3. **Events are denormalized** → Ready for warehouse fact tables
4. **Indexes on timestamps** → Fast range queries for dashboards

---

## 🚀 Run Locally

### Option A: Docker Compose (Recommended)

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd tlaquaNet

# 2. Start PostgreSQL + Backend
docker-compose up -d

# 3. Start frontend
cd frontend
npm install
npm run dev
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

### Option B: Manual Setup

#### 1. PostgreSQL

```bash
# Create database
createdb tlaquanet

# Or with psql
psql -U postgres -c "CREATE DATABASE tlaquanet;"

# (Optional) Run schema manually
psql -U postgres -d tlaquanet -f sql/schema.sql
```

#### 2. Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure database URL
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Run the server
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## ☁️ Deploy for Free

### 1. Database: Neon (Free PostgreSQL)

1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project → Copy the connection string
3. It looks like: `postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb`

### 2. Backend: Render (Free Web Service)

1. Go to [render.com](https://render.com) and connect your GitHub
2. Create a **New Web Service**
3. Configure:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 1`
4. Add Environment Variable:
   - `DATABASE_URL` = your Neon connection string
5. Deploy!

Your API will be at: `https://tlaquanet-api.onrender.com`

### 3. Frontend: Vercel (Free Static Hosting)

1. Go to [vercel.com](https://vercel.com) and connect your GitHub
2. Import the repo
3. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_URL` = `https://tlaquanet-api.onrender.com` (your Render URL)
5. Deploy!

Your app will be at: `https://tlaquanet.vercel.app`

### Alternative Free Hosting

| Service    | For       | Free Tier                        |
|------------|-----------|----------------------------------|
| **Neon**   | Database  | 0.5 GB storage, 190 hours/month  |
| **Supabase** | Database | 500 MB storage, 2 Projects      |
| **Render** | Backend   | 750 hours/month, sleeps on idle  |
| **Railway**| Backend   | $5 free credit/month             |
| **Vercel** | Frontend  | Unlimited static deploys         |
| **Netlify**| Frontend  | 100 GB bandwidth/month           |

---

## 📡 API Reference

### Users

| Method | Endpoint              | Description        |
|--------|-----------------------|--------------------|
| POST   | `/api/users/`         | Create a user      |
| GET    | `/api/users/`         | List all users     |
| GET    | `/api/users/{id}`     | Get user by ID     |

### Posts

| Method | Endpoint                       | Description              |
|--------|--------------------------------|--------------------------|
| POST   | `/api/posts/`                  | Create a post            |
| GET    | `/api/posts/?skip=0&limit=50`  | List posts (feed)        |
| GET    | `/api/posts/{id}`              | Get post by ID           |

### Likes

| Method | Endpoint                           | Description     |
|--------|-------------------------------------|-----------------|
| POST   | `/api/posts/{id}/like`             | Like a post     |
| DELETE | `/api/posts/{id}/like/{user_id}`   | Unlike a post   |

### Comments

| Method | Endpoint                        | Description            |
|--------|---------------------------------|------------------------|
| POST   | `/api/posts/{id}/comments`     | Comment on a post      |
| GET    | `/api/posts/{id}/comments`     | List post comments     |

### Analytics

| Method | Endpoint                              | Description              |
|--------|---------------------------------------|--------------------------|
| GET    | `/api/analytics/events`              | Get event log            |
| GET    | `/api/analytics/events?event_type=X` | Filter by event type     |
| GET    | `/api/analytics/summary`             | Aggregate event counts   |

> 📖 **Interactive docs**: Visit `/docs` on your running backend for Swagger UI.

---

## 📊 Analytics Queries

Once you have data, try these SQL queries against your PostgreSQL database:

```sql
-- 1. Activity timeline (events per day)
SELECT
    DATE(created_at) AS event_date,
    event_type,
    COUNT(*) AS event_count
FROM events
GROUP BY DATE(created_at), event_type
ORDER BY event_date DESC;

-- 2. Most active users
SELECT
    u.username,
    u.display_name,
    COUNT(e.id) AS total_actions
FROM events e
JOIN users u ON u.id = e.user_id
GROUP BY u.id, u.username, u.display_name
ORDER BY total_actions DESC
LIMIT 10;

-- 3. Most liked posts
SELECT
    p.id,
    LEFT(p.content, 50) AS preview,
    u.username AS author,
    COUNT(l.id) AS like_count
FROM posts p
JOIN users u ON u.id = p.author_id
LEFT JOIN likes l ON l.post_id = p.id
GROUP BY p.id, p.content, u.username
ORDER BY like_count DESC
LIMIT 10;

-- 4. Engagement speed (time to first like)
SELECT
    p.id AS post_id,
    p.created_at AS post_time,
    MIN(l.created_at) AS first_like_time,
    MIN(l.created_at) - p.created_at AS time_to_first_like
FROM posts p
JOIN likes l ON l.post_id = p.id
GROUP BY p.id, p.created_at
ORDER BY time_to_first_like ASC;

-- 5. Hourly activity pattern
SELECT
    EXTRACT(HOUR FROM created_at) AS hour_of_day,
    event_type,
    COUNT(*) AS event_count
FROM events
GROUP BY hour_of_day, event_type
ORDER BY hour_of_day;
```

---

## 🎓 Learning Objectives

After working with TlaquaNet, students should understand:

1. **Event-driven architecture**: How to design systems that log events for analytics
2. **Star schema basics**: Fact tables (events, likes) vs dimension tables (users)
3. **REST API design**: How to structure endpoints with FastAPI
4. **ORM patterns**: How SQLAlchemy maps Python classes to SQL tables
5. **Full-stack flow**: Frontend → API → Database → Response
6. **Deployment pipeline**: How to deploy a complete app for free

---

## 📝 License

MIT — Built for educational purposes.
