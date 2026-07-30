# FeedbackIQ Backend

Production-ready FastAPI backend for **FeedbackIQ** — Intelligent Feedback Management Platform.

## 🏗️ Architecture & Technology Stack

- **FastAPI 0.115** — High-performance async web framework
- **Python 3.11+** — Modern type-hinted runtime
- **Motor 3.6** — Async MongoDB driver (Singleton pool)
- **Redis 5.2** — Async caching with fallback when Redis is offline
- **Pydantic v2** — Data validation & Settings management
- **Uvicorn** — ASGI web server

### Directory Structure

```
backend/
├── app/
│   ├── api/            # Central router aggregator
│   ├── routers/        # Health & Feedback API endpoints
│   ├── services/       # Business logic layer (FeedbackService)
│   ├── repositories/   # Data access layer (FeedbackRepository)
│   ├── database/       # Motor connection pool manager
│   ├── cache/          # Redis connection & cache manager
│   ├── schemas/        # Request & Response Pydantic DTOs
│   ├── models/         # MongoDB Document models
│   ├── middleware/     # Request logging & timing middleware
│   ├── config/         # Pydantic Settings (.env configuration)
│   ├── exceptions/     # Custom exception classes & global handlers
│   ├── utils/          # Logging & utility functions
│   ├── dependencies/   # FastAPI Dependency Injection providers
│   └── main.py         # FastAPI application factory
├── Dockerfile          # Multi-stage production Docker build
├── requirements.txt    # Pinned dependencies
├── .env.example        # Environment template
├── .gitignore
└── README.md
```

---

## ⚡ API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/feedback` | Store a new feedback document & invalidate cache |
| `GET` | `/api/dashboard` | Get feedback stats (Total, Positive, Neutral, Negative, Latest 10) |
| `GET` | `/api/search?q=keyword` | Case-insensitive search inside feedback comments |
| `GET` | `/` | API Root Welcome |
| `GET` | `/health` | Deep Health Check (Verifies MongoDB & Redis) |
| `GET` | `/ping` | Lightweight Liveness Ping |
| `GET` | `/docs` | Interactive Swagger UI Documentation |
| `GET` | `/redoc` | ReDoc API Reference |

---

## ⚙️ Environment Configuration

Create a `.env` file in `backend/`:

```env
MONGO_URI=mongodb+srv://informationtechiparth4675_db_user:a0qVRurHcO6ICacI@feedbackiq-cluster.h3wvrvw.mongodb.net/?appName=feedbackiq-cluster
DATABASE_NAME=feedbackiq
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

---

## 🚀 Running the Backend

### Local Execution

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose Execution

From the project root directory:

```bash
docker compose up --build
```
# feedbackiq-backend
