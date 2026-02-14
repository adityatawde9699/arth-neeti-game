import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../contexts/SessionContext';
import { api } from '../api';
import './LoanPage.css';

const LOAN_TYPES = {
    FAMILY: {
        name: 'Family Loan',
        amount: 5000,
        interest: 0,
        description: 'Borrow from family - no interest, impacts happiness',
        color: 'green'
    },
    INSTANT_APP: {
        name: 'Instant Loan App',
        amount: 10000,
        interest: 5,
        description: 'Quick loan - high interest, damages credit score',
        color: 'red'
    },
    BANK: {
        name: 'Bank Personal Loan',
        amount: 100000,
        interest: 1.2,
        description: 'Standard loan. Requires Credit Score > 750',
        color: 'blue'
    }
};

const LoanPage = ({ onTakeLoan }) => {
    const navigate = useNavigate();
    const { session } = useSession();
    const [selectedLoan, setSelectedLoan] = useState(null);
    const [customAmount, setCustomAmount] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState(null);

    if (!session) {
        return (
            <div className="loan-page">
                <div className="page-header">
                    <button onClick={() => navigate(-1)} className="back-button">
                        ← Back
                    </button>
                    <h1>Loan Center</h1>
                </div>
                <div className="error-message">
                    <p>No active game session. Please start a game first.</p>
                    <button onClick={() => navigate('/')} className="btn-primary">
                        Go to Home
                    </button>
                </div>
            </div>
        );
    }

    const handleLoanRequest = async (loanType, amount) => {
        setIsLoading(true);
        setMessage(null);

        try {
            const result = await onTakeLoan(loanType);
            if (result && result.message) {
                setMessage({ type: 'success', text: result.message });
                setTimeout(() => {
                    setSelectedLoan(null);
                    setMessage(null);
                }, 2000);
            } else if (result && result.error) {
                setMessage({ type: 'error', text: result.error });
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Failed to process loan request' });
        } finally {
            setIsLoading(false);
        }
    };

    const currentDebt = session.debt || 0;
    const monthlyIncome = 10000; // Assuming fixed salary

    return (
        <div className="loan-page">
            <div className="page-header">
                <button onClick={() => navigate(-1)} className="back-button">
                    ← Back
                </button>
                <div className="header-content">
                    <h1>Loan Center</h1>
                    <p className="subtitle">Borrow wisely - understand the risks</p>
                </div>
            </div>

            <div className="loan-content">
                {/* Current Financial Status */}
                <div className="status-card">
                    <h2>Your Financial Status</h2>
                    <div className="status-grid">
                        <div className="status-item">
                            <span className="label">Current Wealth</span>
                            <span className="value wealth">₹{session.wealth?.toLocaleString() || 0}</span>
                        </div>
                        <div className="status-item">
                            <span className="label">Monthly Income</span>
                            <span className="value income">₹{monthlyIncome.toLocaleString()}</span>
                        </div>
                        <div className="status-item">
                            <span className="label">Current Debt</span>
                            <span className="value debt">₹{currentDebt.toLocaleString()}</span>
                        </div>
                        <div className="status-item">
                            <span className="label">Credit Score</span>
                            <span className="value credit">{session.credit_score || 700}</span>
                        </div>
                    </div>
                </div>

                {/* Loan Options */}
                <div className="loan-options-section">
                    <h2>Available Loans</h2>
                    <div className="loan-cards">
                        {Object.entries(LOAN_TYPES).map(([key, loan]) => (
                            <div key={key} className={`loan-card ${loan.color}`}>
                                <div className="loan-header">
                                    <h3>{loan.name}</h3>
                                    <div className={`loan-badge ${loan.color}`}>
                                        {loan.interest}% APR
                                    </div>
                                </div>
                                <div className="loan-details">
                                    <div className="loan-amount">
                                        <span className="label">Loan Amount</span>
                                        <span className="value">₹{loan.amount.toLocaleString()}</span>
                                    </div>
                                    <p className="loan-description">{loan.description}</p>
                                    <div className="loan-terms">
                                        <div className="term-item">
                                            <span>Interest Rate:</span>
                                            <span>{loan.interest}% per month</span>
                                        </div>
                                        <div className="term-item">
                                            <span>Monthly Payment:</span>
                                            <span>₹{Math.round(loan.amount * (loan.interest / 100)).toLocaleString()}</span>
                                        </div>
                                    </div>
                                </div>
                                <button
                                    onClick={() => handleLoanRequest(key, loan.amount)}
                                    disabled={isLoading}
                                    className={`loan-button ${loan.color}`}
                                >
                                    {isLoading ? 'Processing...' : `Apply for ${loan.name}`}
                                </button>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Loan Information */}
                <div className="loan-info-card">
                    <h3>⚠️ Important Loan Information</h3>
                    <ul>
                        <li>Loans increase your debt and reduce your credit score</li>
                        <li>Interest payments are deducted monthly from your wealth</li>
                        <li>High debt can lead to bankruptcy</li>
                        <li>Only take loans when absolutely necessary</li>
                        <li>Pay off loans as soon as possible to improve credit</li>
                    </ul>
                </div>

                {/* Message Display */}
                {message && (
                    <div className={`message-banner ${message.type}`}>
                        <span>{message.type === 'success' ? '✅' : '⚠️'}</span>
                        <span>{message.text}</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LoanPage;
