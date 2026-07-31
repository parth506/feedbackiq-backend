"""
Cache dependency provider.
"""
from app.services.cache_service import CacheService


def get_cache_service() -> CacheService:
    """Provide a CacheService instance (stateless, safe to re-create per request)."""
    return CacheService()
