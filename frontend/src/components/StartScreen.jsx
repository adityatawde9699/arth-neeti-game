import React from 'react';

const StartScreen = ({ onStartGame, isLoading }) => {
    return (
        <div className="start-screen">
            <div className="start-logo">🏦</div>

            <h1 className="start-title">Arth-Neeti</h1>
            <p className="start-subtitle">
                The Strategy of Wealth — Navigate your first 5 years of career.
                Make smart decisions. Build your future.
            </p>

            <div className="start-features">
                <div className="feature-item glass">
                    <div className="feature-icon">💰</div>
                    <div className="feature-title">Manage Wealth</div>
                    <div className="feature-desc">Starting salary: ₹25,000/month</div>
                </div>

                <div className="feature-item glass">
                    <div className="feature-icon">😊</div>
                    <div className="feature-title">Stay Happy</div>
                    <div className="feature-desc">Balance work and life</div>
                </div>

                <div className="feature-item glass">
                    <div className="feature-icon">📊</div>
                    <div className="feature-title">Build Credit</div>
                    <div className="feature-desc">Make smart financial choices</div>
                </div>
            </div>

            <button
                className="btn btn-primary btn-lg animate-pulse"
                onClick={onStartGame}
                disabled={isLoading}
            >
                {isLoading ? (
                    <>
                        <span className="loading-spinner" style={{ width: 20, height: 20 }}></span>
                        Starting...
                    </>
                ) : (
                    '🎮 Start Game'
                )}
            </button>

            <p style={{ marginTop: '2rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                Learn financial literacy through real-life scenarios
            </p>
        </div>
    );
};

export default StartScreen;
