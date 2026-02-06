# Backend - Arth-Neeti Game Engine

Django REST API powering the Arth-Neeti financial literacy game.

## 🏗️ Architecture

```
backend/
├── core/                 # Django project settings
│   ├── settings.py       # Configuration
│   └── urls.py           # Root URL routing
├── game_engine/          # Main app
│   ├── models.py         # Database models
│   ├── views.py          # API endpoints
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # App routes
│   └── management/
│       └── commands/
│           └── seed_scenarios.py  # Card seeder
└── requirements.txt
```

## 📊 Data Models

### GameSession
Tracks a player's game state.

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | Player account |
| `wealth` | Integer | Current balance (starts: ₹25,000) |
| `happiness` | Integer | 0-100 scale (Well-being) |
| `credit_score` | Integer | 300-900 range (CIBIL norm) |
| `portfolio` | JSONField | Stock holdings: `{"TECH": 10, ...}` |
| `lifelines` | Integer | Hints remaining (starts: 3) |
| `current_month` | Integer | Game progress (1-12) |
| `is_active` | Boolean | Game in progress |

### PlayerProfile
Persistent player statistics.

| Field | Type | Description |
|-------|------|-------------|
| `highest_credit_score` | Integer | Best anytime credit score |
| `highest_happiness` | Integer | Best well-being index |
| `highest_stock_profit` | Integer | Best portfolio value |
| `financial_literacy` | Integer | Knowledge score (0-100) |

### ScenarioCard
Financial decision scenarios.

| Field | Type | Description |
|-------|------|-------------|
| `title` | String | Scenario name |
| `description` | Text | Situation details |
| `category` | Enum | NEEDS, WANTS, INVESTMENT, TRAP, etc. |
| `difficulty` | Integer | 1-5 scale |
| `min_month` | Integer | Earliest month to appear |

### Choice
Options for each scenario.

| Field | Type | Description |
|-------|------|-------------|
| `text` | String | Choice description |
| `wealth_impact` | Integer | Money change |
| `happiness_impact` | Integer | Happiness change |
| `credit_impact` | Integer | Credit score change |
| `is_recommended` | Boolean | NCFE-approved choice |
| `feedback` | Text | Educational explanation |

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/start-game/` | Create new session |
| GET | `/api/get-card/{session_id}/` | Get next scenario |
| POST | `/api/submit-choice/` | Submit player choice |
| GET | `/api/session/{session_id}/` | Get session state |
| POST | `/api/use-lifeline/` | Use hint (costs 1 lifeline) |

### Example: Start Game
```bash
curl -X POST http://localhost:8000/api/start-game/
```

Response:
```json
{
  "session": {
    "id": 1,
    "wealth": 25000,
    "happiness": 100,
    "credit_score": 700,
    "lifelines": 3,
    "current_month": 1
  }
}
```

## 🎮 Game Logic

### Month Progression
- 3 cards per month
- 12 months total = 36 cards for complete game

### Win/Loss Conditions
| Condition | Trigger | Result |
|-----------|---------|--------|
| COMPLETED | Month > 12 | Victory! |
| BANKRUPTCY | Wealth ≤ 0 | Game Over |
| BURNOUT | Happiness ≤ 0 | Game Over |

### Financial Personas
Based on `financial_literacy` score:
- 80+ → Warren Buffett
- 60-79 → Cautious Saver
- 40-59 → Balanced Spender
- 20-39 → YOLO Enthusiast
- <20 → FOMO Victim

## 🧪 Testing

```bash
python manage.py test game_engine
```

## 🚀 Deployment

### Environment Variables
```env
DEBUG=False
SECRET_KEY=your-production-key
DATABASE_URL=postgres://user:pass@host:5432/dbname
DJANGO_ALLOWED_HOSTS=yourdomain.com
```

### Docker
```bash
docker build -t arth-neeti-backend .
docker run -p 8000:8000 arth-neeti-backend
```
