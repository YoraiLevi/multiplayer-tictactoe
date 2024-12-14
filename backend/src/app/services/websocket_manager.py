import logging
from typing import Dict, Set
from fastapi import WebSocket
from uuid import UUID
import json

logger = logging.getLogger(__name__)

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

class ConnectionManager:
    def __init__(self):
        # game_id -> set of websocket connections
        self.game_connections: Dict[UUID, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, game_id: UUID):
        """Connect a WebSocket client to a game and send the current game state."""
        await websocket.accept()
        if game_id not in self.game_connections:
            self.game_connections[game_id] = set()
        self.game_connections[game_id].add(websocket)
        logger.info(f"WebSocket connected for game {game_id}")
        logger.info(f"Active connections for game {game_id}: {len(self.game_connections[game_id])}")
        
        # Send current game state to the new client
        from app.services.game_service import game_service
        try:
            game = game_service.get_game(game_id)
            await websocket.send_text(json.dumps({
                "game_id": game.id,
                "board": game.board,
                "current_turn": game.current_turn,
                "status": game.status,
                "winner": game.winner,
                "player_count": game.player_count
            }, cls=UUIDEncoder))
        except ValueError:
            logger.warning(f"Game {game_id} not found when connecting WebSocket")
    
    async def disconnect(self, websocket: WebSocket, game_id: UUID):
        if game_id in self.game_connections and websocket in self.game_connections[game_id]:
            self.game_connections[game_id].remove(websocket)
            logger.info(f"WebSocket disconnected from game {game_id}")
            if not self.game_connections[game_id]:
                del self.game_connections[game_id]
                logger.info(f"No more connections for game {game_id}")
    
    async def broadcast_to_game(self, game_id: UUID, message: dict):
        """Broadcast a message to all clients connected to a game."""
        if game_id in self.game_connections:
            logger.info(f"Broadcasting to game {game_id}: {message}")
            
            # Convert GameState enum to string for JSON serialization
            if "status" in message and hasattr(message["status"], "value"):
                message["status"] = message["status"].value
            
            # Create a single JSON string to ensure all clients receive the same data
            json_str = json.dumps(message, cls=UUIDEncoder)
            disconnected = set()
            
            # Send the same JSON string to all clients
            for connection in self.game_connections[game_id]:
                try:
                    await connection.send_text(json_str)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {str(e)}")
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                await self.disconnect(connection, game_id)

manager = ConnectionManager() 