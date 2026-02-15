import { useState, useCallback, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { api } from './api';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { logout } from './services/authService';
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
import ChatOverlay from './components/ChatOverlay';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSkeleton from './components/LoadingSkeleton';
import { useGameActions } from './hooks/useGameActions';
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
    const { currentUser } = useAuth();
    return currentUser ? children : <Navigate to="/auth/login" replace />;
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
    const [chatbotData, setChatbotData] = useState(null);

    useEffect(() => {
        const initGame = async () => {
            const savedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);
            if (savedSessionId) {
                try {
                    const sessionData = await api.getSession(savedSessionId);
                    if (sessionData.session && sessionData.session.is_active) {
                        updateSession(sessionData.session);
                        // Use i18nextLng key to get the correct language set by the switcher
                        const language = localStorage.getItem('i18nextLng') || 'en';
                        const cardData = await api.getCard(savedSessionId, language);
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
                    if (import.meta.env.DEV) console.log('Could not resume session:', err);
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

            // Show chatbot if triggered
            if (result.chatbot) {
                setChatbotData(result.chatbot);
            }

            if (result.game_over) {
                setGameOverData({
                    reason: result.game_over_reason,
                    persona: result.final_persona,
                });
            }
        } catch (err) {
            setError('Failed to submit choice');
            if (import.meta.env.DEV) console.error(err);
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
            // Use i18nextLng key to get the correct language set by the switcher
            const language = localStorage.getItem('i18nextLng') || 'en';
            const cardData = await api.getCard(session.id, language);

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
            setError(err.message || 'Failed to get next card');
            if (import.meta.env.DEV) console.error(err);
        } finally {
            setIsLoading(false);
        }
    }, [session, gameOverData]);

    // Use custom hook for game actions
    const {
        handleUseLifeline,
        handleTakeLoan,
        handleGetAIAdvice,
        handleBuyStock,
        handleSellStock,
    } = useGameActions();

    const handleSkipCard = useCallback(async (cardId) => {
        if (!session || !cardId) return;
        setCurrentCard(null);
        setIsLoading(true);

        try {
            const result = await api.skipCard(session.id, cardId);
            if (result.session) {
                updateSession(result.session);
            }

            const language = localStorage.getItem('i18nextLng') || 'en';
            const cardData = await api.getCard(session.id, language);
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
            if (import.meta.env.DEV) console.error('Failed to skip card:', err);
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

            {isLoading ? (
                <div className="card-container">
                    <LoadingSkeleton variant="card" />
                </div>
            ) : (
                <ScenarioCard
                    card={currentCard}
                    onChoiceSelect={handleChoiceSelect}
                    disabled={isLoading}
                    session={session}
                    onUseLifeline={handleUseLifeline}
                    onTakeLoan={handleTakeLoan}
                    onGetAIAdvice={handleGetAIAdvice}
                    onSkipCard={handleSkipCard}
                />
            )}

            {chatbotData && (
                <ChatOverlay
                    chatbotData={chatbotData}
                    sessionId={session?.id}
                    onDismiss={() => setChatbotData(null)}
                    onSessionUpdate={updateSession}
                />
            )}
        </div>
    );
};

// Main App Component
function AppRoutes() {
    const { currentUser } = useAuth();
    const { session, startGame, updateSession, clearSession } = useSession();
    const navigate = useNavigate();

    // Remove legacy auth checks
    useEffect(() => {
        // Optional: Any auth-dependent side effects
    }, [currentUser]);

    // Use a ref for synchronous checking to prevent double-clicks
    const isStartingRef = useRef(false);
    const [isStarting, setIsStarting] = useState(false);

    const handleStartGame = useCallback(async (formData) => {
        if (isStartingRef.current) return;

        isStartingRef.current = true;
        setIsStarting(true);

        try {
            await startGame(formData);
            navigate('/game');
        } catch (err) {
            if (import.meta.env.DEV) console.error('Failed to start game:', err);
            // Only reset if failed, so user can try again. 
            // If success, we navigate away so no need to reset immediately
            isStartingRef.current = false;
            setIsStarting(false);
        }
    }, [navigate, startGame]);

    const handleLoginSuccess = useCallback(() => {
        navigate('/');
    }, [navigate]);

    const handleLogout = useCallback(async () => {
        try {
            await logout();
            clearSession();
            navigate('/auth/login', { replace: true });
        } catch (error) {
            if (import.meta.env.DEV) console.error('Logout failed:', error);
        }
    }, [navigate, clearSession]);

    // Use custom hook for game actions
    const {
        handleTakeLoan,
        handleBuyStock,
        handleSellStock,
    } = useGameActions();

    // Loading state is handled by AuthProvider wrapper


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
                        <HomePage onStartGame={handleStartGame} isLoading={isStarting} username={currentUser?.email?.split('@')[0] || 'User'} />
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
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            <AuthProvider>
                <SessionProvider>
                    <ErrorBoundary>
                        <AppRoutes />
                    </ErrorBoundary>
                </SessionProvider>
            </AuthProvider>
        </Router>
    );
}

export default App;
