"""
Integration tests for core API routes.
Uses the async_client fixture which overrides all service dependencies.
"""
import pytest


@pytest.mark.asyncio
async def test_ping(async_client):
    response = await async_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


@pytest.mark.asyncio
async def test_health_returns_200_or_503(async_client):
    response = await async_client.get("/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "mongo" in data


@pytest.mark.asyncio
async def test_create_feedback_success(async_client):
    response = await async_client.post(
        "/api/feedback",
        json={"sentiment": "positive", "comment": "Excellent dashboard!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_create_feedback_invalid_sentiment(async_client):
    response = await async_client.post(
        "/api/feedback",
        json={"sentiment": "amazing", "comment": "test"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_feedback_comment_too_long(async_client):
    response = await async_client.post(
        "/api/feedback",
        json={"sentiment": "positive", "comment": "x" * 1001},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_dashboard_stats(async_client):
    response = await async_client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_feedback" in data
    assert "positive" in data
    assert "latest_feedback" in data


@pytest.mark.asyncio
async def test_auth_token_creation_directly():
    """Test token creation/decode directly without hitting MongoDB."""
    from app.features.auth.service import AuthService
    token = AuthService.create_access_token({
        "sub": "test_user_id",
        "email": "test@feedbackiq.ai",
        "role": "admin",
    })
    assert token is not None
    payload = AuthService.decode_access_token(token)
    assert payload["email"] == "test@feedbackiq.ai"
    assert payload["role"] == "admin"


@pytest.mark.asyncio
async def test_analytics_time_series(async_client):
    response = await async_client.get("/api/v1/analytics/time-series")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_sentiment_emotions(async_client):
    response = await async_client.get("/api/v1/sentiment/emotions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_ai_insights_summary(async_client):
    response = await async_client.get("/api/v1/ai-insights/summary")
    assert response.status_code == 200
    data = response.json()
    assert "headline" in data
    assert "summary" in data


@pytest.mark.asyncio
async def test_search_comments(async_client):
    response = await async_client.get("/api/v1/search/comments?q=great")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_search_empty_query_rejected(async_client):
    response = await async_client.get("/api/v1/search/comments?q=")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_monitoring_metrics(async_client):
    response = await async_client.get("/api/v1/monitoring/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "requests_total" in data
    assert "error_rate" in data
