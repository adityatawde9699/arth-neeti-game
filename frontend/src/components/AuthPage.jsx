import React, { useState } from 'react';
import { GoogleOAuthProvider, useGoogleLogin } from '@react-oauth/google';
import { api } from '../api';
import './AuthPage.css';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

const GoogleLoginButton = ({ onLoginStart, onLoginEnd, onError }) => {
    const handleGoogleLogin = useGoogleLogin({
        onSuccess: async (tokenResponse) => {
            try {
                onLoginStart();
                // TODO: Implement backend OAuth endpoint
                // const data = await api.googleLogin(tokenResponse.access_token);
                // For now, show error that backend needs to be implemented
                onError('Google OAuth backend integration pending. Please use email/password for now.');
            } catch (err) {
                onError('Google login failed');
            } finally {
                onLoginEnd();
            }
        },
        onError: () => {
            onError('Google login failed');
        }
    });

    return (
        <button
            type="button"
            onClick={handleGoogleLogin}
            className="oauth-button google"
        >
            <svg width="20" height="20" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Continue with Google
        </button>
    );
};

const AuthForm = ({ mode, onSuccess, onSwitchMode }) => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError(null);
    };

    const handleEmailSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            if (mode === 'register') {
                if (formData.password !== formData.confirmPassword) {
                    throw new Error('Passwords do not match');
                }
                if (formData.password.length < 6) {
                    throw new Error('Password must be at least 6 characters');
                }
                const data = await api.register(formData.username, formData.password, formData.email);
                localStorage.setItem('auth_token', data.token);
                localStorage.setItem('username', data.username);
                onSuccess(data);
            } else {
                const data = await api.login(formData.username, formData.password);
                localStorage.setItem('auth_token', data.token);
                localStorage.setItem('username', data.username);
                onSuccess(data);
            }
        } catch (err) {
            setError(err.message || `${mode === 'register' ? 'Registration' : 'Login'} failed`);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAppleLogin = () => {
        // Apple OAuth requires special setup
        setError('Apple Sign-In requires additional configuration. Please use email/password for now.');
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                {/* Header */}
                <div className="auth-header">
                    <div className="auth-logo">💰</div>
                    <h1>{mode === 'login' ? 'Welcome Back' : 'Create Account'}</h1>
                    <p>{mode === 'login' ? 'Sign in to continue your financial journey' : 'Start your financial education today'}</p>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="error-alert">
                        <span>⚠️</span>
                        <span>{error}</span>
                    </div>
                )}

                {/* OAuth Buttons */}
                <div className="oauth-section">
                    {GOOGLE_CLIENT_ID && (
                        <GoogleLoginButton
                            onLoginStart={() => setIsLoading(true)}
                            onLoginEnd={() => setIsLoading(false)}
                            onError={(msg) => setError(msg)}
                        />
                    )}
                    <button
                        type="button"
                        onClick={handleAppleLogin}
                        disabled={isLoading}
                        className="oauth-button apple"
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
                        </svg>
                        Continue with Apple
                    </button>
                </div>

                {/* Divider */}
                <div className="divider">
                    <span>or</span>
                </div>

                {/* Email Form */}
                <form onSubmit={handleEmailSubmit} className="auth-form">
                    {mode === 'register' && (
                        <div className="form-group">
                            <label>Email (Optional)</label>
                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleInputChange}
                                placeholder="name@example.com"
                                className="form-input"
                            />
                        </div>
                    )}
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleInputChange}
                            placeholder="Enter your username"
                            required
                            className="form-input"
                        />
                    </div>
                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleInputChange}
                            placeholder={mode === 'login' ? 'Enter your password' : 'Create a password'}
                            required
                            className="form-input"
                        />
                    </div>
                    {mode === 'register' && (
                        <div className="form-group">
                            <label>Confirm Password</label>
                            <input
                                type="password"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleInputChange}
                                placeholder="Confirm your password"
                                required
                                className="form-input"
                            />
                        </div>
                    )}
                    {mode === 'login' && (
                        <div className="form-options">
                            <label className="checkbox-label">
                                <input type="checkbox" />
                                <span>Remember me</span>
                            </label>
                            <button type="button" className="link-button">
                                Forgot password?
                            </button>
                        </div>
                    )}
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="submit-button"
                    >
                        {isLoading ? (
                            <>
                                <span className="spinner-small"></span>
                                {mode === 'login' ? 'Signing in...' : 'Creating account...'}
                            </>
                        ) : (
                            mode === 'login' ? 'Sign In' : 'Create Account'
                        )}
                    </button>
                </form>

                {/* Switch Mode */}
                <div className="auth-footer">
                    <span>
                        {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
                    </span>
                    <button
                        type="button"
                        onClick={onSwitchMode}
                        className="link-button"
                    >
                        {mode === 'login' ? 'Sign Up' : 'Sign In'}
                    </button>
                </div>
            </div>
        </div>
    );
};

const AuthPage = ({ mode = 'login', onSuccess, onSwitchMode }) => {
    if (GOOGLE_CLIENT_ID) {
        return (
            <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
                <AuthForm mode={mode} onSuccess={onSuccess} onSwitchMode={onSwitchMode} />
            </GoogleOAuthProvider>
        );
    }
    return <AuthForm mode={mode} onSuccess={onSuccess} onSwitchMode={onSwitchMode} />;
};

export default AuthPage;
