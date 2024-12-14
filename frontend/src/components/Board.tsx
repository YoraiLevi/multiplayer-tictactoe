import React from 'react';
import { Board as BoardType, PlayerSymbol } from '../types/game';
import './Board.css';

interface BoardProps {
    board: BoardType;
    isMyTurn: boolean;
    onCellClick: (row: number, col: number) => void;
}

export const Board: React.FC<BoardProps> = ({ board, isMyTurn, onCellClick }) => {
    const getCellClass = (value: PlayerSymbol | null) => {
        let className = 'cell';
        if (value) {
            className += ` cell-${value.toLowerCase()}`;
        }
        if (isMyTurn && !value) {
            className += ' cell-clickable';
        }
        return className;
    };

    return (
        <div className="board">
            {board.map((row, rowIndex) => (
                <div key={rowIndex} className="board-row">
                    {row.map((cell, colIndex) => (
                        <div
                            key={`${rowIndex}-${colIndex}`}
                            className={getCellClass(cell)}
                            onClick={() => isMyTurn && !cell && onCellClick(rowIndex, colIndex)}
                        >
                            {cell}
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
}; 