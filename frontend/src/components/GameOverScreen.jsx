import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import Confetti from './Confetti';
import { api } from '../api';
import { playSound } from '../utils/sound';
import './GameOverScreen.css';

const GameOverScreen = ({ session, persona, reason, onPlayAgain }) => {
    const [showConfetti, setShowConfetti] = useState(false);
    const [animatedStats, setAnimatedStats] = useState(false);
    const [showReport, setShowReport] = useState(false);
    const [leaderboard, setLeaderboard] = useState([]);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        if (reason === 'COMPLETED') {
            playSound('celebration');
            setShowConfetti(true);
        } else {
            playSound('gameOver');
        }

        api.getLeaderboard()
            .then(data => setLeaderboard(data.leaderboard || []))
            .catch(err => console.error('Failed to fetch leaderboard:', err));

        const timer = setTimeout(() => setAnimatedStats(true), 500);
        return () => clearTimeout(timer);
    }, [reason]);

    // Calculate derived stats
    const portfolioValue = Object.entries(session?.portfolio || {}).reduce((sum, [sector, units]) => {
        const price = session?.market_prices?.[sector] || 100;
        return sum + Math.round(units * price);
    }, 0);

    const totalNetWorth = (session?.wealth || 0) + portfolioValue;
    const startingWealth = 25000;
    const wealthGrowth = ((totalNetWorth - startingWealth) / startingWealth * 100).toFixed(1);
    const monthsSurvived = session?.current_month || 1;
    const survivalRate = ((monthsSurvived / 12) * 100).toFixed(0);

    // Credit Score Rating
    const getCreditRating = (score) => {
        if (score >= 750) return { label: 'Excellent', color: '#22c55e', grade: 'A+' };
        if (score >= 700) return { label: 'Good', color: '#84cc16', grade: 'A' };
        if (score >= 650) return { label: 'Fair', color: '#fbbf24', grade: 'B' };
        if (score >= 550) return { label: 'Poor', color: '#f97316', grade: 'C' };
        return { label: 'Very Poor', color: '#ef4444', grade: 'D' };
    };

    const creditRating = getCreditRating(session?.credit_score || 700);

    const getReasonEmoji = () => {
        switch (reason) {
            case 'BANKRUPTCY': return '💸';
            case 'BURNOUT': return '😫';
            case 'COMPLETED': return '🎉';
            default: return '🎮';
        }
    };

    const getReasonText = () => {
        switch (reason) {
            case 'BANKRUPTCY': return 'Bankruptcy - Ran out of money';
            case 'BURNOUT': return 'Burnout - Mental health depleted';
            case 'COMPLETED': return 'Successfully completed 12 months!';
            default: return 'Game Over';
        }
    };

    const getPersonaEmoji = () => {
        if (!persona) return '🎭';
        const emojiMap = {
            'The Warren Buffett': '🦅',
            'The Cautious Saver': '🐢',
            'The Balanced Spender': '⚖️',
            'The YOLO Enthusiast': '🎢',
            'The FOMO Victim': '😰',
            'The Financial Guru': '🧙',
            'The Survivor': '💪'
        };
        return emojiMap[persona.title] || '🎭';
    };

    const getMedal = (rank) => {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return `#${rank}`;
    };

    const handlePlayAgain = () => {
        playSound('click');
        onPlayAgain();
    };

    // Generate achievements based on performance
    const achievements = [];
    if (reason === 'COMPLETED') achievements.push({ icon: '🏆', title: 'Survivor', desc: 'Completed all 12 months' });
    if (session?.wealth >= 50000) achievements.push({ icon: '💰', title: 'Wealthy', desc: 'Ended with ₹50,000+' });
    if (session?.credit_score >= 750) achievements.push({ icon: '⭐', title: 'Credit Master', desc: 'Excellent credit score' });
    if (session?.happiness >= 80) achievements.push({ icon: '😊', title: 'Happy Camper', desc: 'High well-being score' });
    if (portfolioValue > 10000) achievements.push({ icon: '📈', title: 'Investor', desc: 'Built a stock portfolio' });
    if ((session?.debt || 0) === 0) achievements.push({ icon: '🆓', title: 'Debt Free', desc: 'No outstanding loans' });

    return (
        <>
            <Confetti isActive={showConfetti} duration={5000} />
            <div className="game-over-container">
                {/* Hero Section */}
                <div className="go-hero">
                    <div className={`go-persona-badge ${reason === 'COMPLETED' ? 'success' : 'failure'}`}>
                        <span className="go-persona-emoji">{getPersonaEmoji()}</span>
                    </div>
                    <h1 className={`go-title ${animatedStats ? 'animate-in' : ''}`}>
                        {persona?.title || 'Game Complete'}
                    </h1>
                    <p className="go-subtitle">{persona?.description || getReasonText()}</p>
                    <div className={`go-outcome-badge ${reason === 'COMPLETED' ? 'completed' : reason === 'BANKRUPTCY' ? 'bankrupt' : 'burnout'}`}>
                        {getReasonEmoji()} {getReasonText()}
                    </div>
                </div>

                {/* Quick Stats Grid */}
                <div className="go-stats-grid">
                    <div className={`go-stat-card ${animatedStats ? 'animate-in' : ''}`} style={{ animationDelay: '0.1s' }}>
                        <div className="go-stat-icon">💰</div>
                        <div className="go-stat-value" style={{ color: session?.wealth >= 0 ? '#22c55e' : '#ef4444' }}>
                            ₹{totalNetWorth.toLocaleString('en-IN')}
                        </div>
                        <div className="go-stat-label">Total Net Worth</div>
                        <div className="go-stat-change" style={{ color: wealthGrowth >= 0 ? '#22c55e' : '#ef4444' }}>
                            {wealthGrowth >= 0 ? '↑' : '↓'} {Math.abs(wealthGrowth)}% from start
                        </div>
                    </div>

                    <div className={`go-stat-card ${animatedStats ? 'animate-in' : ''}`} style={{ animationDelay: '0.2s' }}>
                        <div className="go-stat-icon">😊</div>
                        <div className="go-stat-value" style={{ color: session?.happiness >= 50 ? '#22c55e' : '#f97316' }}>
                            {session?.happiness || 0}%
                        </div>
                        <div className="go-stat-label">Well-being Index</div>
                        <div className="go-stat-subtitle">{session?.happiness >= 80 ? 'Thriving' : session?.happiness >= 50 ? 'Stable' : 'Struggling'}</div>
                    </div>

                    <div className={`go-stat-card ${animatedStats ? 'animate-in' : ''}`} style={{ animationDelay: '0.3s' }}>
                        <div className="go-stat-icon">📊</div>
                        <div className="go-stat-value" style={{ color: creditRating.color }}>
                            {session?.credit_score || 700}
                        </div>
                        <div className="go-stat-label">Credit Score</div>
                        <div className="go-stat-grade" style={{ background: creditRating.color }}>{creditRating.grade}</div>
                    </div>

                    <div className={`go-stat-card ${animatedStats ? 'animate-in' : ''}`} style={{ animationDelay: '0.4s' }}>
                        <div className="go-stat-icon">📅</div>
                        <div className="go-stat-value" style={{ color: '#8b5cf6' }}>
                            {monthsSurvived}/12
                        </div>
                        <div className="go-stat-label">Months Survived</div>
                        <div className="go-stat-progress">
                            <div className="go-stat-progress-fill" style={{ width: `${survivalRate}%` }}></div>
                        </div>
                    </div>
                </div>

                {/* Achievements */}
                {achievements.length > 0 && (
                    <div className="go-achievements">
                        <h3>🏅 Achievements Unlocked</h3>
                        <div className="go-achievements-grid">
                            {achievements.map((ach, i) => (
                                <div key={i} className="go-achievement">
                                    <span className="go-achievement-icon">{ach.icon}</span>
                                    <div className="go-achievement-info">
                                        <div className="go-achievement-title">{ach.title}</div>
                                        <div className="go-achievement-desc">{ach.desc}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Leaderboard Section */}
                <div className="go-leaderboard">
                    <h3>🏆 Leaderboard</h3>
                    {leaderboard.length === 0 ? (
                        <p className="go-leaderboard-empty">No entries yet. Be the first!</p>
                    ) : (
                        <div className="go-leaderboard-table">
                            <div className="go-leaderboard-header">
                                <span className="col-rank">Rank</span>
                                <span className="col-player">Player</span>
                                <span className="col-wealth">Wealth</span>
                                <span className="col-score">Score</span>
                                <span className="col-persona">Persona</span>
                            </div>
                            {leaderboard.slice(0, 10).map((entry, i) => (
                                <div key={i} className={`go-leaderboard-row ${entry.rank <= 3 ? 'top-three' : ''}`}>
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

                {/* Action Buttons */}
                <div className="go-actions">
                    <button className="go-btn go-btn-primary" onClick={handlePlayAgain}>
                        🔄 Play Again
                    </button>
                    <button className="go-btn go-btn-secondary" onClick={() => setShowReport(true)}>
                        📋 Detailed Report
                    </button>
                </div>

                {/* Detailed Report Modal */}
                {showReport && (
                    <div className="report-overlay" onClick={() => setShowReport(false)}>
                        <div className="report-container" onClick={e => e.stopPropagation()}>
                            <div className="report-header-bar">
                                <h2>📊 Financial Health Report</h2>
                                <button className="report-close" onClick={() => setShowReport(false)}>×</button>
                            </div>

                            {/* Report Tabs */}
                            <div className="report-tabs">
                                <button className={`report-tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>Overview</button>
                                <button className={`report-tab ${activeTab === 'analysis' ? 'active' : ''}`} onClick={() => setActiveTab('analysis')}>Analysis</button>
                                <button className={`report-tab ${activeTab === 'recommendations' ? 'active' : ''}`} onClick={() => setActiveTab('recommendations')}>Recommendations</button>
                                <button className={`report-tab ${activeTab === 'ai_report' ? 'active' : ''}`} onClick={() => setActiveTab('ai_report')}>AI Report</button>
                            </div>

                            <div className="report-body">
                                {activeTab === 'overview' && (
                                    <div className="report-tab-content">
                                        <div className="report-summary-card">
                                            <div className="report-persona-section">
                                                <span className="report-persona-emoji">{getPersonaEmoji()}</span>
                                                <div>
                                                    <h3>{persona?.title || 'Financial Explorer'}</h3>
                                                    <p>{persona?.description || 'You completed your financial journey.'}</p>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="report-metrics-grid">
                                            <div className="report-metric">
                                                <div className="metric-header">
                                                    <span>💵 Cash Balance</span>
                                                </div>
                                                <div className="metric-value">₹{(session?.wealth || 0).toLocaleString('en-IN')}</div>
                                            </div>
                                            <div className="report-metric">
                                                <div className="metric-header">
                                                    <span>📈 Portfolio Value</span>
                                                </div>
                                                <div className="metric-value">₹{portfolioValue.toLocaleString('en-IN')}</div>
                                            </div>
                                            <div className="report-metric">
                                                <div className="metric-header">
                                                    <span>💳 Debt</span>
                                                </div>
                                                <div className="metric-value" style={{ color: (session?.debt || 0) > 0 ? '#ef4444' : '#22c55e' }}>
                                                    ₹{(session?.debt || 0).toLocaleString('en-IN')}
                                                </div>
                                            </div>
                                            <div className="report-metric">
                                                <div className="metric-header">
                                                    <span>🧾 Monthly Bills</span>
                                                </div>
                                                <div className="metric-value">₹{(session?.recurring_expenses || 15000).toLocaleString('en-IN')}</div>
                                            </div>
                                        </div>

                                        {/* Portfolio Breakdown */}
                                        {portfolioValue > 0 && (
                                            <div className="report-section-card">
                                                <h4>📊 Investment Portfolio</h4>
                                                <div className="portfolio-breakdown">
                                                    {Object.entries(session?.portfolio || {}).filter(([_, units]) => units > 0).map(([sector, units]) => {
                                                        const price = session?.market_prices?.[sector] || 100;
                                                        const value = Math.round(units * price);
                                                        return (
                                                            <div key={sector} className="portfolio-item">
                                                                <span className="portfolio-sector">{sector.charAt(0).toUpperCase() + sector.slice(1)}</span>
                                                                <span className="portfolio-units">{units} units @ ₹{price}</span>
                                                                <span className="portfolio-value">₹{value.toLocaleString('en-IN')}</span>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeTab === 'analysis' && (
                                    <div className="report-tab-content">
                                        {/* Performance Gauges */}
                                        <div className="analysis-gauges">
                                            <div className="gauge-item">
                                                <div className="gauge-label">Wealth Growth</div>
                                                <div className="gauge-bar">
                                                    <div className="gauge-fill" style={{ width: `${Math.min(100, Math.max(0, Number(wealthGrowth) + 50))}%`, background: wealthGrowth >= 0 ? '#22c55e' : '#ef4444' }}></div>
                                                </div>
                                                <div className="gauge-value">{wealthGrowth}%</div>
                                            </div>
                                            <div className="gauge-item">
                                                <div className="gauge-label">Survival Rate</div>
                                                <div className="gauge-bar">
                                                    <div className="gauge-fill" style={{ width: `${survivalRate}%`, background: '#8b5cf6' }}></div>
                                                </div>
                                                <div className="gauge-value">{survivalRate}%</div>
                                            </div>
                                            <div className="gauge-item">
                                                <div className="gauge-label">Credit Health</div>
                                                <div className="gauge-bar">
                                                    <div className="gauge-fill" style={{ width: `${Math.min(100, ((session?.credit_score || 700) - 300) / 6)}%`, background: creditRating.color }}></div>
                                                </div>
                                                <div className="gauge-value">{creditRating.label}</div>
                                            </div>
                                            <div className="gauge-item">
                                                <div className="gauge-label">Well-being</div>
                                                <div className="gauge-bar">
                                                    <div className="gauge-fill" style={{ width: `${session?.happiness || 0}%`, background: session?.happiness >= 50 ? '#22c55e' : '#f97316' }}></div>
                                                </div>
                                                <div className="gauge-value">{session?.happiness}%</div>
                                            </div>
                                        </div>

                                        {/* Key Insights */}
                                        <div className="report-section-card">
                                            <h4>💡 Key Insights</h4>
                                            <div className="insights-list">
                                                <div className="insight-item">
                                                    <span className="insight-icon">📅</span>
                                                    <p>You survived <strong>{monthsSurvived} out of 12</strong> months in your first year as a working professional.</p>
                                                </div>
                                                <div className="insight-item">
                                                    <span className="insight-icon">💰</span>
                                                    <p>Starting with ₹25,000, your net worth {wealthGrowth >= 0 ? 'grew' : 'declined'} by <strong>{Math.abs(wealthGrowth)}%</strong> to ₹{totalNetWorth.toLocaleString('en-IN')}.</p>
                                                </div>
                                                {portfolioValue > 0 && (
                                                    <div className="insight-item">
                                                        <span className="insight-icon">📈</span>
                                                        <p>You invested in the stock market and built a portfolio worth <strong>₹{portfolioValue.toLocaleString('en-IN')}</strong>.</p>
                                                    </div>
                                                )}
                                                {(session?.debt || 0) > 0 && (
                                                    <div className="insight-item warning">
                                                        <span className="insight-icon">⚠️</span>
                                                        <p>You have outstanding debt of <strong>₹{session.debt.toLocaleString('en-IN')}</strong> that needs to be repaid.</p>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {activeTab === 'recommendations' && (
                                    <div className="report-tab-content">
                                        <div className="recommendations-grid">
                                            {session?.wealth < 15000 && (
                                                <div className="rec-card warning">
                                                    <div className="rec-header">
                                                        <span className="rec-icon">🛡️</span>
                                                        <h4>Build Emergency Fund</h4>
                                                    </div>
                                                    <p>Your savings are below the recommended 6-month expense buffer. Prioritize building an emergency fund of at least ₹90,000.</p>
                                                </div>
                                            )}
                                            {session?.credit_score < 700 && (
                                                <div className="rec-card warning">
                                                    <div className="rec-header">
                                                        <span className="rec-icon">💳</span>
                                                        <h4>Improve Credit Score</h4>
                                                    </div>
                                                    <p>A score below 700 limits your loan options. Pay bills on time, avoid high-interest loans, and keep credit utilization low.</p>
                                                </div>
                                            )}
                                            {session?.happiness < 50 && (
                                                <div className="rec-card warning">
                                                    <div className="rec-header">
                                                        <span className="rec-icon">😊</span>
                                                        <h4>Work-Life Balance</h4>
                                                    </div>
                                                    <p>Don't sacrifice happiness for wealth. Budget for leisure activities and maintain social connections.</p>
                                                </div>
                                            )}
                                            <div className="rec-card success">
                                                <div className="rec-header">
                                                    <span className="rec-icon">📈</span>
                                                    <h4>Start a SIP</h4>
                                                </div>
                                                <p>Consider starting a Systematic Investment Plan (SIP) with ₹5,000/month for long-term wealth building through mutual funds.</p>
                                            </div>
                                            <div className="rec-card success">
                                                <div className="rec-header">
                                                    <span className="rec-icon">🏥</span>
                                                    <h4>Get Health Insurance</h4>
                                                </div>
                                                <p>Ensure you have adequate health insurance coverage. A sudden medical emergency can wipe out years of savings.</p>
                                            </div>
                                            <div className="rec-card success">
                                                <div className="rec-header">
                                                    <span className="rec-icon">📚</span>
                                                    <h4>Continue Learning</h4>
                                                </div>
                                                <p>Financial literacy is key. Visit NCFE (ncfe.org.in) and RBI's financial education portal for free resources.</p>
                                            </div>
                                        </div>

                                        {/* Resources */}
                                        <div className="report-section-card">
                                            <h4>🔗 Helpful Resources</h4>
                                            <div className="resources-grid">
                                                <a href="https://www.ncfe.org.in/" target="_blank" rel="noopener noreferrer" className="resource-link-card">
                                                    <span>🏛️</span>
                                                    <div>
                                                        <strong>NCFE</strong>
                                                        <p>National Centre for Financial Education</p>
                                                    </div>
                                                </a>
                                                <a href="https://www.rbi.org.in/commonman/" target="_blank" rel="noopener noreferrer" className="resource-link-card">
                                                    <span>🏦</span>
                                                    <div>
                                                        <strong>RBI For Common Man</strong>
                                                        <p>Financial literacy by Reserve Bank</p>
                                                    </div>
                                                </a>
                                                <a href="https://www.paisabazaar.com/cibil-credit-score/" target="_blank" rel="noopener noreferrer" className="resource-link-card">
                                                    <span>📊</span>
                                                    <div>
                                                        <strong>Check CIBIL Score</strong>
                                                        <p>Free credit score check</p>
                                                    </div>
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {activeTab === 'ai_report' && (
                                    <div className="report-tab-content">
                                        <div className="report-section-card report-markdown">
                                            {session?.final_report ? (
                                                <ReactMarkdown>{session.final_report}</ReactMarkdown>
                                            ) : (
                                                <p>No AI report is available for this session yet.</p>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="report-footer">
                                <button className="go-btn go-btn-secondary" onClick={() => window.print()}>
                                    🖨️ Print Report
                                </button>
                                <button className="go-btn go-btn-primary" onClick={() => setShowReport(false)}>
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
};

export default GameOverScreen;
