from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel

class GameState(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

class Game(BaseModel):
    id: UUID
    player_x: UUID
    player_o: Optional[UUID] = None
    board: List[List[Optional[str]]]
    current_turn: str
    status: GameState
    winner: Optional[str] = None

    @property
    def player_count(self) -> int:
        """Get the number of players currently in the game."""
        return 1 if self.player_o is None else 2

class GameMove(BaseModel):
    player_id: UUID
    position: List[int]

class GameResponse(BaseModel):
    game_id: UUID
    player_id: Optional[UUID] = None
    board: List[List[Optional[str]]]
    current_turn: Optional[str] = None
    status: GameState
    winner: Optional[str] = None
    player_count: int

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None 