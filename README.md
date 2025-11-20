# Personalized E-Learning Dashboard

Modern, adaptive learning platform with module-driven quizzes, forum discussions, and gamified progress.

## Features
- Authentication with login/signup.
- Module catalog with user-selected subjects; quizzes are gated to chosen modules.
- Adaptive quizzes (easy/medium/hard), 5 questions per session, timer support, no question repeats per session.
- Question pools seeded from `backend/question_seed_data.py` (10 curated modules, 5 questions per difficulty).
- Dashboard with per-module average (last 5 quiz attempts), streaks, and tiered badges (Bronze, Silver, Gold, Platinum, Ruby).
- Threaded forum with topic picker (General, Cloud Computing, Web Design with JavaScript, Data Structures, Deep Learning) and nested replies.
- Health check at `/health` for deployment platforms.

## Tech Stack
- Frontend: React + React-Bootstrap (CRA), environment-driven API base.
- Backend: Flask + SQLAlchemy, SQLite by default.
- Deployment: Frontend on Vercel, Backend on Railway (Python 3.11).

## Quick Start (Local)
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate on mac/linux
pip install -r requirements.txt
python app.py  # serves on http://localhost:5000

# Frontend (new shell)
cd frontend
npm install
npm start  # serves on http://localhost:3000
```

## Environment Variables
- Frontend: `REACT_APP_API_BASE` (e.g., `http://localhost:5000` or your Railway URL).
- Backend (optional overrides): `PORT`, `SQLALCHEMY_DATABASE_URI` (defaults to `sqlite:///db.sqlite`), `SECRET_KEY`.

## Data & Seeding
- Quiz/question content lives in `backend/question_seed_data.py`. On backend startup, `seed_question_pool()` loads/updates questions.
- Module progress and forum data persist in `backend/db.sqlite` (or your configured DB).

## Deployment Notes
- **Backend (Railway):**
  - Build: `pip install -r backend/requirements.txt`
  - Start: `python app.py`
  - Health check path: `/health`
  - Use a mounted volume for SQLite (e.g., `/app/data/db.sqlite`) or set `SQLALCHEMY_DATABASE_URI` to a hosted DB.
- **Frontend (Vercel):**
  - Project root: `frontend`
  - Build: `npm run build`
  - Output dir: `build`
  - Env: `REACT_APP_API_BASE=https://<your-backend-host>`

## Key Behaviors
- Quizzes are only available for modules the user selected in the Modules page.
- Each quiz session serves 5 unique questions; difficulty adapts per answer.
- Dashboard progress per module is the average of the last 5 quiz attempts for that module; badges are derived from that average.

## Health Check
`GET /health` → `200 {"status": "ok"}` (used by Railway).

## Repository Layout
- `backend/` – Flask app, models, seeds (`question_seed_data.py`), API routes.
- `frontend/` – React app (Dashboard, Quiz, Forum, Modules).
- `docs/PROJECT_BINDER.md` – Detailed requirements, architecture, and maintenance notes.
