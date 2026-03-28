from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError

from app.dependencies import get_redis_client, get_http_client, RedisClient
from app.models import User
from . import app, limiter

STOCK_API_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}"


# Retry decorator: 3 attempts, 2 seconds apart
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def call_external_service():
    response = httpx.get("https://example.com/api")
    if response.status_code != 200:
        raise Exception("Service failed")
    return response.json()


@app.get("/data")
def get_data():
    try:
        return call_external_service()
    except RetryError:
        raise HTTPException(status_code=503, detail="External service unavailable")


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
@limiter.limit(
    "5/second",
)
@limiter.limit("100/minute")
async def get_stock(
    request: Request,
    symbol: str,
    client: AsyncClient = Depends(get_http_client),
    redis_client: RedisClient = Depends(get_redis_client),
):
    cache_key = f"stock:{symbol}"

    # 1. Try cache
    cached = await redis_client.async_client.get(cache_key)
    if cached:
        return {"symbol": symbol.upper(), "price": float(cached), "source": "cache"}

    # 2. Fetch from upstream
    price = await fetch_stock_price(symbol, client)

    # 3. Store in Redis (TTL = 10s)
    await redis_client.async_set(cache_key, price, ex=10)

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
    return {"message": "Hello, World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/health/")
def health():
    # Just return HTTP 200 if app is alive and DB connection works.
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
