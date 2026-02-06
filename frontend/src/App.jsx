import { useState, useCallback, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { api } from './api';
import { SessionProvider, useSession } from './contexts/SessionContext';
import GameStats from './components/GameStats';
import GameHeader from './components/GameHeader';
import ScenarioCard from './components/ScenarioCard';
import FeedbackModal from './components/FeedbackModal';
import HomePage from './components/HomePage';
import GameOverScreen from './components/GameOverScreen';
import ParticleBackground from './components/ParticleBackground';
import StockMarketPage from './pages/StockMarketPage';
import LoanPage from './pages/LoanPage';
import AuthPage from './components/AuthPage';
import ProfileScreen from './components/ProfileScreen';
import './App.css';
import './components/ReportModal.css';

// Game states
const GAME_STATE = {
    PLAYING: 'playing',
    FEEDBACK: 'feedback',
    GAME_OVER: 'game_over',
    LOADING: 'loading',
};

const SESSION_STORAGE_KEY = 'arthneeti_session_id';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
    const token = localStorage.getItem('auth_token');
    return token ? children : <Navigate to="/auth/login" replace />;
};

// Game Component (handles game logic)
function GameComponent() {
    const navigate = useNavigate();
    const { session, updateSession } = useSession();
    const [gameState, setGameState] = useState(GAME_STATE.LOADING);
    const [currentCard, setCurrentCard] = useState(null);
    const [feedback, setFeedback] = useState(null);
    const [gameOverData, setGameOverData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lang, setLang] = useState('en');

    useEffect(() => {
        const initGame = async () => {
            const savedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);
            if (savedSessionId) {
                try {
                    const sessionData = await api.getSession(savedSessionId);
                    if (sessionData.session && sessionData.session.is_active) {
                        updateSession(sessionData.session);
                        const cardData = await api.getCard(savedSessionId);
                        if (!cardData.game_complete) {
                            setCurrentCard(cardData.card);
                            setGameState(GAME_STATE.PLAYING);
                            return;
                        } else {
                            localStorage.removeItem(SESSION_STORAGE_KEY);
                        }
                    } else {
                        localStorage.removeItem(SESSION_STORAGE_KEY);
                    }
                } catch (err) {
                    console.log('Could not resume session:', err);
                    localStorage.removeItem(SESSION_STORAGE_KEY);
                }
            }
            setGameState(GAME_STATE.PLAYING);
        };
        initGame();
    }, [updateSession]);

    const handleChoiceSelect = useCallback(async (choice) => {
        if (!session || !currentCard) return;

        setIsLoading(true);
        try {
            const result = await api.submitChoice(session.id, currentCard.id, choice.id);
            updateSession(result.session);
            setFeedback({
                text: result.feedback,
                wasRecommended: result.was_recommended,
            });
            setGameState(GAME_STATE.FEEDBACK);

            if (result.game_over) {
                setGameOverData({
                    reason: result.game_over_reason,
                    persona: result.final_persona,
                });
            }
        } catch (err) {
            setError('Failed to submit choice');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    }, [session, currentCard, updateSession]);

    const handleContinue = useCallback(async () => {
        if (gameOverData) {
            setGameState(GAME_STATE.GAME_OVER);
            return;
        }

        setIsLoading(true);
        try {
            const cardData = await api.getCard(session.id);

            if (cardData.game_complete) {
                setGameOverData({
                    reason: 'COMPLETED',
                    persona: null,
                });
                setGameState(GAME_STATE.GAME_OVER);
            } else {
                setCurrentCard(cardData.card);
                setGameState(GAME_STATE.PLAYING);
            }
        } catch (err) {
            setError('Failed to get next card');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    }, [session, gameOverData]);

    const handleUseLifeline = useCallback(async (cardId) => {
        if (!session) return null;
        try {
            const result = await api.useLifeline(session.id, cardId);
            if (result.session) {
                updateSession(result.session);
            }
            return result;
        } catch (err) {
            console.error('Failed to use lifeline:', err);
            return null;
        }
    }, [session, updateSession]);

    const handleTakeLoan = useCallback(async (loanType) => {
        if (!session) return null;
        try {
            const result = await api.takeLoan(session.id, loanType);
            if (result.session) {
                updateSession(result.session);
            }
            return result;
        } catch (err) {
            console.error('Failed to take loan:', err);
            return null;
        }
    }, [session, updateSession]);

    const handleGetAIAdvice = useCallback(async (cardId) => {
        if (!session) return null;
        try {
            const result = await api.getAIAdvice(session.id, cardId);
            return result;
        } catch (err) {
            console.error('Failed to get AI advice:', err);
            return null;
        }
    }, [session]);

    const handleBuyStock = useCallback(async (sector, amount) => {
        if (!session) return null;
        try {
            const result = await api.buyStock(session.id, sector, amount);
            if (result.session) updateSession(result.session);
            return result;
        } catch (err) {
            console.error('Failed to buy stock:', err);
            return { error: err.message };
        }
    }, [session, updateSession]);

    const handleSellStock = useCallback(async (sector, units) => {
        if (!session) return null;
        try {
            const result = await api.sellStock(session.id, sector, units);
            if (result.session) updateSession(result.session);
            return result;
        } catch (err) {
            console.error('Failed to sell stock:', err);
            return { error: err.message };
        }
    }, [session, updateSession]);

    const handleSkipCard = useCallback(async (cardId) => {
        if (!session || !cardId) return;
        setCurrentCard(null);
        setIsLoading(true);

        try {
            const result = await api.skipCard(session.id, cardId);
            if (result.session) {
                updateSession(result.session);
            }

            const cardData = await api.getCard(session.id);
            if (cardData.game_complete) {
                setGameOverData({
                    reason: 'COMPLETED',
                    persona: cardData.persona || null,
                });
                setGameState(GAME_STATE.GAME_OVER);
            } else if (cardData.card) {
                setCurrentCard(cardData.card);
            }
        } catch (err) {
            console.error('Failed to skip card:', err);
        } finally {
            setIsLoading(false);
        }
    }, [session, updateSession]);

    const { clearSession } = useSession();
    const handlePlayAgain = useCallback(() => {
        clearSession();
        setCurrentCard(null);
        setFeedback(null);
        setGameOverData(null);
        setError(null);
        navigate('/');
    }, [navigate, clearSession]);

    if (error) {
        return (
            <div className="container flex-col-center">
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
                <h2 style={{ marginBottom: '1rem' }}>Connection Error</h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>{error}</p>
                <button className="btn btn-primary" onClick={() => setError(null)}>
                    Try Again
                </button>
                <button className="btn btn-secondary mt-4" onClick={() => navigate('/')}>
                    Go Home
                </button>
            </div>
        );
    }

    if (gameState === GAME_STATE.GAME_OVER) {
        return (
            <GameOverScreen
                session={session}
                persona={gameOverData?.persona}
                reason={gameOverData?.reason}
                onPlayAgain={handlePlayAgain}
            />
        );
    }

    if (gameState === GAME_STATE.FEEDBACK) {
        return (
            <>
                <div className="container" style={{ paddingTop: '2rem' }}>
                    <GameStats session={session} />
                </div>
                <FeedbackModal
                    feedback={feedback?.text}
                    wasRecommended={feedback?.wasRecommended}
                    onContinue={handleContinue}
                />
            </>
        );
    }

    return (
        <div className="container game-container" style={{ paddingTop: '1rem', paddingBottom: '2rem' }}>
            <GameHeader />
            <div className="game-toolbar">
                <div className="language-toggle">
                    <span>Language:</span>
                    <div className="language-buttons">
                        <button
                            type="button"
                            className={lang === 'en' ? 'active' : ''}
                            onClick={() => setLang('en')}
                        >
                            En
                        </button>
                        <button
                            type="button"
                            className={lang === 'hi' ? 'active' : ''}
                            onClick={() => setLang('hi')}
                        >
                            Hi
                        </button>
                    </div>
                </div>
                <div className="game-toolbar-links">
                    <button type="button" onClick={() => navigate('/stock-market')} className="game-toolbar-btn">
                        Stock Market
                    </button>
                    <button type="button" onClick={() => navigate('/loans')} className="game-toolbar-btn">
                        Loans
                    </button>
                    <button type="button" onClick={() => navigate('/profile')} className="game-toolbar-btn">
                        Profile
                    </button>
                </div>
            </div>

            <GameStats session={session} />
            <ScenarioCard
                card={currentCard}
                onChoiceSelect={handleChoiceSelect}
                disabled={isLoading}
                session={session}
                onUseLifeline={handleUseLifeline}
                onTakeLoan={handleTakeLoan}
                onGetAIAdvice={handleGetAIAdvice}
                onSkipCard={handleSkipCard}
                lang={lang}
            />
        </div>
    );
};

// Main App Component
function AppRoutes() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const { session, startGame, updateSession, clearSession } = useSession();
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        setIsAuthenticated(!!token);
        setIsLoading(false);
    }, []);

    const handleStartGame = useCallback(async () => {
        setIsLoading(true);
        try {
            const newSession = await startGame();
            navigate('/game');
        } catch (err) {
            console.error('Failed to start game:', err);
        } finally {
            setIsLoading(false);
        }
    }, [navigate, startGame]);

    const handleLoginSuccess = useCallback((data) => {
        setIsAuthenticated(true);
        navigate('/');
    }, [navigate]);

    const handleLogout = useCallback(() => {
        clearSession();
        localStorage.removeItem('auth_token');
        localStorage.removeItem('username');
        setIsAuthenticated(false);
        navigate('/auth/login', { replace: true });
    }, [navigate, clearSession]);

    const handleBuyStock = useCallback(async (sector, amount) => {
        if (!session) return null;
        try {
            const result = await api.buyStock(session.id, sector, amount);
            if (result.session) updateSession(result.session);
            return result;
        } catch (err) {
            return { error: err.message };
        }
    }, [session, updateSession]);

    const handleSellStock = useCallback(async (sector, units) => {
        if (!session) return null;
        try {
            const result = await api.sellStock(session.id, sector, units);
            if (result.session) updateSession(result.session);
            return result;
        } catch (err) {
            return { error: err.message };
        }
    }, [session, updateSession]);

    const handleTakeLoan = useCallback(async (loanType) => {
        if (!session) return null;
        try {
            const result = await api.takeLoan(session.id, loanType);
            if (result.session) {
                updateSession(result.session);
            }
            return result;
        } catch (err) {
            return { error: err.message };
        }
    }, [session, updateSession]);

    if (isLoading) {
        return (
            <div className="loading-screen">
                <div className="loading-spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }

    return (
        <div className="app">
            <ParticleBackground intensity="normal" />
            <Routes>
                <Route path="/auth/login" element={
                    <AuthPage mode="login" onSuccess={handleLoginSuccess} onSwitchMode={() => navigate('/auth/register')} />
                } />
                <Route path="/auth/register" element={
                    <AuthPage mode="register" onSuccess={handleLoginSuccess} onSwitchMode={() => navigate('/auth/login')} />
                } />
                <Route path="/" element={
                    <ProtectedRoute>
                        <HomePage onStartGame={handleStartGame} isLoading={isLoading} username={localStorage.getItem('username')} />
                    </ProtectedRoute>
                } />
                <Route path="/game" element={
                    <ProtectedRoute>
                        <GameComponent />
                    </ProtectedRoute>
                } />
                <Route path="/stock-market" element={
                    <ProtectedRoute>
                        <StockMarketPage onBuy={handleBuyStock} onSell={handleSellStock} />
                    </ProtectedRoute>
                } />
                <Route path="/loans" element={
                    <ProtectedRoute>
                        <LoanPage onTakeLoan={handleTakeLoan} />
                    </ProtectedRoute>
                } />
                <Route path="/profile" element={
                    <ProtectedRoute>
                        <ProfileScreen onLogout={handleLogout} />
                    </ProtectedRoute>
                } />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </div>
    );
}

// Router Wrapper
function App() {
    return (
        <Router>
            <SessionProvider>
                <AppRoutes />
            </SessionProvider>
        </Router>
    );
}

export default App;
