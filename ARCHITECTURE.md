# FeedbackIQ Backend — Architecture Guide

## Overview

FeedbackIQ is an enterprise AI-powered feedback analytics platform. The backend is built with **FastAPI**, **Motor** (async MongoDB), and **Redis**, following **Clean Architecture**, **SOLID principles**, **Repository Pattern**, **Service Layer**, and **Dependency Injection**.

---

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         HTTP Client                              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    Middleware Stack                               │
│  CorrelationIDMiddleware → RequestTimingMiddleware               │
│  → RequestLoggingMiddleware                                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    API / Router Layer                             │
│  app/routers/          — Legacy compat (POST /api/feedback)      │
│  app/features/*/router.py — Thin delegates (GET /api/v1/...)     │
│  Rules: validate → call service → return response                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    Service Layer                                  │
│  FeedbackService    AnalyticsService   SentimentService          │
│  TopicModelingService  AIInsightsService  SearchService          │
│  MonitoringService  CacheService                                 │
│  Rules: business logic, caching, coordination                    │
└────────────┬──────────────────────────┬─────────────────────────┘
             │                          │
┌────────────▼────────────┐  ┌──────────▼──────────────────────────┐
│   Repository Layer       │  │   Cache Layer                        │
│  FeedbackRepository      │  │  CacheService → RedisManager         │
│  extends BaseRepository  │  │  Keys: feedbackiq:<domain>:<res>     │
│  MongoDB: Motor async    │  │  TTLs: 5–10 minutes per domain       │
└────────────┬────────────┘  └─────────────────────────────────────┘
             │
┌────────────▼────────────┐
│   Database Layer         │
│  DatabaseManager         │
│  Motor AsyncIOMotorClient│
│  Connection pool: 10–100 │
│  TLS via certifi (Atlas) │
└─────────────────────────┘
```

---

## Folder Structure

```
app/
├── api/
│   └── router.py          ← Central router aggregator
├── core/
│   ├── constants.py       ← All magic strings, cache keys, limits
│   ├── indexes.py         ← MongoDB index management (run on startup)
│   ├── interfaces.py      ← Abstract interfaces: LLM, Embeddings, Predictions, TaskQueue
│   └── task_queue.py      ← InMemoryTaskQueue stub (swap with Celery/RQ)
├── cache/
│   └── client.py          ← RedisManager (low-level async Redis)
├── config/
│   └── settings.py        ← Pydantic BaseSettings (all from .env)
├── database/
│   └── session.py         ← DatabaseManager (Motor singleton pool)
├── dependencies/
│   ├── db.py              ← get_db() provider
│   ├── cache.py           ← get_cache_service() provider
│   └── feedback.py        ← All service providers (get_feedback_service, etc.)
├── exceptions/
│   ├── exceptions.py      ← Exception hierarchy
│   └── handlers.py        ← FastAPI exception handlers (includes corr_id)
├── features/              ← Feature modules (routers + schemas only)
│   ├── analytics/
│   ├── ai_insights/
│   ├── auth/
│   ├── monitoring/
│   ├── predictions/
│   ├── search/
│   ├── sentiment/
│   └── topic_modeling/
├── middleware/
│   ├── correlation.py     ← X-Correlation-ID injection
│   ├── logging.py         ← Request access logging
│   └── timing.py          ← X-Process-Time header
├── models/
│   └── feedback.py        ← MongoDB document model
├── repositories/
│   ├── base.py            ← BaseRepository ABC (9-method contract)
│   └── feedback.py        ← FeedbackRepository (extends BaseRepository)
├── routers/
│   ├── feedback.py        ← Legacy compat (/api/feedback, /api/dashboard, /api/search)
│   └── health.py          ← /ping, /health
├── schemas/
│   └── feedback.py        ← Pydantic v2 request/response schemas
├── services/
│   ├── analytics_service.py
│   ├── ai_service.py
│   ├── cache_service.py   ← CacheService (get_or_set, namespaced keys)
│   ├── feedback.py        ← FeedbackService
│   ├── monitoring_service.py
│   ├── search_service.py
│   ├── sentiment_service.py
│   └── topic_service.py
└── utils/
    └── logging.py         ← setup_logging() + JSONFormatter + CorrelationFilter
```

---

## Cache Strategy

| Cache Key | TTL | Invalidated By |
|-----------|-----|----------------|
| `feedbackiq:dashboard:stats` | 5 min | `POST /api/feedback` |
| `feedbackiq:analytics:time_series` | 5 min | Manual or TTL expiry |
| `feedbackiq:analytics:categories` | 5 min | TTL expiry |
| `feedbackiq:sentiment:emotions` | 5 min | TTL expiry |
| `feedbackiq:sentiment:evolution` | 5 min | TTL expiry |
| `feedbackiq:topics:importance` | 10 min | TTL expiry |
| `feedbackiq:topics:keywords` | 10 min | TTL expiry |
| `feedbackiq:ai:summary` | 10 min | TTL expiry |
| `feedbackiq:ai:recommendations` | 10 min | TTL expiry |

All caching uses the **Cache-Aside (Lazy Loading)** pattern via `CacheService.get_or_set()`. Redis failure is non-fatal — the service computes from MongoDB.

---

## MongoDB Indexes

Defined in `app/core/indexes.py`, created idempotently on startup:

| Index | Purpose |
|-------|---------|
| `feedback.created_at DESC` | Powers `find_latest()`, time-series, SSE/WS |
| `feedback.sentiment ASC` | Powers `count_documents({sentiment: ...})` |
| `feedback.sentiment + created_at` | Compound for dashboard `$facet` pipeline |
| `feedback.comment TEXT` | Full-text search (replaces O(n) regex scans) |

---

## Dependency Injection Graph

```
get_db()
  └── get_feedback_repository()
        ├── get_feedback_service(cache)
        ├── get_analytics_service(cache)
        ├── get_sentiment_service(cache)
        ├── get_topic_service(cache)
        ├── get_ai_service(cache)
        └── get_search_service()

get_cache_service()
  └── (injected into all services above)

get_monitoring_service()  [stateless — no deps]
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URI` | ✅ | MongoDB connection string |
| `DATABASE_NAME` | ✅ | Database name (default: `feedbackiq`) |
| `REDIS_HOST` | ⚠️ | Redis hostname (cache disabled if absent) |
| `REDIS_PORT` | ⚠️ | Redis port (default: 6379) |
| `REDIS_PASSWORD` | ❌ | Redis auth password |
| `SECRET_KEY` | ✅ | JWT signing secret (**must** be changed in production) |
| `ALLOWED_ORIGINS` | ✅ | JSON list of allowed CORS origins |
| `APP_ENV` | ✅ | `development` or `production` (enables JSON logging) |
| `CACHE_TTL_DASHBOARD` | ❌ | Dashboard cache TTL in seconds (default: 300) |
| `CACHE_TTL_ANALYTICS` | ❌ | Analytics cache TTL (default: 300) |
| `CACHE_TTL_TOPICS` | ❌ | Topics cache TTL (default: 600) |
| `CACHE_TTL_AI_INSIGHTS` | ❌ | AI insights cache TTL (default: 600) |

---

## API Flow (Request Lifecycle)

```
1. Request arrives
2. CorrelationIDMiddleware: injects/generates X-Correlation-ID → ContextVar
3. RequestTimingMiddleware: starts perf timer
4. RequestLoggingMiddleware: logs method + path
5. FastAPI router matches endpoint
6. Depends() resolves: get_db() → get_repository() → get_service()
7. Service checks CacheService.get(key)
   ├── HIT  → return cached JSON
   └── MISS → run MongoDB aggregation via Repository
               → store in Redis via CacheService.set()
               → return response
8. Exception handler catches domain exceptions → includes corr_id in response
9. RequestTimingMiddleware: adds X-Process-Time header
10. CorrelationIDMiddleware: adds X-Correlation-ID response header
```

---

## AI-Readiness

Interfaces in `app/core/interfaces.py`:

- `LLMProviderInterface` — `summarize()`, `classify()`, `extract_keywords()`
- `EmbeddingProviderInterface` — `embed_text()`, `embed_batch()`
- `PredictionProviderInterface` — `forecast(history, horizon_days)`
- `TaskQueueInterface` — `enqueue()`, `get_status()`

Current implementation: rule-based (inline in `AIInsightsService`). Swap by implementing the interface and injecting via `get_ai_service()`.

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MONGO_URI and SECRET_KEY

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests (no MongoDB/Redis required)
pytest tests/ -v
```
