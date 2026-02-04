import React, { useState } from 'react';

const SECTORS = {
    gold: { name: 'Gold', icon: '🥇', color: 'text-yellow-400' },
    tech: { name: 'Tech', icon: '💻', color: 'text-cyan-400' },
    real_estate: { name: 'Real Estate', icon: '🏠', color: 'text-emerald-400' }
};

export default function StockTicker({ session, onBuy, onSell }) {
    // Track previous prices to trigger flash animations
    const [prevPrices, setPrevPrices] = React.useState({});
    const [flashStates, setFlashStates] = React.useState({});

    // Transaction State
    const [selectedSector, setSelectedSector] = useState(null);
    const [actionStart, setActionStart] = useState(null); // 'buy' or 'sell'
    const [amount, setAmount] = useState('');
    const [message, setMessage] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    React.useEffect(() => {
        if (session && session.market_prices) {
            const newFlashes = {};
            Object.keys(SECTORS).forEach(sector => {
                const prev = prevPrices[sector];
                const curr = session.market_prices[sector];
                if (prev && curr > prev) newFlashes[sector] = 'flash-green';
                if (prev && curr < prev) newFlashes[sector] = 'flash-red';
            });

            if (Object.keys(newFlashes).length > 0) {
                setFlashStates(newFlashes);
                // Clear flashes after animation
                setTimeout(() => setFlashStates({}), 1000);
            }
            setPrevPrices(session.market_prices);
        }
    }, [session?.market_prices]);

    if (!session) return null;

    const prices = session.market_prices || { gold: 100, tech: 100, real_estate: 100 };
    const portfolio = session.portfolio || { gold: 0, tech: 0, real_estate: 0 };
    const wealth = session.wealth;

    const handleAction = async () => {
        if (!amount || isNaN(amount) || Number(amount) <= 0) return;

        setIsLoading(true);
        setMessage(null);
        let result;

        try {
            if (actionStart === 'buy') {
                result = await onBuy(selectedSector, Number(amount));
            } else {
                result = await onSell(selectedSector, Number(amount));
            }

            if (result && result.message) {
                setMessage({ type: 'success', text: result.message });
                setAmount('');
                setTimeout(() => {
                    setMessage(null);
                    setActionStart(null);
                    setSelectedSector(null);
                }, 1500);
            } else if (result && result.error) {
                setMessage({ type: 'error', text: result.error });
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Transaction failed' });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="glass-panel rounded-2xl p-4 mb-6 relative overflow-hidden">
            <div className="flex items-center justify-between mb-4 relative z-10">
                <h3 className="text-lg font-bold text-slate-200 flex items-center gap-2">
                    <span className="text-xl">📈</span>
                    <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                        Stock Market
                    </span>
                </h3>
                <div className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-800/50 rounded-full border border-slate-700/50">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Live</span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 relative z-10">
                {Object.entries(SECTORS).map(([key, info]) => {
                    const price = prices[key] || 100;
                    const owned = portfolio[key] || 0;
                    const currentValue = owned * price;
                    const flashClass = flashStates[key] || '';

                    return (
                        <div key={key} className={`relative bg-slate-800/40 rounded-lg p-3 border border-slate-700/50 transition-all duration-300 hover:bg-slate-800/60 hover:border-slate-600 group ${flashClass}`}>
                            {/* Compact Header */}
                            <div className="flex items-center justify-between mb-2.5">
                                <div className="flex items-center gap-2">
                                    <div className="p-1.5 bg-slate-900/50 rounded-md text-lg group-hover:scale-110 transition-transform">
                                        {info.icon}
                                    </div>
                                    <div>
                                        <div className="text-sm font-bold text-slate-200">{info.name}</div>
                                        <div className={`text-base font-mono font-bold ${info.color} leading-none`}>₹{price}</div>
                                    </div>
                                </div>
                            </div>

                            {/* Compact Portfolio Info */}
                            <div className="flex justify-between items-center text-[11px] text-slate-400 bg-slate-900/30 px-2 py-1.5 rounded-md mb-2.5">
                                <span>Owned: <span className="text-white font-mono font-medium">{owned.toFixed(1)}</span></span>
                                <span>Value: <span className="text-emerald-400 font-mono font-medium">₹{currentValue.toLocaleString()}</span></span>
                            </div>

                            {/* Compact Action Buttons */}
                            <div className="grid grid-cols-2 gap-2">
                                <button
                                    onClick={() => { setSelectedSector(key); setActionStart('buy'); }}
                                    className="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-semibold py-1.5 rounded-md border border-emerald-500/20 hover:border-emerald-500/40 transition-all active:scale-95"
                                >
                                    Buy
                                </button>
                                <button
                                    onClick={() => { setSelectedSector(key); setActionStart('sell'); }}
                                    disabled={owned <= 0}
                                    className="bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-semibold py-1.5 rounded-md border border-red-500/20 hover:border-red-500/40 transition-all active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed disabled:active:scale-100"
                                >
                                    Sell
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Transaction Modal */}
            {selectedSector && actionStart && (
                <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
                    <div className="glass-panel border border-slate-700 rounded-3xl p-0 w-full max-w-sm shadow-2xl relative overflow-hidden animate-slide-up">
                        {/* Modal Header */}
                        <div className={`p-5 ${actionStart === 'buy' ? 'bg-emerald-500/10' : 'bg-red-500/10'} border-b border-slate-700/50`}>
                            <h4 className="text-xl font-bold text-white flex items-center gap-2.5">
                                <span className="text-2xl">{SECTORS[selectedSector].icon}</span>
                                <span>{actionStart === 'buy' ? 'Buy' : 'Sell'} {SECTORS[selectedSector].name}</span>
                            </h4>
                        </div>

                        <div className="p-5">
                            {/* Stats Panel */}
                            <div className="text-sm text-slate-300 mb-5 bg-slate-900/50 p-3.5 rounded-xl border border-slate-800 space-y-2">
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-500">Market Price</span>
                                    <span className={`font-mono font-bold ${SECTORS[selectedSector].color}`}>₹{prices[selectedSector]}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-500">Your Portfolio</span>
                                    <span className="font-mono">{portfolio[selectedSector] || 0} units</span>
                                </div>
                                <div className="h-px bg-slate-800 my-2"></div>
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-500">Available Cash</span>
                                    <span className="text-emerald-400 font-mono font-bold">₹{wealth.toLocaleString()}</span>
                                </div>
                            </div>

                            {message && (
                                <div className={`mb-5 p-2.5 rounded-xl text-sm font-medium flex items-center gap-2 ${message.type === 'error' ? 'bg-red-500/10 text-red-300 border border-red-500/20' : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'}`}>
                                    <span>{message.type === 'error' ? '🚫' : '✅'}</span>
                                    {message.text}
                                </div>
                            )}

                            <div className="mb-6">
                                <label className="block text-xs uppercase text-slate-500 font-bold mb-2 tracking-wider">
                                    {actionStart === 'buy' ? 'Investment Amount (₹)' : 'Units to Sell'}
                                </label>
                                <div className="relative">
                                    <input
                                        type="number"
                                        value={amount}
                                        onChange={(e) => setAmount(e.target.value)}
                                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3.5 text-lg text-white font-mono focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/50 transition-all placeholder:text-slate-600"
                                        placeholder="0"
                                        autoFocus
                                    />
                                    {actionStart === 'buy' && (
                                        <div className="absolute right-2 top-2 bottom-2 flex items-center gap-1">
                                            {[1000, 5000].map(val => (
                                                <button
                                                    key={val}
                                                    onClick={() => setAmount(String(val))}
                                                    className="h-full px-2.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-medium text-emerald-400 border border-slate-700 transition-colors"
                                                >
                                                    +{val / 1000}k
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => { setSelectedSector(null); setActionStart(null); setMessage(null); setAmount(''); }}
                                    className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-semibold transition-colors border border-slate-700"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleAction}
                                    disabled={isLoading || !amount || Number(amount) <= 0}
                                    className={`flex-1 py-3 rounded-xl font-bold text-white shadow-lg transition-all transform active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed ${actionStart === 'buy'
                                        ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-emerald-900/20'
                                        : 'bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 shadow-red-900/20'
                                        }`}
                                >
                                    {isLoading ? 'Processing...' : (actionStart === 'buy' ? 'Confirm Buy' : 'Confirm Sell')}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}