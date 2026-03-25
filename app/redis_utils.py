# app/redis_utils.py
import os
from typing import Optional

import redis
import redis.asyncio as redis_async  # built-in async support in redis-py >= 4


class RedisClient:
    """
    Redis client wrapper with both sync and async support.
    Singleton pattern.
    """

    _instance: Optional["RedisClient"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_sync_client"):
            return  # already initialized

        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        db = int(os.getenv("REDIS_DB", 0))
        password = os.getenv("REDIS_PASSWORD", None)
        self.default_ttl = int(os.getenv("REDIS_DEFAULT_TTL", 3600))

        # Sync client
        self._sync_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
        )

        # Async client
        self._async_client = redis_async.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
        )

    # --- Sync methods ---
    @property
    def client(self) -> redis.Redis:
        return self._sync_client

    def set(self, key: str, value: str, expire: Optional[int] = None):
        self._sync_client.set(key, value, ex=expire or self.default_ttl)

    def get(self, key: str) -> Optional[str]:
        return self._sync_client.get(key)

    def delete(self, key: str) -> int:
        return self._sync_client.delete(key)

    # --- Async methods ---
    @property
    def async_client(self) -> redis_async.Redis:
        return self._async_client

    async def async_set(self, key: str, value: str, expire: Optional[int] = None):
        await self._async_client.set(key, value, ex=expire or self.default_ttl)

    async def async_get(self, key: str) -> Optional[str]:
        return await self._async_client.get(key)

    async def async_delete(self, key: str) -> int:
        return await self._async_client.delete(key)


def get_redis_client() -> RedisClient:
    """FastAPI / general utility entrypoint"""
    return RedisClient()
