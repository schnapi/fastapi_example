from fastapi import WebSocket, WebSocketDisconnect


class WebSocketManager:
    """Manages multiple WebSocket connections with optional re-raise on disconnect."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    class Connection:
        def __init__(
            self,
            websocket: WebSocket,
            manager: "WebSocketManager",
            re_raise: bool = True,
        ):
            self.websocket = websocket
            self.manager = manager
            self.re_raise = re_raise
            self.connected = False

        async def __aenter__(self):
            await self.manager._connect(self.websocket)
            self.connected = True
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if self.connected:
                await self.manager._disconnect(self.websocket)
                self.connected = False

        async def receive_text(self):
            try:
                return await self.websocket.receive_text()
            except WebSocketDisconnect:
                await self.manager._disconnect(self.websocket)
                if self.re_raise:
                    raise  # only re-raise if flag is True

        async def send_personal_message(self, message: str):
            await self.websocket.send_text(message)

    async def _connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def _disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            await websocket.close()

    async def connect(self, websocket: WebSocket, re_raise: bool = False):
        """Return an async context manager for this WebSocket."""
        return self.Connection(websocket, self, re_raise)

    # Optional broadcast for all active connections
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
