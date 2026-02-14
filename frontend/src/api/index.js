const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Import Firebase auth
import { auth } from '../firebase/config';

const getAuthHeaders = async () => {
    const user = auth.currentUser;
    if (user) {
        try {
            const token = await user.getIdToken();
            return { 'Authorization': `Bearer ${token}` };
        } catch (error) {
            if (import.meta.env.DEV) console.error('Failed to get Firebase token:', error);
            return {};
        }
    }
    return {};
};

/**
 * Parse a fetch Response and throw an error that includes the server's
 * error message (if any) instead of a generic "Failed to …" string.
 */
async function handleResponse(response) {
    if (response.ok) return response.json();

    // Try to extract the server-side error body
    let serverMessage;
    try {
        const body = await response.json();
        serverMessage = body.error || body.detail || body.message || JSON.stringify(body);
    } catch {
        serverMessage = response.statusText || `HTTP ${response.status}`;
    }
    throw new Error(serverMessage);
}

export const api = {
    // --- AUTHENTICATION ---
    // NOTE: register() and login() methods removed
    // Authentication is now handled by Firebase SDK (see services/authService.js)

    async getProfile() {
        const response = await fetch(`${API_BASE_URL}/profile/`, {
            headers: { ...(await getAuthHeaders()) },
        });
        return handleResponse(response);
    },

    // --- GAME SESSION ---
    async startGame() {
        const response = await fetch(`${API_BASE_URL}/start-game/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(await getAuthHeaders()),
            },
        });
        return handleResponse(response);
    },

    async getCard(sessionId, language = 'en') {
        const response = await fetch(`${API_BASE_URL}/get-card/${sessionId}/?lang=${language}`, {
            headers: { ...(await getAuthHeaders()) },
        });
        return handleResponse(response);
    },

    async submitChoice(sessionId, cardId, choiceId) {
        const response = await fetch(`${API_BASE_URL}/submit-choice/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(await getAuthHeaders()),
            },
            body: JSON.stringify({
                session_id: sessionId,
                card_id: cardId,
                choice_id: choiceId,
            }),
        });
        return handleResponse(response);
    },

    async getSession(sessionId) {
        const response = await fetch(`${API_BASE_URL}/session/${sessionId}/`, {
            headers: { ...(await getAuthHeaders()) },
        });
        return handleResponse(response);
    },

    // --- UTILITIES ---
    async useLifeline(sessionId, cardId) {
        const response = await fetch(`${API_BASE_URL}/use-lifeline/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({ session_id: sessionId, card_id: cardId }),
        });
        return handleResponse(response);
    },

    async takeLoan(sessionId, loanType) {
        const response = await fetch(`${API_BASE_URL}/take-loan/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({ session_id: sessionId, loan_type: loanType }),
        });
        return handleResponse(response);
    },

    async skipCard(sessionId, cardId) {
        const response = await fetch(`${API_BASE_URL}/skip-card/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({ session_id: sessionId, card_id: cardId }),
        });
        return handleResponse(response);
    },

    async getAIAdvice(sessionId, cardId) {
        const response = await fetch(`${API_BASE_URL}/ai-advice/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({ session_id: sessionId, card_id: cardId }),
        });
        return handleResponse(response);
    },

    async getLeaderboard() {
        const response = await fetch(`${API_BASE_URL}/leaderboard/`);
        return handleResponse(response);
    },

    // --- STOCK MARKET 2.0 ---
    async getMarketStatus(sessionId) {
        const response = await fetch(`${API_BASE_URL}/market-status/${sessionId}/`, {
            headers: { ...(await getAuthHeaders()) },
        });
        return handleResponse(response);
    },

    async buyStock(sessionId, sector, amount) {
        const response = await fetch(`${API_BASE_URL}/buy-stock/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({ session_id: sessionId, sector, amount }),
        });
        return handleResponse(response);
    },

    async sellStock(sessionId, sector, units) {
        const response = await fetch(`${API_BASE_URL}/sell-stock/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({ session_id: sessionId, sector, amount: units }),
        });
        return handleResponse(response);
    },

    async investMutualFund(sessionId, fundType, amount) {
        const response = await fetch(`${API_BASE_URL}/mutual-fund/invest/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({ session_id: sessionId, fund_type: fundType, amount }),
        });
        return handleResponse(response);
    },

    async redeemMutualFund(sessionId, fundType, units) {
        const response = await fetch(`${API_BASE_URL}/mutual-fund/redeem/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({ session_id: sessionId, fund_type: fundType, units }),
        });
        return handleResponse(response);
    },

    async applyIPO(sessionId, ipoName, amount) {
        const response = await fetch(`${API_BASE_URL}/ipo/apply/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({ session_id: sessionId, ipo_name: ipoName, amount }),
        });
        return handleResponse(response);
    },

    async tradeFutures(sessionId, sector, units, duration) {
        const response = await fetch(`${API_BASE_URL}/futures/trade/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({ session_id: sessionId, sector, units, duration }),
        });
        return handleResponse(response);
    },

    // --- CHATBOT ---
    async respondToChatbot(sessionId, character, accepted, scamLossAmount = 0) {
        const response = await fetch(`${API_BASE_URL}/chatbot/respond/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(await getAuthHeaders()) },
            body: JSON.stringify({
                session_id: sessionId,
                character,
                accepted,
                scam_loss_amount: scamLossAmount,
            }),
        });
        return handleResponse(response);
    },
};
