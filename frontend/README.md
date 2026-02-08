# Frontend - Arth-Neeti Game UI (v3.0.0)

React + Vite application for the Arth-Neeti financial literacy game.
Features a responsive dashboard, real-time stock ticker, and bilingual support.

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── api/
│   │   └── index.js        # Axios Client (Interceptors for Auth)
│   ├── components/
│   │   ├── GameStats.jsx      # HUD (Wealth, Well-being, Credit)
│   │   ├── BudgetDisplay.jsx  # Monthly Cashflow Visualization
│   │   ├── StockTicker.jsx    # Real-time Market Graph
│   │   ├── ScenarioCard.jsx   # Main Decision UI
│   │   ├── ProfileScreen.jsx  # User Stats & History
│   │   └── GameOverScreen.jsx # Final Report & Certificate
│   ├── pages/
│   │   ├── StockMarketPage.jsx # Full-screen trading view
│   │   └── LoanPage.jsx        # Loan management interface
│   ├── contexts/
│   │   ├── AuthContext.jsx      # Firebase User State
│   │   └── SessionContext.jsx   # Game Session State
│   └── App.jsx                  # Routing & Layout
└── vite.config.js
```

## 🧩 Key Features

### 🎮 Game Interface
*   **HUD**: Persistent top bar showing Wealth, Happiness, and Credit Score.
*   **Budget Preview**: Visual breakdown of income vs expenses (Rent, Food, etc.).
*   **Bilingual Toggle**: Switch between English (En) and Hindi (Hi) instantly.

### 📈 Stock Market Page
*   **Three Sectors**: Gold, Technology, Real Estate.
*   **Interactive Graphs**: Visual price history for the last 12 months.
*   **Trading Actions**: Buy/Sell buttons with validation (insufficient funds, etc.).

### 💳 Loan & Banking
*   **Loan Options**: 
    *   *Family Loan*: Low interest, social pressure.
    *   *Instant App*: High interest, easy approval.
*   **Repayment**: Automatic deductions from monthly salary.

### 👤 Profile & Reports
*   **Player History**: List of all past games and scores.
*   **Achievements**: Badges like "Debt Free", "Wealthy", "Survivor".
*   **Printable Report**: A detailed "Financial Health Report" generated at Game Over.

## 🎨 Styling

*   **CSS Modules**: Component-scoped styles (e.g., `ProfileScreen.css`).
*   **Animations**: `framer-motion` used for transitions.
*   **Glassmorphism**: Dark theme with translucent cards and neon accents.

## 🔌 API Integration

### Environment Variables
```env
VITE_API_URL=http://localhost:8000/api
```

### Authentication
Uses **Firebase Auth SDK** (Google Sign-In + Email/Password).
Token is automatically injected into `Authorization` headers via Axios interceptors.

## 🧪 Development

```bash
npm install
npm run dev     # Start dev server (localhost:5173)
npm run build   # Production build
```

## 🐳 Docker

```bash
docker build -t arth-neeti-frontend .
docker run -p 5173:5173 arth-neeti-frontend
```
