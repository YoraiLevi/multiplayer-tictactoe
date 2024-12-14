from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from uuid import UUID
from app.models.game import GameMove, GameResponse, ErrorResponse, GameState
from app.services.game_service import game_service
from app.services.websocket_manager import manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/games/{game_id}/ws")
async def websocket_endpoint(websocket: WebSocket, game_id: UUID):
    """WebSocket endpoint for real-time game updates."""
    try:
        await manager.connect(websocket, game_id)
        while True:
            try:
                # Keep the connection alive and wait for disconnection
                await websocket.receive_text()
            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected from game {game_id}")
                break
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
    finally:
        await manager.disconnect(websocket, game_id)

@router.post("/games", response_model=GameResponse)
async def create_game():
    """Create a new game."""
    try:
        game, player_id = await game_service.create_game()
        return GameResponse(
            game_id=game.id,
            player_id=player_id,
            board=game.board,
            status=game.status,
            current_turn=game.current_turn,
            player_count=game.player_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                code="GAME_ERROR",
                message="Failed to create game",
                details={"error": str(e)}
            ).model_dump()
        )

@router.post("/games/{game_id}/join", response_model=GameResponse)
async def join_game(game_id: UUID):
    """Join an existing game."""
    try:
        game, player_id = await game_service.join_game(game_id)
        return GameResponse(
            game_id=game.id,
            player_id=player_id,
            board=game.board,
            current_turn=game.current_turn,
            status=game.status,
            player_count=game.player_count
        )
    except ValueError as e:
        if str(e) == "Game not found":
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    code="GAME_NOT_FOUND",
                    message="Game not found",
                    details={"game_id": str(game_id)}
                ).model_dump()
            )
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                code="GAME_RULE_VIOLATION",
                message=str(e),
                details={"game_id": str(game_id)}
            ).model_dump()
        )

@router.post("/games/{game_id}/move", response_model=GameResponse)
async def make_move(game_id: UUID, move: GameMove):
    """Make a move in the game."""
    try:
        game = await game_service.make_move(game_id, move.player_id, move.position)
        return GameResponse(
            game_id=game.id,
            board=game.board,
            current_turn=game.current_turn,
            status=game.status,
            winner=game.winner,
            player_count=game.player_count
        )
    except ValueError as e:
        if str(e) == "Game not found":
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    code="GAME_NOT_FOUND",
                    message="Game not found",
                    details={"game_id": str(game_id)}
                ).model_dump()
            )
        elif str(e) == "Invalid position":
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    code="INVALID_POSITION",
                    message="Position out of bounds",
                    details={"position": move.position}
                ).model_dump()
            )
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                code="GAME_RULE_VIOLATION",
                message=str(e),
                details={
                    "game_id": str(game_id),
                    "player_id": str(move.player_id),
                    "position": move.position
                }
            ).model_dump()
        )

@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game(game_id: UUID):
    """Get the current state of a game."""
    try:
        game = game_service.get_game(game_id)
        return GameResponse(
            game_id=game.id,
            player_id=game.player_x,  # Include player X's ID in the response
            board=game.board,
            current_turn=game.current_turn,
            status=game.status,
            winner=game.winner,
            player_count=game.player_count
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                code="GAME_NOT_FOUND",
                message="Game not found",
                details={"game_id": str(game_id)}
            ).model_dump()
        ) 