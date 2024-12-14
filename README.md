# Multiplayer Tic-tac-toe

A real-time multiplayer Tic-tac-toe game built with FastAPI (backend) and React,Vite (frontend). The game supports multiple concurrent games and provides a clean, modern interface.
 
<span>
<img src="pictures/Screenshot%20from%202024-12-14%2021-06-32.png" alt="Screenshot from 2024-12-14 21-06-32" width="225"/>
<img src="pictures/Screenshot%20from%202024-12-14%2021-06-34.png" alt="Screenshot from 2024-12-14 21-06-34" width="225"/>
<img src="pictures/Screenshot%20from%202024-12-14%2021-05-52.png" alt="Screenshot from 2024-12-14 21-05-52" width="225"/>
<img src="pictures/Screenshot%20from%202024-12-14%2021-06-26.png" alt="Screenshot from 2024-12-14 21-06-26" width="225"/>
</span>


## Project Structure

```
├── backend/
│   ├── src/
│   │   └── app/
│   │       ├── models/      # Data models and game state
│   │       ├── services/    # Game logic and WebSocket management
│   │       ├── routes/      # API endpoints
│   │       └── middleware/  # Logging middleware
│   ├── tests/              # API and WebSocket tests
│   └── run.sh             # Server startup script
└── frontend/
    └── src/
        ├── components/    # React components
        ├── services/      # API client
        └── types/         # TypeScript definitions
```

## Getting Started

### Backend Setup

1. Create and activate a virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   ./run.sh --reload
   ```
   The server will run on http://localhost:8000

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   ./run.sh
   ```
   The frontend will run on http://localhost:5173

To start both at once, make sure you have the python's virtual environment activated:
```bash
source ./backend/.venv/bin/activate
./run.sh
```

## Game Architecture

### Key Entities
[backend/src/app/models/game.py](backend/src/app/models/game.py) &
<a href="frontend/src/types/game.ts">frontend/src/types/game.ts</a>

1. **Game State**
   ```typescript
   {
     game_id: string;          // Unique identifier
     player_id?: string;       // Current player's ID
     board: Board;             // 3x3 matrix
     current_turn?: Symbol;    // 'X' or 'O'
     status: GameStatus;       // 'waiting'|'in_progress'|'finished'
     winner?: Symbol;          // Winner symbol or null for draw
     player_count: number;     // Number of players (1 or 2)
   }
   ```

2. **Game Move**
   ```typescript
   {
     player_id: string;        // Player making the move
     position: [number, number] // Board coordinates [row, col]
   }
   ```

### Game Flow
[backend/src/app/services/game_service.py](backend/src/app/services/game_service.py)
1. **Game Creation**
   - Player creates a new game (becomes Player X)
   - Receives a unique game ID to share
   - Waits for opponent to join

2. **Joining a Game**
   - Second player joins using game ID (becomes Player O)
   - Game status changes to 'in_progress'
   - Players alternate making moves

3. **Making Moves**
   - Validates:
     - Correct player's turn
     - Valid board position
     - Position is unoccupied
   - Updates game state
   - Checks for win/draw condition
   - ~~Websocket broadcasts new state to all players~~ - not implemented, Polling every second is used instead

4. **Win Condition Check**
   After each move, checks for:
   - Three matching symbols in any row
   - Three matching symbols in any column
   - Three matching symbols in either diagonal
   - Full board with no winner (draw)

## API Endpoints  
[backend/src/app/routes/games.py](backend/src/app/routes/games.py)
- `POST /api/games` - Create new game
- `POST /api/games/{id}/join` - Join existing game
- `POST /api/games/{id}/move` - Make a move
- `GET /api/games/{id}` - Get game state

## Features

- **Real-time Updates**: Game state is polled every second
- **Multiple Games**: Server supports concurrent game sessions
- **Error Handling**: Comprehensive error messages and validation
- **User Experience**:
  - Easy game ID sharing - copy to clipboard!
  - Clear turn indicators!
  - Visual feedback for valid moves!

## Code Organization

1. **Backend**
   - Clean separation of concerns (models, services, routes)
   - Centralized game logic in GameService
   - Comprehensive test coverage for RESTAPI
   - Type safety with Pydantic models

2. **Frontend**
   - Component-based architecture
   - TypeScript for type safety
   - Centralized game service for API calls
   - CSS modules for style isolation

## Error Handling

- Invalid moves return appropriate HTTP status codes:
  - 400: Bad Request (invalid position)
  - 422: Unprocessable Entity (wrong turn/game rules)
  - 404: Not Found (game doesn't exist)

## Future Improvements

1. Persistent storage for game history
2. User authentication
3. Game replay,undo move feature
4. Spectator mode
5. Game statistics and leaderboards
6. Websocket for real-time updates
7. More UI Fluff
8. Timeouts for inactive games
9. Resource cleanup (memory after game ends)
