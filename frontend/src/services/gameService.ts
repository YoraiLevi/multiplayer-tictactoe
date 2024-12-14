import axios from 'axios';
import { GameState, GameMove } from '../types/game';

const API_URL = 'http://localhost:8000/api';

export class GameService {
    async createGame(): Promise<GameState> {
        const response = await axios.post<GameState>(`${API_URL}/games`);
        return response.data;
    }

    async joinGame(gameId: string): Promise<GameState> {
        const response = await axios.post<GameState>(`${API_URL}/games/${gameId}/join`);
        return response.data;
    }

    async makeMove(gameId: string, move: GameMove): Promise<GameState> {
        const response = await axios.post<GameState>(
            `${API_URL}/games/${gameId}/move`,
            move
        );
        return response.data;
    }

    async getGameState(gameId: string): Promise<GameState> {
        const response = await axios.get<GameState>(`${API_URL}/games/${gameId}`);
        return response.data;
    }

    connectWebSocket(
        gameId: string, 
        onMessage: (data: GameState) => void,
        onConnectionChange: (connected: boolean) => void
    ): void {
        this.gameId = gameId;
        this.onMessage = onMessage;
        this.onConnectionChange = onConnectionChange;
        this.reconnectAttempts = 0;
        
        this.establishWebSocketConnection();
    }

    private establishWebSocketConnection(): void {
        if (this.ws?.readyState === WebSocket.OPEN) {
            console.log('WebSocket already connected');
            return;
        }

        console.log('Establishing WebSocket connection...');
        this.ws = new WebSocket(`ws://localhost:8000/api/games/${this.gameId}/ws`);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            this.onConnectionChange?.(true);
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.onMessage?.(data);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.onConnectionChange?.(false);
        };

        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
            this.onConnectionChange?.(false);
            this.attemptReconnect();
        };
    }

    private attemptReconnect(): void {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 10000);
        
        console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        this.reconnectTimeout = setTimeout(() => {
            if (this.gameId) {
                this.establishWebSocketConnection();
            }
        }, delay);
    }

    disconnectWebSocket(): void {
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        this.gameId = null;
        this.onMessage = null;
        this.onConnectionChange = null;
        this.reconnectAttempts = 0;
    }
}

export const gameService = new GameService(); 