import React, { useState, useEffect } from 'react';
import { registerWithEmail, loginWithEmail, loginWithGoogle, checkRedirectResult } from '../services/authService';
import './AuthPage.css';



const GoogleLoginButton = ({ onLoginStart, onLoginEnd, onError, onSuccess }) => {
    const handleGoogleLogin = async () => {
        try {
            onLoginStart();
            await loginWithGoogle();
            onSuccess();
        } catch (err) {
            onError('Google login failed: ' + err.message);
            onLoginEnd();
        }
    };

    return (
        <button
            type="button"
            onClick={handleGoogleLogin}
            className="oauth-button google"
        >
            <svg width="20" height="20" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.04-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
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
                await registerWithEmail(formData.email, formData.password);
                onSuccess();
            } else {
                await loginWithEmail(formData.email, formData.password);
                onSuccess();
            }
        } catch (err) {
            setError(err.message || `${mode === 'register' ? 'Registration' : 'Login'} failed`);
        } finally {
            setIsLoading(false);
        }
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
                    <GoogleLoginButton
                        onLoginStart={() => setIsLoading(true)}
                        onLoginEnd={() => setIsLoading(false)}
                        onError={(msg) => setError(msg)}
                        onSuccess={onSuccess} // Pass for consistency, though unused in redirect
                    />
                </div>

                {/* Divider */}
                <div className="divider">
                    <span>or</span>
                </div>

                {/* Email Form */}
                <form onSubmit={handleEmailSubmit} className="auth-form">
                    {mode === 'register' && (
                        <div className="form-group">
                            <label>Username</label>
                            <input
                                type="text"
                                name="username"
                                value={formData.username}
                                onChange={handleInputChange}
                                placeholder="Enter your username"
                                className="form-input"
                            />
                        </div>
                    )}
                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            placeholder="name@example.com"
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
    // Check if we just came back from Google
    useEffect(() => {
        const verifyLogin = async () => {
            try {
                const user = await checkRedirectResult();
                if (user) {
                    onSuccess(); // Login successful after reload
                }
            } catch (err) {
                console.error("Redirect login failed:", err);
            }
        };
        verifyLogin();
    }, [onSuccess]);

    return <AuthForm mode={mode} onSuccess={onSuccess} onSwitchMode={onSwitchMode} />;
};

export default AuthPage;
