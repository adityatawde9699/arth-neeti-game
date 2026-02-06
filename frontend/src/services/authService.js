/**
 * Firebase Authentication Service
 * Handles all Firebase authentication operations
 */
import {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    GoogleAuthProvider,
    signInWithPopup,
    signInWithRedirect,
    getRedirectResult,
    onAuthStateChanged,
} from 'firebase/auth';
import { auth } from '../firebase/config';

/**
 * Register a new user with email and password
 */
export const registerWithEmail = async (email, password) => {
    try {
        console.log('📝 Registering user with email:', email);
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        console.log('✅ User registered successfully:', userCredential.user.uid);
        return userCredential.user;
    } catch (error) {
        console.error('❌ Registration error:', error);
        throw new Error(getFirebaseErrorMessage(error.code));
    }
};

/**
 * Sign in with email and password
 */
export const loginWithEmail = async (email, password) => {
    try {
        console.log('🔑 Logging in user with email:', email);
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        console.log('✅ User logged in successfully:', userCredential.user.uid);
        return userCredential.user;
    } catch (error) {
        console.error('❌ Login error:', error);
        throw new Error(getFirebaseErrorMessage(error.code));
    }
};

/**
 * Sign in with Google using Popup (works better in most cases)
 */
export const loginWithGoogle = async () => {
    try {
        console.log('🔵 Initiating Google login...');
        const provider = new GoogleAuthProvider();
        provider.addScope('profile');
        provider.addScope('email');

        // Use popup instead of redirect for better UX
        const result = await signInWithPopup(auth, provider);
        console.log('✅ Google login successful:', result.user.email);
        return result.user;
    } catch (error) {
        console.error('❌ Google login error:', error);

        // If popup was blocked, fallback to redirect
        if (error.code === 'auth/popup-blocked' || error.code === 'auth/network-request-failed' || error.message.includes('closed')) {
            console.log('⚠️ Popup failed or blocked, switching to redirect strategy...');
            const provider = new GoogleAuthProvider();
            await signInWithRedirect(auth, provider);
            return null; // Will redirect
        }

        throw new Error(getFirebaseErrorMessage(error.code));
    }
};

/**
 * Check for Redirect Result (Call this on app load)
 */
export const checkRedirectResult = async () => {
    try {
        console.log('🔍 Checking for redirect result...');
        const result = await getRedirectResult(auth);
        if (result) {
            console.log('✅ Redirect login successful:', result.user.email);
            return result.user;
        }
        console.log('ℹ️ No redirect result found');
        return null;
    } catch (error) {
        console.error('❌ Redirect result error:', error);
        throw new Error(getFirebaseErrorMessage(error.code));
    }
};

/**
 * Sign out current user
 */
export const logout = async () => {
    try {
        console.log('👋 Logging out user...');
        await signOut(auth);
        console.log('✅ User logged out successfully');
    } catch (error) {
        console.error('❌ Logout error:', error);
        throw new Error('Failed to logout');
    }
};

/**
 * Get current user
 */
export const getCurrentUser = () => {
    return auth.currentUser;
};

/**
 * Get current user's ID token
 */
export const getIdToken = async (forceRefresh = false) => {
    const user = auth.currentUser;
    if (user) {
        try {
            const token = await user.getIdToken(forceRefresh);
            return token;
        } catch (error) {
            console.error('❌ Failed to get ID token:', error);
            return null;
        }
    }
    return null;
};

/**
 * Listen to auth state changes
 */
export const onAuthChange = (callback) => {
    return onAuthStateChanged(auth, callback);
};

/**
 * Convert Firebase error codes to user-friendly messages
 */
const getFirebaseErrorMessage = (errorCode) => {
    switch (errorCode) {
        case 'auth/email-already-in-use':
            return 'This email is already registered. Please login instead.';
        case 'auth/invalid-email':
            return 'Invalid email address.';
        case 'auth/operation-not-allowed':
            return 'Operation not allowed. Please contact support.';
        case 'auth/weak-password':
            return 'Password is too weak. Use at least 6 characters.';
        case 'auth/user-disabled':
            return 'This account has been disabled.';
        case 'auth/user-not-found':
            return 'No account found with this email.';
        case 'auth/wrong-password':
            return 'Incorrect password.';
        case 'auth/invalid-credential':
            return 'Invalid email or password.';
        case 'auth/too-many-requests':
            return 'Too many failed attempts. Please try again later.';
        case 'auth/network-request-failed':
            return 'Network error. Please check your connection.';
        case 'auth/popup-closed-by-user':
            return 'Sign-in popup was closed. Please try again.';
        case 'auth/popup-blocked':
            return 'Popup was blocked by browser. Please allow popups for this site.';
        case 'auth/cancelled-popup-request':
            return 'Only one popup request is allowed at a time.';
        case 'auth/account-exists-with-different-credential':
            return 'An account already exists with the same email but different sign-in credentials.';
        default:
            return `Authentication error: ${errorCode || 'Unknown error'}`;
    }
};