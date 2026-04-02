from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request
from httpx import AsyncClient
import logging

from app.api.dependencies import redis_dependency, get_http_client, RedisClient
from app.models import User
from app.resilience import registry
from . import app, limiter

logger = logging.getLogger("my-fastapi-app")

STOCK_API_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}"


# Retry decorator: 3 attempts, 2 seconds apart. Circuit breaker: opens after 3 failures, recovers after 10 seconds.
@registry.decorator("default")
async def call_external_service(client: AsyncClient):
    response = client.get("https://example.com/api")
    if response.status_code != 200:
        raise Exception("Service failed")
    return response.json()


@app.get("/data")
async def get_data(client: AsyncClient = Depends(get_http_client)):
    try:
        return await call_external_service(client)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


async def fetch_stock_price(symbol: str, client: AsyncClient) -> float:
    url = STOCK_API_URL.format(symbol)

    resp = await client.get(url)

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Upstream API error")

    data = resp.json()

    try:
        result = data["chart"]["result"][0]
        price = result["meta"]["regularMarketPrice"]
        return price
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid symbol")


@app.get("/stock/{symbol}")
# @limiter.limit("10/minute")
@limiter.limit("5/second")
@limiter.limit("100/minute")
async def get_stock(
    request: Request,
    symbol: str,
    client: AsyncClient = Depends(get_http_client),
    redis_client: RedisClient = Depends(redis_dependency),
):
    cache_key = f"stock:{symbol}"

    # 1. Try cache
    cached = await redis_client.async_client.get(cache_key)
    if cached:
        return {"symbol": symbol.upper(), "price": float(cached), "source": "cache"}

    # 2. Fetch from upstream
    price = await fetch_stock_price(symbol, client)

    # 3. Store in Redis (TTL = 10s)
    await redis_client.async_set(cache_key, str(price), ex=10)

    return {"symbol": symbol.upper(), "price": price, "source": "api"}


# from oxyde.db import transaction

# async with transaction.atomic():
#     user = await User.objects.create(name="Alice", email="alice@example.com")
#     await Profile.objects.create(user_id=user.id)


@app.get("/users")
async def get_users():
    # Use Django-style queries!
    return await User.objects.all()


@app.post("/users")
async def create_user(user: User):
    return await user.save()


@app.get("/")
def read_root():
    logger.error("test123")
    logger.warning("Root endpoint was called")
    return {"message": "Hello, World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/health/")
def health():
    # Just return HTTP 200 if app is alive and DB connection works.
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
