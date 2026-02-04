import { useState, useCallback, useEffect } from 'react';
import { api } from './api';
import GameStats from './components/GameStats';
import ScenarioCard from './components/ScenarioCard';
import FeedbackModal from './components/FeedbackModal';
import StartScreen from './components/StartScreen';
import GameOverScreen from './components/GameOverScreen';
import ParticleBackground from './components/ParticleBackground';
import './App.css';
import './components/ReportModal.css';

// Game states
const GAME_STATE = {
    START: 'start',
    PLAYING: 'playing',
    FEEDBACK: 'feedback',
    GAME_OVER: 'game_over',
    LOADING: 'loading',
};

const SESSION_STORAGE_KEY = 'arthneeti_session_id';

function App() {
    const [gameState, setGameState] = useState(GAME_STATE.START);
    const [session, setSession] = useState(null);
    const [currentCard, setCurrentCard] = useState(null);
    const [feedback, setFeedback] = useState(null);
    const [gameOverData, setGameOverData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lang, setLang] = useState('en');

    // Check for existing session on app load
    useEffect(() => {
        const resumeSession = async () => {
            const savedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);
            if (!savedSessionId) return;

            setIsLoading(true);
            try {
                const sessionData = await api.getSession(savedSessionId);
                if (sessionData.session && sessionData.session.is_active) {
                    setSession(sessionData.session);

                    // Get next card
                    const cardData = await api.getCard(savedSessionId);
                    if (!cardData.game_complete) {
                        setCurrentCard(cardData.card);
                        setGameState(GAME_STATE.PLAYING);
                    } else {
                        localStorage.removeItem(SESSION_STORAGE_KEY);
                    }
                } else {
                    localStorage.removeItem(SESSION_STORAGE_KEY);
                }
            } catch (err) {
                console.log('Could not resume session:', err);
                localStorage.removeItem(SESSION_STORAGE_KEY);
            } finally {
                setIsLoading(false);
            }
        };

        resumeSession();
    }, []);

    // Start a new game
    const handleStartGame = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await api.startGame();
            setSession(data.session);

            // Save session to localStorage for resume capability
            localStorage.setItem(SESSION_STORAGE_KEY, data.session.id);

            // Fetch first card
            const cardData = await api.getCard(data.session.id);
            setCurrentCard(cardData.card);
            setGameState(GAME_STATE.PLAYING);
        } catch (err) {
            setError('Failed to start game. Is the backend running?');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Handle choice selection
    const handleChoiceSelect = useCallback(async (choice) => {
        if (!session || !currentCard) return;

        setIsLoading(true);
        try {
            const result = await api.submitChoice(session.id, currentCard.id, choice.id);

            // Update session with new values
            setSession(result.session);

            // Show feedback
            setFeedback({
                text: result.feedback,
                wasRecommended: result.was_recommended,
            });
            setGameState(GAME_STATE.FEEDBACK);

            // Check if game over
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
    }, [session, currentCard]);

    // Continue after feedback
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

    // Use a lifeline
    const handleUseLifeline = useCallback(async (cardId) => {
        if (!session) return null;
        try {
            const result = await api.useLifeline(session.id, cardId);
            // Update session with new lifeline count
            if (result.session) {
                setSession(result.session);
            }
            return result;
        } catch (err) {
            console.error('Failed to use lifeline:', err);
            return null;
        }
    }, [session]);

    const handleTakeLoan = useCallback(async (loanType) => {
        if (!session) return null;
        try {
            const result = await api.takeLoan(session.id, loanType);
            if (result.session) {
                setSession(result.session);
            }
            return result;
        } catch (err) {
            console.error('Failed to take loan:', err);
            return null;
        }
    }, [session]);

    // Play again
    const handlePlayAgain = useCallback(() => {
        localStorage.removeItem(SESSION_STORAGE_KEY);
        setSession(null);
        setCurrentCard(null);
        setFeedback(null);
        setGameOverData(null);
        setError(null);
        setGameState(GAME_STATE.START);
    }, []);

    // Render based on game state
    const renderContent = () => {
        if (error) {
            return (
                <div className="container" style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '100vh',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
                    <h2 style={{ marginBottom: '1rem' }}>Connection Error</h2>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>{error}</p>
                    <button className="btn btn-primary" onClick={() => setError(null)}>
                        Try Again
                    </button>
                </div>
            );
        }

        switch (gameState) {
            case GAME_STATE.START:
                return <StartScreen onStartGame={handleStartGame} isLoading={isLoading} />;

            case GAME_STATE.PLAYING:
                return (
                    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
                        <div className="language-toggle">
                            <span>Language:</span>
                            <div className="language-buttons">
                                <button
                                    type="button"
                                    className={lang === 'en' ? 'active' : ''}
                                    onClick={() => setLang('en')}
                                >
                                    English
                                </button>
                                <button
                                    type="button"
                                    className={lang === 'hi' ? 'active' : ''}
                                    onClick={() => setLang('hi')}
                                >
                                    हिंदी
                                </button>
                                <button
                                    type="button"
                                    className={lang === 'mr' ? 'active' : ''}
                                    onClick={() => setLang('mr')}
                                >
                                    मराठी
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
                            lang={lang}
                        />
                    </div>
                );

            case GAME_STATE.FEEDBACK:
                return (
                    <>
                        <div className="container" style={{ paddingTop: '2rem' }}>
                            <div className="language-toggle">
                                <span>Language:</span>
                                <div className="language-buttons">
                                    <button
                                        type="button"
                                        className={lang === 'en' ? 'active' : ''}
                                        onClick={() => setLang('en')}
                                    >
                                        English
                                    </button>
                                    <button
                                        type="button"
                                        className={lang === 'hi' ? 'active' : ''}
                                        onClick={() => setLang('hi')}
                                    >
                                        हिंदी
                                    </button>
                                    <button
                                        type="button"
                                        className={lang === 'mr' ? 'active' : ''}
                                        onClick={() => setLang('mr')}
                                    >
                                        मराठी
                                    </button>
                                </div>
                            </div>
                            <GameStats session={session} />
                        </div>
                        <FeedbackModal
                            feedback={feedback?.text}
                            wasRecommended={feedback?.wasRecommended}
                            onContinue={handleContinue}
                        />
                    </>
                );

            case GAME_STATE.GAME_OVER:
                return (
                    <GameOverScreen
                        session={session}
                        persona={gameOverData?.persona}
                        reason={gameOverData?.reason}
                        onPlayAgain={handlePlayAgain}
                    />
                );

            case GAME_STATE.LOADING:
                return (
                    <div className="loading-screen">
                        <div className="loading-spinner"></div>
                        <p>Loading...</p>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="app">
            <ParticleBackground intensity="normal" />
            {renderContent()}
        </div>
    );
}

export default App;
