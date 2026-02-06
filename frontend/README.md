# Frontend - Arth-Neeti Game UI

React + Vite application for the Arth-Neeti financial literacy game.

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── api/
│   │   └── index.js        # API client
│   ├── components/
│   │   ├── GameStats.jsx      # Health bars + month display
│   │   ├── ScenarioCard.jsx   # Card UI + lifeline button
│   │   ├── FeedbackModal.jsx  # Choice feedback
│   │   ├── StartScreen.jsx    # Welcome screen
│   │   └── GameOverScreen.jsx # Results + certificate
│   ├── utils/
│   │   └── sound.js        # Audio feedback
│   ├── App.jsx             # Main app + state management
│   └── App.css             # Styles
├── index.html
└── vite.config.js
```

## 🧩 Components

### App.jsx
Main component managing game state machine:

```
START → PLAYING ↔ FEEDBACK → GAME_OVER
```

**Key Features:**
- Session persistence via `localStorage`
- Automatic session resume on page load
- Lifeline handling

### GameStats.jsx
Displays player stats with visual feedback:
- 💰 Wealth bar (green/red flash on change)
- 😊 Well-being bar (renamed from Happiness)
- 📊 Credit Score bar (RBI standards 300-900)
- 🧾 Monthly Bills indicator
- 📅 Month indicator (calendar style)

### ScenarioCard.jsx
Card display with:
- Category badge (color-coded)
- Description
- Choice buttons with impact preview
- **"💡 Ask NCFE"** lifeline button
- Recommended choice highlighting (⭐ badge)

### StockTicker.jsx
- Real-time stock market simulation
- Buy/Sell interface for Tech, Green Energy, and Gold
- Portfolio tracking

### GameOverScreen.jsx
End game display (Redesigned v2.0):
- Animated Financial Persona result
- **Tabbed Reports:** Overview, Analysis, Recommendations
- **Achievements:** Unlockable badges
- **Leaderboard:** Top 10 players list
- **🖨️ Print Certificate** functionality

## 🎨 Styling

### Design System
- Dark theme with glassmorphism
- Gradient accents (purple/pink/gold)
- Smooth animations

### Key CSS Classes
| Class | Purpose |
|-------|---------|
| `.flash-green` | Positive stat change animation |
| `.flash-red` | Negative stat change animation |
| `.lifeline-btn` | Golden gradient hint button |
| `.recommended` | Green border for NCFE choice |
| `@media print` | Certificate print styles |

## 🔌 API Integration

### Environment Variables
```env
VITE_API_URL=http://localhost:8000/api
```

### API Functions
```javascript
api.startGame()           // Create session
api.getCard(sessionId)    // Get next card
api.submitChoice(sessionId, cardId, choiceId)
api.getSession(sessionId) // Resume session
api.useLifeline(sessionId, cardId)  // Get hints
```

## 🧪 Development

```bash
npm install
npm run dev     # Start dev server
npm run build   # Production build
npm run preview # Preview production build
```

## 🐳 Docker

```bash
docker build -t arth-neeti-frontend .
docker run -p 5173:5173 arth-neeti-frontend
```

## 📱 Responsive Design

- Desktop optimized
- Mobile-friendly stat bars
- Touch-friendly buttons

## ⚡ Performance

- Vite for fast HMR
- Lazy loading ready
- Minimal dependencies
