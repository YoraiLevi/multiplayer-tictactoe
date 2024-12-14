import pytest
import json
import asyncio
import websockets
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

async def wait_for_message(ws, timeout=2):
    """Helper function to wait for a WebSocket message."""
    try:
        message = await asyncio.wait_for(ws.recv(), timeout=timeout)
        data = json.loads(message)
        logger.info(f"Received WebSocket message: {data}")
        return data
    except asyncio.TimeoutError:
        logger.error("Timeout waiting for WebSocket message")
        raise

@pytest.mark.asyncio
async def test_websocket_connection(websocket_client, game_id):
    """Test that WebSocket connection can be established."""
    try:
        # Connection is already established in the fixture
        assert websocket_client.open
        logger.info(f"WebSocket connection established for game {game_id}")
    finally:
        await websocket_client.close()
        logger.info("WebSocket connection closed")

@pytest.mark.asyncio
async def test_websocket_game_updates(async_client, test_server, game_id):
    """Test that game updates are broadcasted via WebSocket."""
    # Get player X's ID from game creation
    game_response = await async_client.get(f"/api/games/{game_id}")
    game_data = game_response.json()
    logger.info(f"Get game response: {game_data}")
    player_x_id = game_data["player_id"]
    
    # Create two WebSocket connections (one for each player)
    ws_url = test_server.replace("http://", "ws://")
    uri = f"{ws_url}/api/games/{game_id}/ws"
    logger.info(f"Connecting to WebSocket at {uri}")
    
    async with websockets.client.connect(uri) as ws1, \
              websockets.client.connect(uri) as ws2:
        logger.info("Both WebSocket connections established")
        
        # Join the game
        join_response = await async_client.post(f"/api/games/{game_id}/join")
        assert join_response.status_code == 200
        join_data = join_response.json()
        logger.info(f"Join game response: {join_data}")
        player_o_id = join_data["player_id"]
        
        # Skip initial state messages
        initial_state1 = await wait_for_message(ws1)
        initial_state2 = await wait_for_message(ws2)
        logger.info(f"Initial states received: {initial_state1}, {initial_state2}")
        
        # Wait for join game update
        update1 = await wait_for_message(ws1)
        assert update1["status"] == "in_progress"
        
        # Make a move as player X
        move_data = {
            "player_id": player_x_id,
            "position": [0, 0]
        }
        logger.info(f"Making move with data: {move_data}")
        move_response = await async_client.post(f"/api/games/{game_id}/move", json=move_data)
        assert move_response.status_code == 200
        move_result = move_response.json()
        logger.info(f"Move response: {move_result}")
        
        # Both clients should receive the update
        for i, ws in enumerate([ws1, ws2]):
            update = await wait_for_message(ws)
            logger.info(f"Client {i+1} received update: {update}")
            assert update["board"][0][0] == "X"

@pytest.mark.asyncio
async def test_websocket_multiple_clients(async_client, test_server, game_id):
    """Test that multiple clients can connect and receive updates."""
    # Create three WebSocket connections (two players + spectator)
    ws_url = test_server.replace("http://", "ws://")
    uri = f"{ws_url}/api/games/{game_id}/ws"
    logger.info(f"Connecting three clients to WebSocket at {uri}")
    
    async with websockets.client.connect(uri) as ws1, \
              websockets.client.connect(uri) as ws2, \
              websockets.client.connect(uri) as ws3:
        logger.info("All three WebSocket connections established")
        
        # Skip initial states
        for i, ws in enumerate([ws1, ws2, ws3]):
            initial_state = await wait_for_message(ws)
            logger.info(f"Client {i+1} initial state: {initial_state}")
        
        # Join the game
        join_response = await async_client.post(f"/api/games/{game_id}/join")
        assert join_response.status_code == 200
        join_data = join_response.json()
        logger.info(f"Join game response: {join_data}")
        
        # All clients should receive the join update
        for i, ws in enumerate([ws1, ws2, ws3]):
            update = await wait_for_message(ws)
            logger.info(f"Client {i+1} received update: {update}")
            assert update["status"] == "in_progress"

@pytest.mark.asyncio
async def test_websocket_game_completion(async_client, test_server, game_id):
    """Test that game completion is broadcasted to all clients."""
    # Get player X's ID from game creation
    game_response = await async_client.get(f"/api/games/{game_id}")
    game_data = game_response.json()
    logger.info(f"Get game response: {game_data}")
    player_x_id = game_data["player_id"]
    
    ws_url = test_server.replace("http://", "ws://")
    uri = f"{ws_url}/api/games/{game_id}/ws"
    logger.info(f"Connecting to WebSocket at {uri}")
    
    async with websockets.client.connect(uri) as ws:
        logger.info("WebSocket connection established")
        
        # Skip initial state
        initial_state = await wait_for_message(ws)
        logger.info(f"Initial state: {initial_state}")
        
        # Join the game to get player O's ID
        join_response = await async_client.post(f"/api/games/{game_id}/join")
        assert join_response.status_code == 200
        join_data = join_response.json()
        logger.info(f"Join game response: {join_data}")
        player_o_id = join_data["player_id"]
        
        # Wait for join game update
        join_update = await wait_for_message(ws)
        logger.info(f"Join game update: {join_update}")
        assert join_update["status"] == "in_progress"
        
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
            move_result = response.json()
            logger.info(f"Move {i+1} response: {move_result}")
            update = await wait_for_message(ws)
            logger.info(f"Move {i+1} WebSocket update: {update}")
        
        # Check final update
        assert update["status"] == "finished"
        assert update["winner"] == "X"

@pytest.mark.asyncio
async def test_websocket_disconnect_reconnect(async_client, test_server, game_id):
    """Test that clients can disconnect and reconnect."""
    ws_url = test_server.replace("http://", "ws://")
    uri = f"{ws_url}/api/games/{game_id}/ws"
    logger.info(f"Connecting to WebSocket at {uri}")
    
    # First connection
    ws1 = await websockets.client.connect(uri)
    assert ws1.open
    logger.info("First WebSocket connection established")
    initial_state = await wait_for_message(ws1)
    logger.info(f"First connection initial state: {initial_state}")
    await ws1.close()
    logger.info("First WebSocket connection closed")
    
    # Reconnect
    ws2 = await websockets.client.connect(uri)
    assert ws2.open
    logger.info("Second WebSocket connection established")
    
    try:
        # Skip initial state
        initial_state = await wait_for_message(ws2)
        logger.info(f"Second connection initial state: {initial_state}")
        
        # Join the game and verify we receive the update
        join_response = await async_client.post(f"/api/games/{game_id}/join")
        assert join_response.status_code == 200
        join_data = join_response.json()
        logger.info(f"Join game response: {join_data}")
        update = await wait_for_message(ws2)
        logger.info(f"Reconnection update: {update}")
        assert update["status"] == "in_progress"
    finally:
        await ws2.close()
        logger.info("Second WebSocket connection closed") 