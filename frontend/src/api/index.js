const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = {
    // Start a new game session
    async startGame() {
        const response = await fetch(`${API_BASE_URL}/start-game/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) throw new Error('Failed to start game');
        return response.json();
    },

    // Get a random scenario card
    async getCard(sessionId) {
        const response = await fetch(`${API_BASE_URL}/get-card/${sessionId}/`);
        if (!response.ok) throw new Error('Failed to get card');
        return response.json();
    },

    // Submit a choice
    async submitChoice(sessionId, cardId, choiceId) {
        const response = await fetch(`${API_BASE_URL}/submit-choice/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                card_id: cardId,
                choice_id: choiceId,
            }),
        });
        if (!response.ok) throw new Error('Failed to submit choice');
        return response.json();
    },

    // Get session state
    async getSession(sessionId) {
        const response = await fetch(`${API_BASE_URL}/session/${sessionId}/`);
        if (!response.ok) throw new Error('Failed to get session');
        return response.json();
    },

    // Use a lifeline to get hint
    async useLifeline(sessionId, cardId) {
        const response = await fetch(`${API_BASE_URL}/use-lifeline/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                card_id: cardId,
            }),
        });
        if (!response.ok) throw new Error('Failed to use lifeline');
        return response.json();
    },

    // Take an emergency loan
    async takeLoan(sessionId, loanType) {
        const response = await fetch(`${API_BASE_URL}/take-loan/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                loan_type: loanType,
            }),
        });
        if (!response.ok) throw new Error('Failed to take loan');
        return response.json();
    },
};
