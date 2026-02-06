import React, { useState, useEffect } from 'react';
import { api } from '../api';
import './GameOverScreen.css'; // Reuse the new styles

const Leaderboard = () => {
    const [leaderboard, setLeaderboard] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getLeaderboard()
            .then(data => {
                setLeaderboard(data.leaderboard || []);
                setLoading(false);
            })
            .catch(err => {
                console.error('Failed to fetch leaderboard:', err);
                setLoading(false);
            });
    }, []);

    const getMedal = (rank) => {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return `#${rank}`;
    };

    if (loading) return <div className="go-leaderboard-empty">Loading scores...</div>;

    return (
        <div className="go-leaderboard" style={{ maxWidth: '100%', margin: 0, background: 'transparent', border: 'none', boxShadow: 'none' }}>
            <h3>🏆 Hall of Fame</h3>
            {leaderboard.length === 0 ? (
                <p className="go-leaderboard-empty">No players yet. Be the first to complete the game!</p>
            ) : (
                <div className="go-leaderboard-table">
                    <div className="go-leaderboard-header">
                        <span className="col-rank">Rank</span>
                        <span className="col-player">Player</span>
                        <span className="col-wealth">Wealth</span>
                        <span className="col-score">Score</span>
                        <span className="col-persona">Persona</span>
                    </div>
                    {leaderboard.map((entry) => (
                        <div
                            key={entry.rank}
                            className={`go-leaderboard-row ${entry.rank <= 3 ? 'top-three' : ''}`}
                        >
                            <span className="col-rank">{getMedal(entry.rank)}</span>
                            <span className="col-player">{entry.player_name}</span>
                            <span className="col-wealth">₹{(entry.wealth || 0).toLocaleString('en-IN')}</span>
                            <span className="col-score">{entry.score?.toLocaleString() || 0}</span>
                            <span className="col-persona">{entry.persona || '-'}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Leaderboard;
