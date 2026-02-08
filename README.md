# 🎮 Arth-Neeti: Financial Literacy Through Gamification

> A full-stack financial simulation game designed to teach financial literacy to young professionals through real-world scenarios, stock market investment, and credit management.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Django 5.0](https://img.shields.io/badge/django-5.0-green.svg)](https://www.djangoproject.com/)
[![React 18](https://img.shields.io/badge/react-18-61DAFB.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/vite-4.0+-646CFF.svg)](https://vitejs.dev/)
[![Firebase](https://img.shields.io/badge/firebase-auth-orange.svg)](https://firebase.google.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](./LICENSE)

---

## 📖 Project Overview

**Arth-Neeti** ("Financial Policy" or "Wisdom") is a turn-based role-playing game where players navigate the first 12 months of their professional life.

### 🚀 Version 3.0.0: The "Market Mogul" Update
The latest release introduces a complete economic simulation, allowing players to trade stocks, manage debt, and receive AI-powered financial advice.

*   **Income & Expenses**: Managing a fixed salary against recurring bills (rent, utilities) and unexpected costs.
*   **Investment**: Real-time stock market simulation with sector-specific trends (Tech, Green Energy, Gold).
*   **Credit Logic**: A dynamic credit score system (300-900) influenced by bill payments and loan management.
*   **AI Advisory**: Integrated Google Gemini AI providing contextual financial advice for every scenario.

The project is built as a **Headless Django Monolith (API)** serving a **React Single Page Application (SPA)**.

---

## ✨ Key Features (Implemented)

### 🕹️ Core Gameplay
*   **Scenario-Based Engine**: Over 36 diverse scenarios (Needs vs. Wants, Scams, Social Pressure) stored in the database.
*   **Decision Impact**: Every choice affects 4 metrics: Wealth, Happiness, Credit Score, and Financial Literacy.
*   **Turn-Based Progression**: Players play through 12 months, dealing with inflation and lifestyle creep.

### 📈 Financial Simulation
*   **Stock Market 2.0**: 
    *   Buy/Sell stocks in 3 sectors.
    *   Market events (News) trigger price fluctuations.
    *   Historical price tracking and portfolio value calculation.
    *   *Experimental*: Futures Contracts (Short Selling) implemented in backend models.
*   **Banking System**:
    *   Recurring expenses engine (Rent, Subscriptions).
    *   Loan management (Take Loans, Interest Calculation).

### 🤖 AI Integration
*   **Hybrid Advisor System**:
    *   **Primary**: Calls Google Gemini (Generative AI) for personalized advice based on player's current stats.
    *   **Fallback**: Robust keyword-based rule engine ensures advice is always available if the API fails.

### 📊 Analytics & Reporting
*   **Post-Game Dashboard**:
    *   Detailed breakdown of Net Worth, Survival Rate, and Credit Health.
    *   **Financial Persona**: Assigns a persona (e.g., "The Warren Buffett", "The FOMO Victim") based on playstyle.
    *   **Printable Report**: Generates a browser-printable "Financial Health Report" with actionable recommendations.
*   **Leaderboard**: Tracks top players based on valid verified game sessions.

### 🌐 Internationalization
*   **Bilingual Support**: UI toggles between English and Hindi (backend models support bilingual content).

---

## 🛠️ Tech Stack

### Frontend
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | React 18 | Functional components, Hooks |
| **Build Tool** | Vite | Fast HMR and bundling |
| **Routing** | React Router DOM v6 | Protected routes, navigation |
| **State Management** | Context API | `AuthContext`, `SessionContext` for global state |
| **Styling** | CSS Modules | Component-scoped vanilla CSS |
| **Auth** | Firebase SDK | Google OAuth & Email/Password |
| **API Client** | Axios | REST communication with Django |

### Backend
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | Django 5.0 | Core logic and ORM |
| **API** | Django REST Framework | Serializers, ViewSets, Permissions |
| **Auth** | Firebase Admin SDK | Verifies frontend tokens, syncs to Django Users |
| **AI** | Google Generative AI | Gemini 1.5 Flash for advisory |
| **Database** | SQLite (Dev) | Standard Django default (Postgres ready) |
| **Task Queue** | Standard Sync | Requests handled synchronously |

---

## 🏗️ Architecture

The system follows a predictable **Client-Server** architecture:

```mermaid
graph TD
    Client[React Frontend] -->|REST API (Axios)| Server[Django Backend]
    
    subgraph "Frontend Layer"
        Client --> Auth[Firebase SDK]
        Client --> State[Context Providers]
    end

    subgraph "Backend Layer"
        Server -->|Verify Token| Firebase[Firebase Admin]
        Server -->|Query| DB[(SQLite/Postgres)]
        Server -->|Prompt| Gemini[Google AI API]
        Server -->|Business Logic| GameEngine[Game Engine App]
    end
```

### Key Modules
1.  **game_engine**:
    *   `models.py`: Defines the world (ScenarioCard, GameSession, StockHistory).
    *   `advisor.py`: Encapsulates the AI logic (Gemini + Rules).
    *   `firebase_auth.py`: Middleware for verifying Identity Tokens.
2.  **frontend/src/components**:
    *   `ScenarioCard.jsx`: Main interaction UI.
    *   `StockTicker.jsx`: Investment dashboard.
    *   `GameOverScreen.jsx`: Analytics and Reporting.

---

## 🚀 Setup & Installation

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Firebase Project (for `serviceAccountKey.json` and frontend config)
*   Google Gemini API Key

### Backend Setup
1.  Navigate to `backend`:
    ```bash
    cd backend
    ```
2.  Create and activate virtual environment:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure Environment:
    *   Set `GEMINI_API_KEY` in `.env` or environment variables.
    *   Place `serviceAccountKey.json` in `backend/` or set `FIREBASE_SERVICE_ACCOUNT_PATH`.
5.  Run Migrations and Seed Data:
    ```bash
    python manage.py migrate
    python manage.py seed_scenarios  # Populates cards
    ```
6.  Start Server:
    ```bash
    python manage.py runserver
    ```

### Frontend Setup
1.  Navigate to `frontend`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start Dev Server:
    ```bash
    npm run dev
    ```

---

## 📝 Usage

### Starting a Game
1.  Login via Google or Email (Firebase Auth).
2.  Click **"Start Your Journey"** on the Dashboard.
3.  Review your starting stats (Width: ₹25k, Happiness: 100%).

### Gameplay Loop
1.  **Read Scenario**: Analyze the situation (e.g., "Friend's Wedding").
2.  **Get Advice**: Click "Ask AI Advisor" for Gemini-powered tips.
3.  **Make Choice**: Select an option. Watch your stats update immediately.
4.  **Manage Finances**:
    *   Visit **Stock Market** to trade assets.
    *   Visit **Loans** to manage debt if cash flows are negative.

### Game Over
*   Occurs after **12 Months** (Success) or if **Wealth = 0** (Bankruptcy) or **Happiness = 0** (Burnout).
*   View your **Financial Health Report** and print it for reference.

---

## ⚠️ Limitations & Known Gaps

*   **Leaderboard Visibility**: The leaderboard is currently only accessible via the *Game Over* screen, not from the main dashboard.
*   **Styling System**: The project uses component-specific CSS files (`.css`). There is no global utility framework (like Tailwind), making global style changes slower.
*   **Mobile Responsiveness**: While playable on mobile, complex dashboards (Stock Market/Reports) are optimized for Desktop.
*   **Test Coverage**: Basic tests exist in `tests.py`, but comprehensive unit testing for React components is missing.

---

## 🔮 Future Improvements

Based on the current architecture, these extensions are viable:
1.  **Persistent Leaderboard Page**: Expose the `api.getLeaderboard()` endpoint to a new `/leaderboard` frontend route.
2.  **Multi-Language Content**: Fully populate the `title_hi` and `description_hi` fields in the database for complete Hindi support.
3.  **Real-Time Stock Updates**: Replace the per-turn stock update with a WebSocket connection (using Django Channels) for "live" ticker feels.
4.  **Social Features**: Share "Financial Persona" directly to social media using the `ProfileScreen` data.

---

## 🙏 Acknowledgments

*   **National Centre for Financial Education (NCFE)**: For inspiration and financial literacy resources.
*   **Reserve Bank of India (RBI)**: For guidelines on credit scores and banking norms.

---

*Verified based on codebase analysis v3.0.0*
