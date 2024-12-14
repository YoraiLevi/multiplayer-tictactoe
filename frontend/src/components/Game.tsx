import React, { useEffect, useState, useCallback } from 'react';
import { Board } from './Board';
import { gameService } from '../services/gameService';
import { GameState, PlayerSymbol } from '../types/game';
import './Game.css';

const POLLING_INTERVAL = 1000; // Poll every second

// UUID validation regex
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const Game: React.FC = () => {
    const [gameState, setGameState] = useState<GameState | null>(null);
    const [playerId, setPlayerId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [gameId, setGameId] = useState<string | null>(null);
    const [pollingInterval, setPollingInterval] = useState<NodeJS.Timer | null>(null);
    const [joinGameId, setJoinGameId] = useState('');
    const [isValidGameId, setIsValidGameId] = useState(false);

    // Validate game ID input
    const handleGameIdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setJoinGameId(value);
        setIsValidGameId(UUID_REGEX.test(value));
        setError(null);
    };

    // Polling function to get game state
    const pollGameState = useCallback(async () => {
        if (!gameId) return;
        
        try {
            const newState = await gameService.getGameState(gameId);
            setGameState(newState);
            setError(null);
        } catch (err) {
            console.error('Error polling game state:', err);
            setError('Failed to get game state');
        }
    }, [gameId]);

    // Start polling when game is created/joined
    useEffect(() => {
        if (gameId) {
            // Initial poll
            pollGameState();
            
            // Set up polling interval
            const interval = setInterval(pollGameState, POLLING_INTERVAL);
            setPollingInterval(interval);
            
            // Cleanup polling on unmount or when gameId changes
            return () => {
                if (interval) {
                    clearInterval(interval);
                }
            };
        }
    }, [gameId, pollGameState]);

    const setupGame = async (game: GameState) => {
        console.log('Setting up game:', game);
        setGameState(game);
        setPlayerId(game.player_id!);
        setGameId(game.game_id);
        setError(null);
    };

    const createGame = async () => {
        try {
            const game = await gameService.createGame();
            await setupGame(game);
        } catch (err) {
            setError('Failed to create game');
            console.error(err);
        }
    };

    const joinGame = async () => {
        if (!isValidGameId) return;

        try {
            const game = await gameService.joinGame(joinGameId);
            await setupGame(game);
        } catch (err) {
            setError('Failed to join game');
            console.error(err);
        }
    };

    const handleCellClick = async (row: number, col: number) => {
        if (!gameState || !playerId || !isMyTurn()) return;

        try {
            await gameService.makeMove(gameState.game_id, {
                player_id: playerId,
                position: [row, col]
            });
            setError(null);
            
            // Poll immediately after making a move
            await pollGameState();
        } catch (err: any) {
            setError(err.response?.data?.error?.message || 'Failed to make move');
            console.error(err);
        }
    };

    const isMyTurn = (): boolean => {
        if (!gameState || !playerId) return false;
        if (gameState.player_count !== 2) return false;
        return gameState.current_turn === getMySymbol();
    };

    const getMySymbol = (): PlayerSymbol | null => {
        if (!gameState || !playerId) return null;
        return gameState.player_id === playerId ? 'X' : 'O';
    };

    const resetGame = () => {
        setGameState(null);
        setPlayerId(null);
        setGameId(null);
        setError(null);
        setJoinGameId('');
        setIsValidGameId(false);
        if (pollingInterval) {
            clearInterval(pollingInterval);
            setPollingInterval(null);
        }
    };

    const copyGameId = (gameId: string) => {
        navigator.clipboard.writeText(gameId)
            .then(() => {
                // Could add a toast notification here
                console.log('Game ID copied to clipboard');
            })
            .catch(err => {
                console.error('Failed to copy game ID:', err);
            });
    };

    const getGameStatus = (): JSX.Element | string => {
        if (!gameState) return '';

        if (gameState.status === 'finished') {
            return (
                <>
                    <div>
                        {gameState.winner 
                            ? (gameState.winner === getMySymbol() ? 'You won!' : 'You lost!')
                            : 'Game ended in a draw!'}
                    </div>
                    <button onClick={resetGame} className="new-game-button">
                        New Game
                    </button>
                </>
            );
        }

        if (gameState.status === 'waiting') {
            return (
                <>
                    <div>Waiting for opponent</div>
                    <div className="game-id-container">
                        <div className="game-id-label">Share this game ID:</div>
                        <div className="game-id-wrapper">
                            <input 
                                type="text" 
                                readOnly 
                                value={gameState.game_id} 
                                className="game-id"
                            />
                            <button 
                                onClick={() => copyGameId(gameState.game_id)}
                                className="copy-button"
                                title="Copy game ID"
                            >
                                📋
                            </button>
                        </div>
                    </div>
                    <div className="player-count">
                        Players in game: {gameState.player_count}/2
                    </div>
                </>
            );
        }

        return isMyTurn() ? 'Your turn!' : "Opponent's turn";
    };

    return (
        <div className="game">
            <h1>Tic-tac-toe</h1>
            
            {!gameState ? (
                <div className="game-menu">
                    <button onClick={createGame}>Create Game</button>
                    <div className="join-game-container">
                        <input
                            type="text"
                            value={joinGameId}
                            onChange={handleGameIdChange}
                            placeholder="Enter game ID"
                            className={`game-id-input ${isValidGameId ? 'valid' : ''}`}
                        />
                        <button 
                            onClick={joinGame}
                            disabled={!isValidGameId}
                            className={!isValidGameId ? 'disabled' : ''}
                        >
                            Join Game
                        </button>
                    </div>
                    {error && <p className="error">{error}</p>}
                </div>
            ) : (
                <>
                    <div className="game-info">
                        <div className="status">{getGameStatus()}</div>
                        <p className="player-info">You are: {getMySymbol()}</p>
                        {error && <p className="error">{error}</p>}
                    </div>
                    
                    <Board
                        board={gameState.board}
                        isMyTurn={isMyTurn()}
                        onCellClick={handleCellClick}
                    />
                </>
            )}
        </div>
    );
}; 