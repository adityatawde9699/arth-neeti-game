# Backend - Arth-Neeti Game Engine (v3.0.0)

Django REST API powering the Arth-Neeti financial literacy game.
Includes Stock Market simulation, AI Advisory, and Firebase Authentication.

## 🏗️ Architecture

```
backend/
├── core/                 # Django project settings
│   ├── settings.py       # Configuration
│   └── urls.py           # Root URL routing
├── game_engine/          # Main app
│   ├── models.py         # Database models (Session, Stocks, Expenses)
│   ├── views.py          # API endpoints
│   ├── serializers.py    # DRF serializers
│   ├── advisor.py        # Gemini AI + Fallback Logic
│   ├── firebase_auth.py  # Auth Middleware
│   ├── ml/               # Machine Learning
│   │   └── predictor.py  # Stock trend prediction logic
│   └── management/
│       └── commands/
│           └── seed_scenarios.py  # Card seeder
└── requirements.txt
```

## 📊 Data Models

### Core Game
| Model | Description |
|-------|-------------|
| `GameSession` | Tracks wealth, happiness, credit score, and current month. |
| `PlayerProfile` | Persistent user stats across multiple games (High scores, Badges). |
| `ScenarioCard` | The decision events presented to the player. |
| `Choice` | Options for each card with specific impacts. |

### Stock Market 2.0
| Model | Description |
|-------|-------------|
| `StockHistory` | Pre-generated price points for Tech, Gold, Real Estate (Ground Truth). |
| `FuturesContract` | Tracks short-selling positions (hedge interactions). |
| `MarketEvent` | News items that trigger price fluctuations (e.g., "Tech Bubble Burst"). |

### Banking & Finance
| Model | Description |
|-------|-------------|
| `RecurringExpense` | Monthly drains like Rent, Netflix, Loan EMIs. |
| `Loan` | (In Session) Tracks active loans and interest accumulation. |

## 🔌 API Endpoints

### Game Flow
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/start-game/` | Create new session (Resets state) |
| GET | `/api/get-card/{session_id}/` | Get next scenario card |
| POST | `/api/submit-choice/` | Submit decision & update stats |
| GET | `/api/session/{session_id}/` | Get full HUD state (Wealth, Happiness) |
| GET | `/api/leaderboard/` | Get top 10 players |

### Stock Market
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/buy-stock/` | Buy units of a sector |
| POST | `/api/sell-stock/` | Sell units & realize profit/loss |

### Banking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/take-loan/` | borrow money (Family or Instant App) |

### AI Advisory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/get-ai-advice/` | Get context-aware advice from Gemini 1.5 Flash |

## 🤖 AI Integration

### Provider: Google Gemini 1.5 Flash
The `advisor.py` module constructs a prompt with:
1.  Player's current financials (Wealth, Salary).
2.  The specific scenario and choices.
3.  Request for "Friendly Indian Financial Advisor" persona.

**Fallback:** If the API Key is missing or quota exceeded, a Keyword-based heuristic engine returns pre-written advice safe for gameplay.

## 🔐 Authentication

Uses **Firebase Authentication**:
1.  Frontend sends ID Token in `Authorization: Bearer <token>`.
2.  `firebase_auth.py` Middleware validates token with Firebase Admin SDK.
3.  Syncs Firebase UID to Django `User` model automatically.

## 🧪 Testing

```bash
python manage.py test game_engine
```

## 🚀 Deployment

### Dependencies
*   Python 3.11+
*   Allowed Hosts, Secret Key, Debug Mode via Environment Variables.

### Docker
```bash
docker build -t arth-neeti-backend .
docker run -p 8000:8000 arth-neeti-backend
```
