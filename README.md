# Can You Code — AI Code Review with Personality

> Paste your code. Pick a personality. Let the AI find the bugs and roast your code.

**Can You Code** blends real static analysis with human-style code review. The engine detects genuine issues — complexity, security flaws, style violations — then rewrites them with personality, from *Gordon Ramsay But For Code* to *The Encouraging Mentor*.

## Core Features

- **Multi-language static analysis** — Python, Java, C, C++, JavaScript, and TypeScript with auto-detection
- **12 distinct reviewer personalities** — select your preferred roast or mentoring style
- **Real-time streaming feedback** — streamed progressive responses via Server-Sent Events (SSE)
- **Dark & light luxury themes** — seamless switching with persistent user preference
- **Shareable review links** — permanent public links for every code critique

## Quick Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env      # set your GEMINI_API_KEY
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`, paste your code, pick a personality, and click **Roast My Code**.

## Environment Variables

| Name | Description |
|------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key (required) |
| `DATABASE_URL` | SQLite database path |
| `CORS_ORIGINS` | Allowed CORS origins list |

## Technology Stack

- **Backend:** FastAPI, SQLAlchemy (SQLite), Pydantic, Google GenerativeAI (`gemini-1.5-flash`)
- **Frontend:** React 19 + Vite + TypeScript + Tailwind CSS
