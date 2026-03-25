from slowapi.errors import RateLimitExceeded
from fastapi import HTTPException, Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware

from oxyde import db
from oxyde_admin import FastAPIAdmin

from app.redis_utils import get_redis_client
from app.config import settings
from app.models import User
from app.rate_limit_utils import user_key

# Enable debugpy in development
if settings.debug:
    from app.debugger import enable_debugpy

    enable_debugpy()

app = FastAPI(title="MyApp")
redis_client = get_redis_client()


app = FastAPI(lifespan=db.lifespan(default=settings.database_url))
admin = FastAPIAdmin(title="My Dashboard")
admin.register(User, list_display=["username", "email"], search_fields=["username"])
app.mount("/admin", admin.app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
limiter = Limiter(key_func=user_key, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return HTTPException(status_code=429, detail="Rate limit exceeded")


@app.on_event("startup")
async def on_startup():
    try:
        redis_client.client.ping()
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    try:
        redis_client.client.close()
        if hasattr(redis_client, "_async_client") and redis_client._async_client:
            await redis_client._async_client.close()
        print("Redis connection closed")
    except Exception:
        pass
