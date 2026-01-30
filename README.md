# 🎮 Arth-Neeti: Financial Literacy Through Gamification

> A card-based financial decision-making game that teaches young Indians smart money habits through real-life scenarios.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![React](https://img.shields.io/badge/react-18+-61DAFB.svg)

## 🎯 What is Arth-Neeti?

Arth-Neeti ("Financial Wisdom" in Hindi) is an interactive game where players make financial decisions through scenario cards. Each choice impacts their:

- 💰 **Wealth** - Your bank balance
- 😊 **Happiness** - Life satisfaction
- 📊 **Credit Score** - Financial reputation

Complete 12 months of decisions to discover your **Financial Persona**!

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🃏 **36+ Scenario Cards** | Real-life situations: investments, scams, social pressure |
| 💡 **Lifelines (Ask NCFE)** | 3 hints per game reveal recommended choices |
| 🔊 **Audio Feedback** | Sound effects for gains/losses |
| 📱 **Session Persistence** | Resume games after browser refresh |
| 🖨️ **Printable Certificate** | Download your Financial Health Report |
| 🐳 **Docker Ready** | One-command deployment |

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/adityatawde9699/arth-neeti.git
cd arth-neeti/arth-neeti-game
docker-compose up --build
```

Open http://localhost:5173

### Option 2: Manual Setup

**Backend:**
```bash
cd arth-neeti-game/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_scenarios
python manage.py runserver
```

**Frontend:**
```bash
cd arth-neeti-game/frontend
npm install
npm run dev
```

## 📁 Project Structure

```
arth-neeti-game/
├── backend/           # Django REST API
│   ├── game_engine/   # Core game logic
│   └── core/          # Django settings
├── frontend/          # React + Vite
│   └── src/
│       ├── components/  # UI components
│       └── api/         # API client
└── docker-compose.yml   # Full stack orchestration
```

## 🎓 Educational Value

Built for the **NCFE Financial Literacy Hackathon**, Arth-Neeti teaches:

- Emergency fund importance
- Investment basics (SIP, ELSS, NPS)
- Scam awareness (MLM, Ponzi, phishing)
- Credit score management
- Budgeting and lifestyle choices

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, CSS3 |
| Backend | Django 5, Django REST Framework |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Deployment | Docker, Docker Compose |

## 📄 Documentation

- [Backend README](./arth-neeti-game/backend/README.md) - API endpoints, models
- [Frontend README](./arth-neeti-game/frontend/README.md) - Components, state management
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](./CONTRIBUTING.md).

## 📝 License

Proprietary License - see [LICENSE](./LICENSE) for details.

## 🙏 Acknowledgments

- **NCFE** - National Centre for Financial Education
- **RBI** - For financial literacy resources

---

*Made with ❤️ for the NCFE Hackathon*
