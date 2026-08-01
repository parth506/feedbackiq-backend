"""
Legacy integration tests — migrated to use mock fixtures.
The original test_api.py hit real MongoDB which is unreliable in CI.
All tests now use the async_client fixture with dependency overrides.
"""
import pytest


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    response = await async_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


@pytest.mark.asyncio
async def test_auth_token_service():
    """Test JWT token creation & decode without MongoDB dependency."""
    from app.features.auth.service import AuthService
    token = AuthService.create_access_token({"sub": "u1", "email": "admin@feedbackiq.ai", "role": "admin"})
    payload = AuthService.decode_access_token(token)
    assert payload["email"] == "admin@feedbackiq.ai"


@pytest.mark.asyncio
async def test_analytics_time_series(async_client):
    response = await async_client.get("/api/v1/analytics/time-series")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_ai_insights_summary(async_client):
    response = await async_client.get("/api/v1/ai-insights/summary")
    assert response.status_code == 200
    data = response.json()
    assert "headline" in data
    assert "summary" in data
