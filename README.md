# Aptiverse - AI-Powered Aptitude Practice & Battle Platform

A comprehensive full-stack aptitude practice platform featuring AI-powered question recommendations, real-time multiplayer battles, and an extensive question bank with community discussions.

## Features

### Core Features
- **Daily Practice** - AI-curated personalized practice sets based on weak areas
- **Question Bank** - Browse 1000+ aptitude questions across multiple categories
- **Battle Mode** - Real-time multiplayer competitions with WebSocket support
- **Discussions** - Community discussions with voting on each question
- **Progress Tracking** - Detailed analytics, streaks, and performance metrics
- **Badges & Achievements** - Gamification with unlockable badges
- **Event-driven rewards engine** - Kafka-powered real-time gamification system

### AI & ML Features
- **Weak Area Detection** - Naive Bayes classifier identifies struggling topics
- **Vector Similarity Search** - Weaviate-powered semantic question recommendations
- **Adaptive Difficulty** - Hybrid difficulty system adjusts to user performance
- **Personalized Practice** - Customizable settings for daily practice sessions

### Admin Dashboard
- **User Management** - Ban/unban, warnings, password resets
- **Question Management** - Bulk upload, edit, delete questions
- **Report Handling** - Community report moderation
- **Analytics** - Platform-wide statistics and logs

## Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - SQL ORM with PostgreSQL/SQLite support
- **WebSockets** - Real-time battle communication
- **Weaviate** - Vector database for AI recommendations
- **Scikit-learn** - ML for weak area prediction
- **Kafka** - Event streaming for gamification engine

### Frontend
- **React 18** - Modern UI library
- **TailwindCSS** - Utility-first styling
- **React Router** - Client-side routing
- **WebSocket API** - Real-time updates
- **Context API** - State management

### Infrastructure
- **Docker** - Containerization
- **Fly.io** - Backend deployment
- **Vercel** - Frontend deployment
- **PostgreSQL** - Production database
- **Redis** - Caching and session storage

## Project Structure

```
Aptiverse V1/
├── backend/
│   ├── main.py              # FastAPI app & routes
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # JWT authentication
│   ├── admin_routes.py      # Admin API endpoints
│   ├── admin_questions.py   # Question management
│   ├── battle_manager.py    # Battle room logic
│   ├── ml_service.py        # ML recommendation engine
│   ├── vector_service.py    # Weaviate integration
│   ├── hybrid_difficulty.py # Adaptive difficulty
│   ├── cache.py             # Response caching
│   └── database.py          # DB configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js
│   │   │   ├── PracticeSet.js
│   │   │   ├── QuestionBank.js
│   │   │   ├── BattleRoom.js
│   │   │   ├── AdminDashboard.js
│   │   │   └── ...
│   │   ├── context/
│   │   │   └── AuthContext.js
│   │   └── config/
│   │       └── api.js
│   └── public/
├── docker-compose.yml
└── Documentation files (*.md)
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (optional)

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

### Docker
```bash
docker-compose up --build
```

Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Login & get JWT |
| GET | `/verify-email` | Verify email token |
| GET | `/me` | Get current user |

### Practice & Questions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/daily-practice` | Get personalized practice set |
| POST | `/submit-answer` | Submit answer & get feedback |
| GET | `/weak-areas` | Get ML-detected weak topics |
| GET | `/question-bank/categories` | List all categories |
| GET | `/question-bank/questions` | Browse questions |
| GET | `/question-bank/question/{id}` | Get question details |

### Discussions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/discussions/{question_id}` | Get discussions |
| POST | `/discussions` | Create discussion |
| POST | `/discussions/{id}/vote` | Vote on discussion |
| POST | `/discussions/{id}/report` | Report discussion |

### Battles
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/battles/create` | Create battle room |
| POST | `/battles/{code}/join` | Join battle |
| POST | `/battles/{code}/start` | Start battle |
| GET | `/battles/history` | Get battle history |
| WS | `/ws/battle/{code}` | Battle WebSocket |

### Admin (requires admin role)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | List all users |
| POST | `/admin/users/{id}/ban` | Ban user |
| POST | `/admin/questions/upload` | Bulk upload questions |
| GET | `/admin/reports` | View community reports |
| GET | `/admin/stats` | Platform statistics |

## Database Models

- **User** - Account info, XP, streaks, role
- **Question** - Multi-category aptitude questions
- **QuestionAttempt** - User answer history
- **BattleRoom** - Multiplayer battle sessions
- **BattleParticipant** - Battle player scores
- **Discussion** - Question discussions
- **DiscussionVote** - Upvote/downvote tracking
- **Badge** / **UserBadge** - Achievement system
- **AdminActionLog** - Admin audit trail
- **ReportedPost** - Community reports
- **UserWarning** - User warnings

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/aptiverse

# Auth
SECRET_KEY=your-secret-key

# Email (optional)
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
SKIP_EMAIL_VERIFICATION=false

# Frontend
FRONTEND_URL=http://localhost:3000

# Weaviate (optional, for AI features)
WEAVIATE_URL=your-weaviate-url
WEAVIATE_API_KEY=your-api-key
```

## Documentation

| Document | Description |
|----------|-------------|
| [BATTLE_ARCHITECTURE.md](BATTLE_ARCHITECTURE.md) | Battle system design |
| [BATTLE_ROOM_GUIDE.md](BATTLE_ROOM_GUIDE.md) | Battle feature usage |
| [AI_RECOMMENDATION_SYSTEM.md](AI_RECOMMENDATION_SYSTEM.md) | ML recommendation details |
| [ADMIN_SYSTEM_GUIDE.md](ADMIN_SYSTEM_GUIDE.md) | Admin panel guide |
| [QUESTION_UPLOAD_FORMAT.md](QUESTION_UPLOAD_FORMAT.md) | Bulk upload format |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Production deployment |
| [GMAIL_SETUP.md](GMAIL_SETUP.md) | Email configuration |
| [MODULE_4_EVENT_DRIVEN_GAMIFICATION.md](MODULE_4_EVENT_DRIVEN_GAMIFICATION.md) | Event-driven gamification engine |

## Production Deployment

The app is configured for deployment on:
- **Backend**: Fly.io (`fly.backend.toml`)
- **Frontend**: Vercel (`vercel.json`) or Fly.io (`frontend/fly.toml`)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with FastAPI, React, and AI-powered recommendations**
