# Contributing to Arth-Neeti

Thank you for your interest in contributing! 🎉

## 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/yourusername/arth-neeti.git
   ```
3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 💻 Development Setup

### Backend
```bash
cd arth-neeti-game/backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_scenarios
python manage.py runserver
```

### Frontend
```bash
cd arth-neeti-game/frontend
npm install
npm run dev
```

## 📝 Types of Contributions

### 🃏 New Scenario Cards
Add cards to `backend/game_engine/management/commands/seed_scenarios.py`:

```python
{
    'title': "Your Scenario Title",
    'description': "Detailed situation...",
    'category': 'INVESTMENT',  # NEEDS, WANTS, TRAP, etc.
    'difficulty': 2,
    'min_month': 1,
    'choices': [
        {
            'text': "Option A",
            'wealth_impact': -5000,
            'happiness_impact': 10,
            'credit_impact': 0,
            'literacy_impact': 10,
            'feedback': "Educational explanation...",
            'is_recommended': True
        },
        # Add 2-3 choices
    ]
}
```

### 🐛 Bug Fixes
1. Check existing issues
2. Create a new issue if needed
3. Reference issue number in PR

### ✨ New Features
1. Open an issue first to discuss
2. Keep changes focused
3. Add tests if applicable

## 📋 Pull Request Guidelines

### Checklist
- [ ] Code follows existing style
- [ ] Changes tested locally
- [ ] README updated if needed
- [ ] No console errors

### PR Title Format
```
[TYPE] Brief description

Types: feat, fix, docs, style, refactor, test
```

Examples:
- `[feat] Add UPI payment scenario`
- `[fix] Correct credit score calculation`
- `[docs] Update API documentation`

## 🧪 Testing

### Backend
```bash
python manage.py test game_engine
```

### Manual Testing Checklist
- [ ] Start new game successfully
- [ ] Complete 12-month game
- [ ] Use all 3 lifelines
- [ ] Refresh page and resume game
- [ ] Print certificate

## 📁 Code Style

### Python
- Follow PEP 8
- Use docstrings for functions
- Type hints appreciated

### JavaScript
- ES6+ syntax
- Functional components
- Props destructuring

## 🏷️ Issue Labels

| Label | Description |
|-------|-------------|
| `good first issue` | Great for newcomers |
| `bug` | Something isn't working |
| `enhancement` | New feature request |
| `content` | New scenario cards |
| `documentation` | Docs improvements |

## 💬 Questions?

Open an issue with the `question` label.

---

**Thank you for contributing!** 🙏
