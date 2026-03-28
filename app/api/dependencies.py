from httpx import AsyncClient
from typing import AsyncGenerator

from app.utils.redis_utils import RedisClient, get_redis_client


def redis_dependency() -> RedisClient:
    """
    FastAPI dependency to inject Redis client.
    Usage: redis: RedisClient = Depends(redis_dependency)
    """
    return get_redis_client()


async def get_http_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(timeout=5.0) as client:
        yield client
