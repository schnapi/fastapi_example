from fastapi import Depends, APIRouter

from app.api.dependencies import redis_dependency, RedisClient
from app.services.websocket_manager import (
    WebSocketManager,
    WebSocket,
)


router = APIRouter()
manager = WebSocketManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    async with await manager.connect(websocket) as connection:
        while True:
            data = await connection.receive_text()  # disconnect handled internally
            await connection.send_personal_message(f"User {user_id} says: {data}")
            # optional broadcast:
            # await manager.broadcast(f"User {user_id} says: {data}")


@router.websocket("/ws/tasks/{task_id}")
async def task_ws(
    websocket: WebSocket,
    task_id: str,
    redis_client: RedisClient = Depends(redis_dependency),
):
    await websocket.accept()
    pubsub = redis_client.async_client.pubsub()
    await pubsub.subscribe(f"task:{task_id}")

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = message["data"]
            await websocket.send_json(data)
            if data["status"] in ["done", "failed"]:
                break
