import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4
from app.models.game import Game, GameState
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

class GameService:
    def __init__(self):
        self.games: Dict[UUID, Game] = {}
    
    async def create_game(self) -> Tuple[Game, UUID]:
        """Create a new game and return the game object and player X's ID."""
        game_id = uuid4()
        player_x_id = uuid4()
        game = Game(
            id=game_id,
            player_x=player_x_id,
            player_o=None,
            board=[[None] * 3 for _ in range(3)],
            current_turn="X",
            status=GameState.WAITING,
            winner=None
        )
        self.games[game_id] = game
        logger.info(f"Created new game {game_id} for player {player_x_id}")
        return game, player_x_id
    
    async def join_game(self, game_id: UUID) -> Tuple[Game, UUID]:
        """Join an existing game and return the game object and player O's ID."""
        if game_id not in self.games:
            raise ValueError("Game not found")
        
        game = self.games[game_id]
        if game.status != GameState.WAITING:
            raise ValueError("Game is not in waiting state")
        
        player_o_id = uuid4()
        game.player_o = player_o_id
        game.status = GameState.IN_PROGRESS
        
        logger.info(f"Player {player_o_id} joined game {game_id}")
        
        # Broadcast game update to all connected clients
        await manager.broadcast_to_game(game_id, {
            "game_id": game.id,
            "board": game.board,
            "current_turn": game.current_turn,
            "status": game.status,
            "winner": game.winner
        })
        
        return game, player_o_id
    
    async def make_move(self, game_id: UUID, player_id: UUID, position: List[int]) -> Game:
        """Make a move in the game."""
        if game_id not in self.games:
            raise ValueError("Game not found")
        
        game = self.games[game_id]
        if game.status != GameState.IN_PROGRESS:
            raise ValueError("Game is not in progress")
        
        # Validate player and turn
        if game.current_turn == "X" and player_id != game.player_x:
            logger.warning(f"Player {player_id} attempted to move out of turn in game {game_id}")
            raise ValueError("Not your turn")
        if game.current_turn == "O" and player_id != game.player_o:
            logger.warning(f"Player {player_id} attempted to move out of turn in game {game_id}")
            raise ValueError("Not your turn")
        
        # Validate position
        row, col = position
        if not (0 <= row < 3 and 0 <= col < 3):
            raise ValueError("Invalid position")
        if game.board[row][col] is not None:
            raise ValueError("Position already taken")
        
        # Make the move
        game.board[row][col] = game.current_turn
        
        # Check for win
        if self._check_win(game.board, game.current_turn):
            game.status = GameState.FINISHED
            game.winner = game.current_turn
        # Check for draw
        elif all(cell is not None for row in game.board for cell in row):
            game.status = GameState.FINISHED
        else:
            # Switch turns
            game.current_turn = "O" if game.current_turn == "X" else "X"
        
        # Broadcast game update
        await manager.broadcast_to_game(game_id, {
            "game_id": game.id,
            "board": game.board,
            "current_turn": game.current_turn,
            "status": game.status,
            "winner": game.winner
        })
        
        return game
    
    def get_game(self, game_id: UUID) -> Game:
        """Get the current state of a game."""
        if game_id not in self.games:
            raise ValueError("Game not found")
        return self.games[game_id]
    
    def _check_win(self, board: List[List[Optional[str]]], player: str) -> bool:
        """Check if the given player has won."""
        # Check rows
        for row in board:
            if all(cell == player for cell in row):
                return True
        
        # Check columns
        for col in range(3):
            if all(board[row][col] == player for row in range(3)):
                return True
        
        # Check diagonals
        if all(board[i][i] == player for i in range(3)):
            return True
        if all(board[i][2-i] == player for i in range(3)):
            return True
        
        return False

game_service = GameService() 