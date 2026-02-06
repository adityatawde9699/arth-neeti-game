import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import './ProfileScreen.css';

export default function ProfileScreen({ onBack, onLogout }) {
    const navigate = useNavigate();
    const [profileData, setProfileData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await api.getProfile();
                setProfileData(data);
            } catch (err) {
                setError('Failed to load profile.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchProfile();
    }, []);

    if (isLoading) {
        return (
            <div className="profile-page">
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Loading profile...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="profile-page">
                <div className="error-container">
                    <p>{error}</p>
                    <button onClick={onBack || (() => navigate('/'))} className="btn-primary">
                        Back
                    </button>
                </div>
            </div>
        );
    }

    const { profile, game_history } = profileData;
    const username = localStorage.getItem('username') || 'Player';

    return (
        <div className="profile-page">
            {/* Header */}
            <div className="profile-header">
                <button
                    onClick={onBack || (() => navigate('/'))}
                    className="back-button"
                >
                    ← Back
                </button>
                <div className="header-content">
                    <h1>Player Profile</h1>
                    <p className="subtitle">Your financial journey overview</p>
                </div>
            </div>

            {/* Profile Card */}
            <div className="profile-card">
                <div className="profile-avatar">
                    <div className="avatar-circle">
                        {username.charAt(0).toUpperCase()}
                    </div>
                </div>
                <div className="profile-info">
                    <h2 className="profile-name">{username}</h2>
                    <p className="profile-email">Member since {new Date().getFullYear()}</p>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon games">🎮</div>
                    <div className="stat-content">
                        <span className="stat-label">Games Played</span>
                        <span className="stat-value">{profile.total_games || 0}</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon wealth">💰</div>
                    <div className="stat-content">
                        <span className="stat-label">Highest Wealth</span>
                        <span className="stat-value">₹{profile.highest_wealth?.toLocaleString() || 0}</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon score">💳</div>
                    <div className="stat-content">
                        <span className="stat-label">Best Credits</span>
                        <span className="stat-value">{profile.highest_score || 0}/100</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon credit">📊</div>
                    <div className="stat-content">
                        <span className="stat-label">Best Credit Score</span>
                        <span className="stat-value">{profile.highest_credit_score || 700}</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon wellbeing">😊</div>
                    <div className="stat-content">
                        <span className="stat-label">Best Well-being</span>
                        <span className="stat-value">{profile.highest_happiness || 0}%</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon stocks">📈</div>
                    <div className="stat-content">
                        <span className="stat-label">Highest Stock Profits</span>
                        <span className="stat-value">₹{profile.highest_stock_profit?.toLocaleString() || 0}</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon persona">👤</div>
                    <div className="stat-content">
                        <span className="stat-label">Favorite Persona</span>
                        <span className="stat-value">{profile.favorite_persona || 'N/A'}</span>
                    </div>
                </div>
            </div>

            {/* Logout Action */}
            <div className="profile-actions">
                <button onClick={onLogout} className="logout-button">
                    <span>🚪</span> Logout
                </button>
            </div>

            {/* Tabs */}
            <div className="tabs-container">
                <button
                    className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    Overview
                </button>
                <button
                    className={`tab ${activeTab === 'history' ? 'active' : ''}`}
                    onClick={() => setActiveTab('history')}
                >
                    Game History
                </button>
                <button
                    className={`tab ${activeTab === 'achievements' ? 'active' : ''}`}
                    onClick={() => setActiveTab('achievements')}
                >
                    Achievements
                </button>
            </div>

            {/* Tab Content */}
            <div className="tab-content">
                {activeTab === 'overview' && (
                    <div className="overview-section">
                        <div className="section-card">
                            <h3>Financial Summary</h3>
                            <div className="summary-grid">
                                <div className="summary-item">
                                    <span className="summary-label">Total Games</span>
                                    <span className="summary-value">{profile.total_games || 0}</span>
                                </div>
                                <div className="summary-item">
                                    <span className="summary-label">Average Score</span>
                                    <span className="summary-value">
                                        {profile.average_score ? Math.round(profile.average_score) : 0}/100
                                    </span>
                                </div>
                                <div className="summary-item">
                                    <span className="summary-label">Completion Rate</span>
                                    <span className="summary-value">
                                        {profile.completion_rate ? `${Math.round(profile.completion_rate)}%` : '0%'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'history' && (
                    <div className="history-section">
                        {game_history && game_history.length > 0 ? (
                            <div className="history-table">
                                <div className="table-header">
                                    <div className="table-cell">Date</div>
                                    <div className="table-cell">Persona</div>
                                    <div className="table-cell">Wealth</div>
                                    <div className="table-cell">Score</div>
                                    <div className="table-cell">Outcome</div>
                                </div>
                                {game_history.map((game) => (
                                    <div key={game.id} className="table-row">
                                        <div className="table-cell">
                                            {new Date(game.ended_at).toLocaleDateString()}
                                        </div>
                                        <div className="table-cell persona-cell">
                                            {game.persona || 'Unknown'}
                                        </div>
                                        <div className="table-cell wealth-cell">
                                            ₹{game.final_wealth?.toLocaleString() || 0}
                                        </div>
                                        <div className="table-cell">
                                            <div className="score-container">
                                                <span className={`score-value ${game.financial_literacy_score >= 80 ? 'excellent' :
                                                    game.financial_literacy_score >= 50 ? 'good' : 'poor'
                                                    }`}>
                                                    {game.financial_literacy_score || 0}
                                                </span>
                                                <div className="score-bar">
                                                    <div
                                                        className={`score-fill ${game.financial_literacy_score >= 80 ? 'excellent' :
                                                            game.financial_literacy_score >= 50 ? 'good' : 'poor'
                                                            }`}
                                                        style={{ width: `${Math.min(100, game.financial_literacy_score || 0)}%` }}
                                                    ></div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="table-cell">
                                            <span className={`outcome-badge ${game.end_reason === 'COMPLETED' ? 'completed' :
                                                game.end_reason === 'BANKRUPTCY' ? 'bankruptcy' : 'other'
                                                }`}>
                                                {game.end_reason?.replace('_', ' ') || 'Unknown'}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="empty-state">
                                <div className="empty-icon">📊</div>
                                <p>No games played yet</p>
                                <p className="empty-subtitle">Start your first game to see your history here</p>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'achievements' && (
                    <div className="achievements-section">
                        {profile.badges && profile.badges.length > 0 ? (
                            <div className="badges-grid">
                                {profile.badges.map((badge, index) => (
                                    <div key={index} className="badge-card">
                                        <div className="badge-icon">🏆</div>
                                        <div className="badge-name">{badge}</div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="empty-state">
                                <div className="empty-icon">🎖️</div>
                                <p>No achievements yet</p>
                                <p className="empty-subtitle">Complete games with high scores to earn badges</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
