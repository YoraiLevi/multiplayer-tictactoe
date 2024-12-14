import pytest
import logging
from uuid import UUID
from src.app.models.game import GameState

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_create_game(async_client):
    """Test creating a new game."""
    response = await async_client.post("/api/games")
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Create game response: {data}")
    
    assert "game_id" in data
    assert "player_id" in data
    assert data["status"] == "waiting"
    assert data["board"] == [[None] * 3 for _ in range(3)]

@pytest.mark.asyncio
async def test_join_game(async_client, game_id):
    """Test joining an existing game."""
    response = await async_client.post(f"/api/games/{game_id}/join")
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Join game response: {data}")
    
    assert data["game_id"] == str(game_id)
    assert "player_id" in data
    assert data["status"] == "in_progress"
    assert data["current_turn"] == "X"

@pytest.mark.asyncio
async def test_join_nonexistent_game(async_client):
    """Test joining a game that doesn't exist."""
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    response = await async_client.post(f"/api/games/{fake_id}/join")
    assert response.status_code == 404
    data = response.json()
    logger.info(f"Join nonexistent game error response: {data}")

@pytest.mark.asyncio
async def test_get_game_state(async_client, game_id):
    """Test getting the state of an existing game."""
    response = await async_client.get(f"/api/games/{game_id}")
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Get game state response: {data}")
    
    assert data["game_id"] == str(game_id)
    assert data["status"] == "waiting"

@pytest.mark.asyncio
async def test_make_move(async_client, game_id):
    """Test making a valid move in a game."""
    # Get player X's ID from game creation
    game_response = await async_client.get(f"/api/games/{game_id}")
    game_data = game_response.json()
    logger.info(f"Get game response: {game_data}")
    player_x_id = game_data["player_id"]
    
    # Join the game to start it
    join_response = await async_client.post(f"/api/games/{game_id}/join")
    join_data = join_response.json()
    logger.info(f"Join game response: {join_data}")
    player_o_id = join_data["player_id"]
    
    # Make a move as player X
    move_data = {
        "player_id": player_x_id,
        "position": [0, 0]
    }
    logger.info(f"Making move with data: {move_data}")
    response = await async_client.post(f"/api/games/{game_id}/move", json=move_data)
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Make move response: {data}")
    
    assert data["board"][0][0] == "X"
    assert data["current_turn"] == "O"

@pytest.mark.asyncio
async def test_invalid_move(async_client, game_id):
    """Test making an invalid move."""
    # Get player X's ID from game creation
    game_response = await async_client.get(f"/api/games/{game_id}")
    game_data = game_response.json()
    logger.info(f"Get game response: {game_data}")
    player_x_id = game_data["player_id"]
    
    # Join the game
    join_response = await async_client.post(f"/api/games/{game_id}/join")
    join_data = join_response.json()
    logger.info(f"Join game response: {join_data}")
    
    # Try to make a move out of bounds
    move_data = {
        "player_id": player_x_id,
        "position": [3, 3]
    }
    logger.info(f"Making invalid move with data: {move_data}")
    response = await async_client.post(f"/api/games/{game_id}/move", json=move_data)
    assert response.status_code == 400
    error_data = response.json()
    logger.info(f"Invalid move error response: {error_data}")

@pytest.mark.asyncio
async def test_move_wrong_turn(async_client, game_id):
    """Test making a move when it's not the player's turn."""
    # Get player X's ID from game creation
    game_response = await async_client.get(f"/api/games/{game_id}")
    game_data = game_response.json()
    logger.info(f"Get game response: {game_data}")
    player_x_id = game_data["player_id"]
    
    # Join the game to get player O's ID
    join_response = await async_client.post(f"/api/games/{game_id}/join")
    join_data = join_response.json()
    logger.info(f"Join game response: {join_data}")
    player_o_id = join_data["player_id"]
    
    # Try to make a move as O when it's X's turn
    move_data = {
        "player_id": player_o_id,
        "position": [0, 0]
    }
    logger.info(f"Making wrong turn move with data: {move_data}")
    response = await async_client.post(f"/api/games/{game_id}/move", json=move_data)
    assert response.status_code == 422
    error_data = response.json()
    logger.info(f"Wrong turn error response: {error_data}")

@pytest.mark.asyncio
async def test_win_condition(async_client, game_id):
    """Test winning a game."""
    # Get player X's ID from game creation
    game_response = await async_client.get(f"/api/games/{game_id}")
    game_data = game_response.json()
    logger.info(f"Get game response: {game_data}")
    player_x_id = game_data["player_id"]
    
    # Join the game to get player O's ID
    join_response = await async_client.post(f"/api/games/{game_id}/join")
    join_data = join_response.json()
    logger.info(f"Join game response: {join_data}")
    player_o_id = join_data["player_id"]
    
    # Make winning moves for X (diagonal)
    moves = [
        {"player_id": player_x_id, "position": [0, 0]},  # X
        {"player_id": player_o_id, "position": [0, 1]},  # O
        {"player_id": player_x_id, "position": [1, 1]},  # X
        {"player_id": player_o_id, "position": [0, 2]},  # O
        {"player_id": player_x_id, "position": [2, 2]},  # X - winning move
    ]
    
    for i, move in enumerate(moves):
        logger.info(f"Making move {i+1} with data: {move}")
        response = await async_client.post(f"/api/games/{game_id}/move", json=move)
        assert response.status_code == 200
        move_data = response.json()
        logger.info(f"Move {i+1} response: {move_data}")
    
    # Check final state
    final_response = await async_client.get(f"/api/games/{game_id}")
    final_state = final_response.json()
    logger.info(f"Final game state: {final_state}")
    assert final_state["status"] == "finished"
    assert final_state["winner"] == "X" 