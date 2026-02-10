from fastapi import WebSocket
from typing import Dict, List
from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        # user_id -> list of websocket connections
        self.active_connections: Dict[int, List[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)
        print(f"User {user_id} connected")

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)

            # Remove user if no active connections left
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        print(f"User {user_id} disconnected")

    async def send_notification(self, user_id: int, message: dict):
        """
        Send JSON notification to all active connections of a user
        """
        if user_id in self.active_connections:
            disconnected = []

            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # If sending fails, mark connection for removal
                    disconnected.append(connection)

            # Clean up broken connections
            for connection in disconnected:
                self.active_connections[user_id].remove(connection)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]


manager = ConnectionManager()
