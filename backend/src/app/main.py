import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import games
from app.middleware.logging import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('game_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Tic-tac-toe API",
    description="A multiplayer Tic-tac-toe game API with WebSocket support",
    version="1.0.0"
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(games.router, prefix="/api", tags=["games"])

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("Starting up Tic-tac-toe API server...")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=" * 50)
    logger.info("Shutting down Tic-tac-toe API server...")
    logger.info("=" * 50) 