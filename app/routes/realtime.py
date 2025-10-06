from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from app.utils.cache import get_cache

router = APIRouter()
redis = get_cache()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        self.active_connections[project_id] = websocket

    def disconnect(self, project_id: str):
        if project_id in self.active_connections:
            del self.active_connections[project_id]

    async def send_to_project(self, project_id: str, message: dict):
        if project_id in self.active_connections:
            try:
                await self.active_connections[project_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"WebSocket send error: {e}")
                self.disconnect(project_id)


manager = ConnectionManager()


@router.websocket("/ws/projects/{project_id}")
async def project_websocket(websocket: WebSocket, project_id: str):
    await manager.connect(websocket, project_id)
    
    try:
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "type": "connected",
            "project_id": project_id,
            "message": "Connected to real-time updates"
        }))
        
        # Subscribe to Redis channel for this project
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"project:{project_id}")
        
        # Listen for messages
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    await websocket.send_text(json.dumps(data))
                except Exception as e:
                    print(f"WebSocket message error: {e}")
                    
    except WebSocketDisconnect:
        manager.disconnect(project_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(project_id)
    finally:
        await pubsub.unsubscribe(f"project:{project_id}")
        await pubsub.close()


@router.get("/ws/health")
async def websocket_health():
    """Check WebSocket connection health"""
    return {
        "active_connections": len(manager.active_connections),
        "projects": list(manager.active_connections.keys())
    }
