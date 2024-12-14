export type PlayerSymbol = 'X' | 'O';
export type GameStatus = 'waiting' | 'in_progress' | 'finished';
export type Board = (PlayerSymbol | null)[][];

export interface GameState {
    game_id: string;
    player_id?: string;
    board: Board;
    current_turn?: PlayerSymbol;
    status: GameStatus;
    winner?: PlayerSymbol | null;
    player_count: number;
}

export interface GameMove {
    player_id: string;
    position: [number, number];
} 