# Syllabot

Syllabot is an adaptive, production-grade AI Study Planning Platform designed to act as the **"Google Maps for your syllabus."** It transforms messy, free-text syllabus content into structured topic trees, constructs realistic daily schedules weighted by importance, logs check-ins, and dynamically re-plans in real-time when students fall behind.

---

## 🚀 Key Features

* **Syllabus Parsing**: Uses Google Gemini to turn unstructured syllabi documents or text dumps into clean, parent-child topic JSON hierarchies.
* **Adaptive Planning Engine**: Generates study plans using spaced-repetition logic, complexity weights, and target exams dates.
* **Real-time Replanning**: Monitors daily logged progress and automatically recalibrates upcoming schedules if a student slips behind.
* **Neural Assist Chatbot**: Built with a LangGraph state machine. Provides:
  - Contextual responses to user syllabus questions.
  - Multi-choice quiz generation (`quiz_node`) on study plan topics.
  - Topic explanations and breakdowns (`summarize_node`).
  - Study pattern analysis (`check_progress_node`).
* **Resilient Routing & Fallbacks**: Features a central ModelRouter with a 60-second cooldown health cache. If Gemini experiences outages (429/503), the application auto-switches to Groq (Llama 3.3) seamlessly.

---

## 🛠️ Technology Stack

* **Frontend**: Next.js 16 (TypeScript, Tailwind CSS, Custom Cursor, Flip-Clock, Interactive Dashboard).
* **Backend**: FastAPI (Python 3.13), slowapi (Rate Limiter), slowapi CORS checks.
* **Database**: PostgreSQL (SQLAlchemy ORM + Alembic for migrations).
* **Orchestration**: LangGraph, LangChain Core.
* **LLM APIs**: Google Generative AI (Gemini 2.5 Pro/Flash), Groq (Llama 3.3 70B).

---

## 📂 Project Structure

```text
syllabot/
├── backend/                  # FastAPI Application
│   ├── ai/                   # Agent logic, LangGraph workflow, providers (Gemini/Groq)
│   ├── api/v1/               # Router endpoints (auth, syllabi, plans, progress)
│   ├── core/                 # Config settings, logging configuration, serializers
│   ├── models/               # SQLAlchemy Database schemas
│   └── tests/                # 65+ unit & integration tests
├── frontend/                 # Next.js Application
│   ├── src/app/              # Next.js page routers
│   ├── src/components/       # UI Components (Dashboard, Intake, Clock, Auth)
│   └── src/lib/              # API clients & network bindings
└── docs/                     # System design and architecture specs
```

---

## ⚙️ Local Development Setup

### 1. Database Provisioning
Configure a PostgreSQL database locally, or use a SQLite fallback file (`sqlite:///./syllabot.db`).

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables. Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
5. Run migrations to initialize the database:
   ```bash
   alembic upgrade head
   ```
6. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Copy environment configurations and set `NEXT_PUBLIC_API_URL` to `http://localhost:8000`:
   ```bash
   npm run dev
   ```

---

## 📚 Documentation Reference

Detailed documentation is located in the root and `/docs` directory:
* **[Architecture.md](Architecture.md)** — High-level system design.
* **[docs/AI_INFRASTRUCTURE.md](docs/AI_INFRASTRUCTURE.md)** — ModelRouter, health cache, message normalization, and providers details.
* **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** — Complete step-by-step production setup guide for **Supabase**, **Render**, and **Vercel**.
* **[Memory.md](Memory.md)** — System state and development phases tracking.
