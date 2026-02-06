import React from 'react';
import { useNavigate } from 'react-router-dom';
import './GameHeader.css';

/**
 * Game screen header: app title with spark icon (left), Quit button (right).
 * Matches design: dark slate bar, rounded corners, purple title, white Quit + refresh icon.
 */
export default function GameHeader() {
    const navigate = useNavigate();

    return (
        <header className="game-header">
            <div className="game-header-inner">
                <div className="game-header-brand">
                    <span className="game-header-icon" aria-hidden>₹</span>
                    <h1 className="game-header-title">Arth Neeti</h1>
                </div>
                <button
                    type="button"
                    className="game-header-quit"
                    onClick={() => navigate('/')}
                    aria-label="Quit game"
                >
                    <span className="game-header-quit-icon" aria-hidden>↻</span>
                    <span>Quit</span>
                </button>
            </div>
        </header>
    );
}
