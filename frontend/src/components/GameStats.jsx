import React, { useEffect, useState, useRef } from 'react';
import { playSound } from '../utils/sound';

const GameStats = ({ session }) => {
    const [prevSession, setPrevSession] = useState(null);
    const [flashState, setFlashState] = useState({});

    // Track previous values to detect changes
    useEffect(() => {
        if (!session) return;

        if (prevSession) {
            const newFlashState = {};
            let soundPlayed = false;

            // Check Wealth
            if (session.wealth !== prevSession.wealth) {
                const diff = session.wealth - prevSession.wealth;
                newFlashState.wealth = diff > 0 ? 'flash-green' : 'flash-red';
                if (!soundPlayed) {
                    playSound(diff > 0 ? 'success' : 'error');
                    soundPlayed = true;
                }
            }

            // Check Happiness
            if (session.happiness !== prevSession.happiness) {
                newFlashState.happiness = session.happiness > prevSession.happiness ? 'flash-green' : 'flash-red';
            }

            // Check Credit
            if (session.credit_score !== prevSession.credit_score) {
                newFlashState.credit = session.credit_score > prevSession.credit_score ? 'flash-green' : 'flash-red';
            }

            setFlashState(newFlashState);

            // Clear flash after animation
            const timer = setTimeout(() => {
                setFlashState({});
            }, 1000);

            return () => clearTimeout(timer);
        }

        setPrevSession(session);
    }, [session]);

    if (!session) return null;

    const formatMoney = (amount) => {
        if (amount >= 100000) {
            return `₹${(amount / 100000).toFixed(1)}L`;
        }
        return `₹${amount.toLocaleString('en-IN')}`;
    };

    const getWealthClass = (wealth) => {
        if (wealth > 30000) return 'positive';
        if (wealth < 10000) return 'negative';
        return '';
    };

    const getHappinessClass = (happiness) => {
        if (happiness > 70) return 'positive';
        if (happiness < 30) return 'negative';
        if (happiness < 50) return 'warning';
        return '';
    };

    const getCreditClass = (credit) => {
        if (credit >= 750) return 'positive';
        if (credit < 600) return 'negative';
        return '';
    };

    return (
        <div className="stats-bar glass">
            <div className={`stat-item ${flashState.wealth || ''}`}>
                <span className="stat-label">💰 Wealth</span>
                <span className={`stat-value ${getWealthClass(session.wealth)}`}>
                    {formatMoney(session.wealth)}
                </span>
                <div className="progress-bar">
                    <div
                        className={`progress-bar-fill ${session.wealth > 20000 ? 'success' : session.wealth < 5000 ? 'danger' : 'warning'}`}
                        style={{ width: `${Math.min(100, (session.wealth / 50000) * 100)}%` }}
                    />
                </div>
            </div>

            <div className={`stat-item ${flashState.happiness || ''}`}>
                <span className="stat-label">😊 Happiness</span>
                <span className={`stat-value ${getHappinessClass(session.happiness)}`}>
                    {session.happiness}%
                </span>
                <div className="progress-bar">
                    <div
                        className={`progress-bar-fill ${session.happiness > 50 ? 'success' : session.happiness < 25 ? 'danger' : 'warning'}`}
                        style={{ width: `${session.happiness}%` }}
                    />
                </div>
            </div>

            <div className={`stat-item ${flashState.credit || ''}`}>
                <span className="stat-label">📊 Credit Score</span>
                <span className={`stat-value ${getCreditClass(session.credit_score)}`}>
                    {session.credit_score}
                </span>
                <div className="progress-bar">
                    <div
                        className={`progress-bar-fill ${session.credit_score >= 750 ? 'success' : session.credit_score < 600 ? 'danger' : 'primary'}`}
                        style={{ width: `${((session.credit_score - 300) / 600) * 100}%` }}
                    />
                </div>
            </div>

            <div className="month-indicator">
                <div>Month {session.current_month}</div>
                <span>Year {Math.ceil(session.current_month / 12)} of 1</span>
            </div>
        </div>
    );
};

export default GameStats;
