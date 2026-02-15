import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';
import BudgetDisplay from './BudgetDisplay';
import LanguageSwitcher from './LanguageSwitcher';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import GameSetupModal from './GameSetupModal';

const HomePage = ({ onStartGame, isLoading, username }) => {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const [showModal, setShowModal] = useState(false);

    // Data moved inside component to allow dynamic translation
    const expenses = [
        { id: 1, name: t('home.budget.rent'), amount: 10000, category: 'HOUSING', is_essential: true },
        { id: 2, name: t('home.budget.groceries'), amount: 2500, category: 'FOOD', is_essential: true },
        { id: 3, name: t('home.budget.utilities'), amount: 1000, category: 'UTILITIES', is_essential: true },
        { id: 4, name: t('home.budget.transport'), amount: 1000, category: 'TRANSPORT', is_essential: true },
    ];

    return (
        <div className="home-page">
            {/* Profile Icon */}
            <div className="profile-icon-container">
                <button onClick={() => navigate('/profile')} className="profile-icon-btn" aria-label="Profile">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                </button>
            </div>

            {/* Language Switcher */}
            <div className="home-lang-switcher" style={{ position: 'absolute', top: '1rem', right: '1rem', zIndex: 10 }}>
                <LanguageSwitcher />
            </div>

            {/* Hero Section */}
            <div className="hero-section">
                <div className="hero-icon">💼💰</div>
                <h1 className="hero-title">Arth-Neeti</h1>
                <p className="hero-subtitle">{t('home.hero.subtitle')}</p>
                <p className="hero-description">{t('home.hero.description')}</p>
                <button className="cta-button" onClick={() => setShowModal(true)} disabled={isLoading}>
                    {isLoading ? (
                        <>
                            <span className="loading-spinner-small"></span>
                            Starting...
                        </>
                    ) : (
                        <>
                            <span className="play-icon">▶</span>
                            {t('common.start_game')}
                        </>
                    )}
                </button>
            </div>

            {/* Info Cards */}
            <div className="info-cards-section">
                <div className="info-cards-row">
                    {/* Objective Card */}
                    <div className="info-card">
                        <div className="card-icon red">🎯</div>
                        <h3 className="card-title">{t('home.mission.title')}</h3>
                        <div className="card-content">
                            <p className="mission-text">{t('home.mission.text')}</p>
                            <div className="danger-badges">
                                <span className="badge danger-badge">{t('home.mission.bankruptcy')}</span>
                                <span className="badge warning-badge">{t('home.mission.burnout')}</span>
                            </div>
                            <p className="reward-text">{t('home.mission.reward')}</p>
                        </div>
                    </div>

                    {/* Stats Card */}
                    <div className="info-card">
                        <div className="card-icon blue">📊</div>
                        <h3 className="card-title">{t('home.stats.title')}</h3>
                        <div className="card-content">
                            <ul className="stats-list">
                                <li><span className="stat-emoji">💰</span> <strong>{t('common.wealth')}</strong> - {t('home.stats.wealth_desc')}</li>
                                <li><span className="stat-emoji">😊</span> <strong>{t('common.happiness')}</strong> - {t('home.stats.happiness_desc')}</li>
                                <li><span className="stat-emoji">📊</span> <strong>{t('common.credit_score')}</strong> - {t('home.stats.credit_desc')}</li>
                                <li><span className="stat-emoji">🧾</span> <strong>{t('home.stats.bills')}</strong> - {t('home.stats.bills_desc')}</li>
                            </ul>
                        </div>
                    </div>
                </div>

                {/* How to Play Card */}
                <div className="info-card full-width">
                    <div className="card-icon green">🎮</div>
                    <h3 className="card-title">{t('home.how_to.title')}</h3>
                    <div className="card-content game-loop">
                        <div className="loop-step">
                            <div className="step-number">1</div>
                            <div className="step-content">
                                <h4>📋 {t('home.how_to.step1_title')}</h4>
                                <p>{t('home.how_to.step1_desc')}</p>
                            </div>
                        </div>
                        <div className="loop-arrow">→</div>
                        <div className="loop-step">
                            <div className="step-number">2</div>
                            <div className="step-content">
                                <h4>🤔 {t('home.how_to.step2_title')}</h4>
                                <p>{t('home.how_to.step2_desc')}</p>
                            </div>
                        </div>
                        <div className="loop-arrow">→</div>
                        <div className="loop-step">
                            <div className="step-number">3</div>
                            <div className="step-content">
                                <h4>💵 {t('home.how_to.step3_title')}</h4>
                                <p>{t('home.how_to.step3_desc')}</p>
                            </div>
                        </div>
                        <div className="loop-arrow">→</div>
                        <div className="loop-step">
                            <div className="step-number">4</div>
                            <div className="step-content">
                                <h4>🔄 {t('home.how_to.step4_title')}</h4>
                                <p>{t('home.how_to.step4_desc')}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Budget Preview */}
            <div className="budget-preview-section" style={{ maxWidth: '800px', margin: '0 auto 2rem auto', padding: '0 1rem' }}>
                <BudgetDisplay expenses={expenses} totalMonthlyDrain={14500} />
            </div>

            {/* Features (Goals) Section */}
            <div className="goals-section">
                <div className="goal-card">
                    <div className="goal-icon blue">📈</div>
                    <h3 className="goal-title">{t('home.features.stock.title')}</h3>
                    <div className="goal-info">
                        <span className="goal-label">{t('home.features.stock.label')}</span>
                        <span className="goal-amount blue">{t('home.features.stock.value')}</span>
                    </div>
                    <p className="goal-description">{t('home.features.stock.desc')}</p>
                </div>
                <div className="goal-card">
                    <div className="goal-icon green">🏦</div>
                    <h3 className="goal-title">{t('home.features.loans.title')}</h3>
                    <div className="goal-info">
                        <span className="goal-label">{t('home.features.loans.label')}</span>
                        <span className="goal-amount green">{t('home.features.loans.value')}</span>
                    </div>
                    <p className="goal-description">{t('home.features.loans.desc')}</p>
                </div>
                <div className="goal-card">
                    <div className="goal-icon purple">💡</div>
                    <h3 className="goal-title">{t('home.features.lifelines.title')}</h3>
                    <div className="goal-info">
                        <span className="goal-label">{t('home.features.lifelines.label')}</span>
                        <span className="goal-amount purple">{t('home.features.lifelines.value')}</span>
                    </div>
                    <p className="goal-description">{t('home.features.lifelines.desc')}</p>
                </div>
            </div>

            {/* Pro Tips */}
            <div className="tips-section">
                <h3 className="tips-title">💡 {t('home.tips.title')}</h3>
                <div className="tips-grid">
                    <div className="tip-item">
                        <span className="tip-icon">🚫</span>
                        <span>{t('home.tips.tip1')}</span>
                    </div>
                    <div className="tip-item">
                        <span className="tip-icon">🛡️</span>
                        <span>{t('home.tips.tip2')}</span>
                    </div>
                    <div className="tip-item">
                        <span className="tip-icon">⚠️</span>
                        <span>{t('home.tips.tip3')}</span>
                    </div>
                    <div className="tip-item">
                        <span className="tip-icon">📊</span>
                        <span>{t('home.tips.tip4')}</span>
                    </div>
                </div>
            </div>
            {/* Game Setup Modal */}
            <GameSetupModal
                isOpen={showModal}
                onClose={() => setShowModal(false)}
                onConfirm={(data) => {
                    setShowModal(false);
                    onStartGame(data);
                }}
            />
        </div>
    );
};

export default HomePage;
