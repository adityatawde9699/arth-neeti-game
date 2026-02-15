/**
 * Session Context
 * Manages game session state throughout the app
 */
import React, { createContext, useContext, useState, useCallback } from 'react';
import { api } from '../api';

const SessionContext = createContext({});

const SESSION_STORAGE_KEY = 'arthneeti_session_id';

export const useSession = () => {
    const context = useContext(SessionContext);
    if (!context) {
        throw new Error('useSession must be used within a SessionProvider');
    }
    return context;
};

export const SessionProvider = ({ children }) => {
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const startGame = useCallback(async (data) => {
        setLoading(true);
        setError(null);
        try {
            if (import.meta.env.DEV) console.log('🎮 Starting new game session...', data);
            const responseData = await api.startGame(data);
            if (import.meta.env.DEV) console.log('✅ Game session started:', responseData.session.id);

            setSession(responseData.session);
            localStorage.setItem(SESSION_STORAGE_KEY, responseData.session.id);

            return responseData.session;
        } catch (err) {
            if (import.meta.env.DEV) console.error('❌ Failed to start game:', err);
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const updateSession = useCallback((newSession) => {
        if (import.meta.env.DEV) console.log('🔄 Updating session:', newSession?.id);
        setSession(newSession);
        if (newSession?.id) {
            localStorage.setItem(SESSION_STORAGE_KEY, newSession.id);
        }
    }, []);

    const clearSession = useCallback(() => {
        if (import.meta.env.DEV) console.log('🧹 Clearing session');
        setSession(null);
        setError(null);
        localStorage.removeItem(SESSION_STORAGE_KEY);
    }, []);

    const loadSession = useCallback(async (sessionId) => {
        setLoading(true);
        setError(null);
        try {
            if (import.meta.env.DEV) console.log('📥 Loading session:', sessionId);
            const data = await api.getSession(sessionId);
            setSession(data.session);
            return data.session;
        } catch (err) {
            if (import.meta.env.DEV) console.error('❌ Failed to load session:', err);
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const value = {
        session,
        loading,
        error,
        startGame,
        updateSession,
        clearSession,
        loadSession,
    };

    return (
        <SessionContext.Provider value={value}>
            {children}
        </SessionContext.Provider>
    );
};