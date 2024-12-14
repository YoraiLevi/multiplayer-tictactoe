import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import websockets.client
from uuid import UUID
import uvicorn
import multiprocessing
import time
import socket
import logging

from src.app.main import app
from src.app.services.game_service import game_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_free_port():
    """Get a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_server():
    """Start a test server instance."""
    port = get_free_port()
    server_config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config=server_config)
    
    # Start server in a separate process
    process = multiprocessing.Process(target=server.run)
    process.start()
    time.sleep(0.5)  # Give the server more time to start
    
    yield f"http://127.0.0.1:{port}"
    
    # Cleanup
    process.terminate()
    process.join()

@pytest.fixture
def client() -> Generator:
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client(test_server) -> AsyncGenerator:
    """Create an async HTTP client."""
    async with AsyncClient(base_url=test_server, follow_redirects=True) as ac:
        yield ac

@pytest.fixture(autouse=True)
async def clear_game_service():
    """Clear the game service state before each test."""
    game_service.games.clear()
    yield

@pytest.fixture
async def game_id(async_client) -> UUID:
    """Create a game and return its ID."""
    response = await async_client.post("/api/games")
    assert response.status_code == 200
    return UUID(response.json()["game_id"])

@pytest.fixture
async def websocket_client(game_id, test_server) -> AsyncGenerator:
    """Create a WebSocket client connected to a specific game."""
    ws_url = test_server.replace("http://", "ws://")
    uri = f"{ws_url}/api/games/{game_id}/ws"
    
    try:
        async with websockets.client.connect(uri) as websocket:
            yield websocket
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
        raise 