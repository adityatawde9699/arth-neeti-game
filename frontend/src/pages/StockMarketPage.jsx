import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../contexts/SessionContext';
import { api } from '../api';
import StockTicker from '../components/StockTicker';
import LoadingSkeleton from '../components/LoadingSkeleton';
import './StockMarketPage.css';

const StockMarketPage = ({ onBuy, onSell }) => {
    const navigate = useNavigate();
    const { session } = useSession();
    const [marketData, setMarketData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('stocks');
    const [message, setMessage] = useState(null);

    // Form States
    const [mfAmount, setMfAmount] = useState('');
    const [fnoSector, setFnoSector] = useState('tech');
    const [fnoUnits, setFnoUnits] = useState('');
    const [fnoDuration, setFnoDuration] = useState('1');
    const [ipoAmount, setIpoAmount] = useState('');

    useEffect(() => {
        if (session?.id) {
            fetchMarketData();
        }
    }, [session?.id]);

    const fetchMarketData = async () => {
        try {
            setIsLoading(true);
            const data = await api.getMarketStatus(session.id);
            setMarketData(data);
        } catch (err) {
            setError('Failed to load market data');
            if (import.meta.env.DEV) console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAction = async (actionFn) => {
        try {
            setIsLoading(true);
            setMessage(null);
            const result = await actionFn();
            if (result.message) {
                setMessage({ type: 'success', text: result.message });
                fetchMarketData(); // Refresh data
            }
        } catch (err) {
            setMessage({ type: 'error', text: err.message });
        } finally {
            setIsLoading(false);
        }
    };

    // --- RENDER HELPERS ---

    const renderTabs = () => (
        <div className="market-tabs">
            <button
                className={`tab-btn ${activeTab === 'stocks' ? 'active' : ''}`}
                onClick={() => setActiveTab('stocks')}
            >
                Stocks
            </button>
            <button
                className={`tab-btn ${activeTab === 'mf' ? 'active' : ''}`}
                onClick={() => setActiveTab('mf')}
            >
                Mutual Funds
            </button>
            <button
                className={`tab-btn ${activeTab === 'ipo' ? 'active' : ''}`}
                onClick={() => setActiveTab('ipo')}
            >
                IPOs
            </button>
            <button
                className={`tab-btn ${activeTab === 'fno' ? 'active risk' : ''}`}
                onClick={() => setActiveTab('fno')}
            >
                Futures (F&O) ⚠️
            </button>
        </div>
    );

    const renderStocks = () => (
        <div className="tab-content">
            <div className="market-info-card">
                <h2>Market Overview</h2>
                <div className="info-grid">
                    <div className="info-item">
                        <span className="label">Current Wealth</span>
                        <span className="value wealth">₹{session.wealth?.toLocaleString() || 0}</span>
                    </div>
                    <div className="info-item">
                        <span className="label">Portfolio Value</span>
                        <span className="value portfolio">
                            ₹{marketData?.total_portfolio_value?.toLocaleString() || 0}
                        </span>
                    </div>
                </div>
            </div>
            <StockTicker session={session} onBuy={onBuy} onSell={onSell} />
            <div className="market-tips">
                <h3>💡 Investment Tips</h3>
                <ul>
                    <li>Diversify your portfolio across different sectors</li>
                    <li>Don't invest more than you can afford to lose</li>
                    <li>Market prices fluctuate - buy low, sell high</li>
                </ul>
            </div>
        </div>
    );

    const renderMutualFunds = () => {
        const funds = [
            { key: 'NIFTY50', name: 'Nifty 50 Index Fund', risk: 'Low', desc: 'Safe, steady growth.' },
            { key: 'MIDCAP', name: 'MidCap Opportunities', risk: 'Medium', desc: 'Balanced risk/reward.' },
            { key: 'SMALLCAP', name: 'SmallCap Discovery', risk: 'High', desc: 'High risk, high return.' }
        ];

        return (
            <div className="tab-content">
                <h2>Mutual Funds (SIPs)</h2>
                <div className="mf-grid">
                    {funds.map(fund => {
                        const nav = marketData?.market_prices?.[`MF_${fund.key}`] || 100;
                        const holdings = marketData?.mutual_funds?.[fund.key] || { units: 0, invested: 0 };
                        const currentValue = holdings.units * nav;

                        return (
                            <div key={fund.key} className="mf-card">
                                <div className="mf-header">
                                    <h3>{fund.name}</h3>
                                    <span className={`risk-tag ${fund.risk.toLowerCase()}`}>{fund.risk} Risk</span>
                                </div>
                                <p className="mf-desc">{fund.desc}</p>
                                <div className="mf-stats">
                                    <div className="stat">
                                        <span className="label">NAV</span>
                                        <span className="value">₹{nav.toFixed(2)}</span>
                                    </div>
                                    <div className="stat">
                                        <span className="label">Units Held</span>
                                        <span className="value">{holdings.units.toFixed(2)}</span>
                                    </div>
                                    <div className="stat">
                                        <span className="label">Current Value</span>
                                        <span className="value">₹{currentValue.toFixed(0)}</span>
                                    </div>
                                </div>
                                <div className="mf-actions">
                                    <input
                                        type="number"
                                        placeholder="Amount (₹)"
                                        className="input-field"
                                        onChange={(e) => setMfAmount(e.target.value)}
                                    />
                                    <div className="btn-group">
                                        <button
                                            className="btn-primary"
                                            onClick={() => handleAction(() => api.investMutualFund(session.id, fund.key, parseInt(mfAmount)))}
                                        >
                                            Invest
                                        </button>
                                        <button
                                            className="btn-secondary"
                                            onClick={() => handleAction(() => api.redeemMutualFund(session.id, fund.key, 1))} // Simplification: redeem 1 unit or logic needed
                                            title="Redeem logic simplified for demo"
                                        >
                                            Redeem
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    };

    const renderIPOs = () => {
        const schedule = marketData?.ipo_schedule || {};
        const currentMonth = session.current_month;
        const activeIPOs = marketData?.active_ipos || [];

        return (
            <div className="tab-content">
                <h2>IPO Dashboard</h2>
                <div className="ipo-list">
                    {Object.entries(schedule).map(([monthStr, details]) => {
                        const month = parseInt(monthStr);
                        const isOpen = month === currentMonth;
                        const isPast = month < currentMonth;
                        const isFuture = month > currentMonth;

                        const application = activeIPOs.find(app => app.name === details.name);

                        return (
                            <div key={details.name} className={`ipo-card ${isOpen ? 'open' : ''} ${isPast ? 'closed' : ''}`}>
                                <div className="ipo-header">
                                    <h3>{details.name} IPO</h3>
                                    {isOpen && <span className="status-badge open">OPEN NOW</span>}
                                    {isFuture && <span className="status-badge future">Month {month}</span>}
                                    {isPast && <span className="status-badge closed">CLOSED</span>}
                                </div>
                                <div className="ipo-details">
                                    <p>Price Band: ₹{details.price_band}</p>
                                    <p>Listing Chance: {(details.listing_gain_prob * 100).toFixed(0)}% Profit</p>
                                </div>
                                {application ? (
                                    <div className="application-status">
                                        Status: <strong>{application.status}</strong> (Invested: ₹{application.amount})
                                    </div>
                                ) : (
                                    isOpen && (
                                        <div className="ipo-actions">
                                            <input
                                                type="number"
                                                placeholder="Amount (15k - 2L)"
                                                className="input-field"
                                                value={ipoAmount}
                                                onChange={(e) => setIpoAmount(e.target.value)}
                                            />
                                            <button
                                                className="btn-primary"
                                                onClick={() => handleAction(() => api.applyIPO(session.id, details.name, parseInt(ipoAmount)))}
                                            >
                                                Apply
                                            </button>
                                        </div>
                                    )
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    };

    const renderFnO = () => (
        <div className="tab-content">
            <div className="fno-warning">
                <h3>⚠️ High Risk Warning</h3>
                <p>Futures & Options are leveraged products. You can lose more than your investment. proceed with caution.</p>
            </div>

            <div className="fno-panel">
                <h3>Short Selling (Futures)</h3>
                <p>Bet against a sector falling in price.</p>

                <div className="trade-form">
                    <div className="form-group">
                        <label>Sector</label>
                        <select
                            value={fnoSector}
                            onChange={(e) => setFnoSector(e.target.value)}
                            className="input-field"
                        >
                            <option value="tech">Tech</option>
                            <option value="gold">Gold</option>
                            <option value="real_estate">Real Estate</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Units to Short</label>
                        <input
                            type="number"
                            className="input-field"
                            value={fnoUnits}
                            onChange={(e) => setFnoUnits(e.target.value)}
                        />
                    </div>
                    <div className="form-group">
                        <label>Duration (Months)</label>
                        <select
                            value={fnoDuration}
                            onChange={(e) => setFnoDuration(e.target.value)}
                            className="input-field"
                        >
                            <option value="1">1 Month</option>
                            <option value="3">3 Months</option>
                        </select>
                    </div>

                    <button
                        className="btn-danger"
                        onClick={() => handleAction(() => api.tradeFutures(session.id, fnoSector, fnoUnits, fnoDuration))}
                    >
                        Short Sell (Bearish)
                    </button>
                </div>
            </div>
        </div>
    );

    if (!session) return (
        <div className="stock-market-page"><div className="error-message">No Session</div></div>
    );

    return (
        <div className="stock-market-page">
            <div className="page-header">
                <button onClick={() => navigate(-1)} className="back-button">← Back</button>
                <h1>Dalal Street</h1>
            </div>

            {renderTabs()}

            {message && (
                <div className={`message-banner ${message.type}`}>
                    {message.text}
                </div>
            )}

            {isLoading && !marketData ? (
                <div className="loading-container"><LoadingSkeleton variant="card" /></div>
            ) : (
                <div className="market-container">
                    {activeTab === 'stocks' && renderStocks()}
                    {activeTab === 'mf' && renderMutualFunds()}
                    {activeTab === 'ipo' && renderIPOs()}
                    {activeTab === 'fno' && renderFnO()}
                </div>
            )}
        </div>
    );
};

export default StockMarketPage;
