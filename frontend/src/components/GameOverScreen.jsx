import React from 'react';

const GameOverScreen = ({ session, persona, reason, onPlayAgain }) => {
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
            case 'BANKRUPTCY': return 'You ran out of money!';
            case 'BURNOUT': return 'You burned out from stress!';
            case 'COMPLETED': return 'You completed 5 years!';
            default: return 'Game Over';
        }
    };

    const [showReport, setShowReport] = React.useState(false);

    const getPersonaEmoji = () => {
        if (!persona) return '🎭';
        switch (persona.title) {
            case 'The Warren Buffett': return '🦅';
            case 'The Cautious Saver': return '🐢';
            case 'The Balanced Spender': return '⚖️';
            case 'The YOLO Enthusiast': return '🎢';
            case 'The FOMO Victim': return '😰';
            default: return '🎭';
        }
    };

    return (
        <div className="game-over-screen">
            <div className="persona-card glass">
                <div className="persona-icon">{getPersonaEmoji()}</div>

                <h2 className="persona-title">
                    {persona?.title || 'Game Complete'}
                </h2>

                <p className="persona-description">
                    {persona?.description || getReasonText()}
                </p>

                <div className="final-stats">
                    <div className="final-stat">
                        <div className={`final-stat-value ${session?.wealth > 0 ? 'text-success' : 'text-danger'}`}>
                            ₹{session?.wealth?.toLocaleString('en-IN') || 0}
                        </div>
                        <div className="final-stat-label">Final Wealth</div>
                    </div>

                    <div className="final-stat">
                        <div className={`final-stat-value ${session?.happiness > 50 ? 'text-success' : 'text-warning'}`}>
                            {session?.happiness || 0}%
                        </div>
                        <div className="final-stat-label">Happiness</div>
                    </div>

                    <div className="final-stat">
                        <div className="final-stat-value text-primary">
                            {session?.credit_score || 700}
                        </div>
                        <div className="final-stat-label">Credit Score</div>
                    </div>

                    <div className="final-stat">
                        <div className="final-stat-value text-gold">
                            {session?.current_month || 1}
                        </div>
                        <div className="final-stat-label">Months Survived</div>
                    </div>
                </div>
            </div>

            {/* Report Modal */}
            {showReport && (
                <div className="report-modal-overlay">
                    <div className="report-modal glass">
                        <h2>📊 Financial Health Report</h2>
                        <div className="report-content">
                            <div className="report-section">
                                <h3>Performance Summary</h3>
                                <p><strong>Net Worth:</strong> ₹{session.wealth.toLocaleString('en-IN')}</p>
                                <p><strong>Credit Score:</strong> {session.credit_score} (Excellent is 750+)</p>
                                <p><strong>Financial Knowledge:</strong> {session.financial_literacy || 50}/100</p>
                            </div>

                            <div className="report-section">
                                <h3>Key Recommendations</h3>
                                <ul>
                                    <li>Based on your gameplay:</li>
                                    {session.wealth < 10000 && <li>⚠️ <strong>Emergency Fund:</strong> Your savings are low. Aim for 6 months of expenses.</li>}
                                    {session.credit_score < 700 && <li>⚠️ <strong>Credit Health:</strong> Avoid unnecessary loans and pay bills on time.</li>}
                                    {session.happiness < 50 && <li>⚠️ <strong>Life Balance:</strong> Don't sacrifice happiness for money. Budget for fun!</li>}
                                    <li>✅ <strong>Investment:</strong> Consider starting a SIP for long-term wealth.</li>
                                    <li>✅ <strong>Insurance:</strong> Ensure you have adequate health and term insurance.</li>
                                </ul>
                            </div>

                            <div className="report-section">
                                <h3>Resources (NCFE)</h3>
                                <p>Learn more about financial planning:</p>
                                <ul>
                                    <li><a href="https://www.ncfe.org.in/" target="_blank" rel="noopener noreferrer">National Centre for Financial Education</a></li>
                                    <li><a href="https://www.rbi.org.in/commonman/" target="_blank" rel="noopener noreferrer">RBI - For Common Man</a></li>
                                </ul>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                            <button className="btn btn-primary" onClick={() => window.print()}>🖨️ Print Certificate</button>
                            <button className="btn btn-secondary" onClick={() => setShowReport(false)}>Close</button>
                        </div>
                    </div>
                </div>
            )}

            <div className="flex gap-md" style={{ marginTop: '1rem' }}>
                <button className="btn btn-primary btn-lg" onClick={onPlayAgain}>
                    🔄 Play Again
                </button>
                <button className="btn btn-secondary btn-lg" onClick={() => setShowReport(true)}>
                    📄 Download Report
                </button>
            </div>

            <p style={{ marginTop: '2rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                {getReasonEmoji()} {getReasonText()}
            </p>
        </div>
    );
};

export default GameOverScreen;
