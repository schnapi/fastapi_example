from fastapi import APIRouter
from prometheus_client import make_asgi_app

from app.api.routes import users, items, auth, websockets

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users")
api_router.include_router(items.router, prefix="/users/{user_id}/items")
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(websockets.router)  # WebSocket endpoints

metrics_app = make_asgi_app()
api_router.mount("/metrics", metrics_app)
