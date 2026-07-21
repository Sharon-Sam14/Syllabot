# Syllabot AI Context Ledger

> Strict instruction: Update this document after every major coding session so project context is never lost. Preserve decisions, progress, open questions, and next steps here.

## Current Status
- **Core AI Backend Architecture**: Upgraded to a production-grade Agentic AI Study Planning Platform.
- **Workflow Orchestration**: Implemented LangGraph StateGraph engine with task-based routing (Gemini for reasoning/parsing, Groq for high-speed plan and quiz generation).
- **Persistent AI Memory**: Built user-specific learning profile memory (`UserMemory` database table and `DatabaseMemory` backend logic) tracking strengths, weaknesses, preferences, and streaks.
- **Database Layer**: Production database fully configured with Supabase PostgreSQL connection pooler (Session mode, IPv4 compatible) and SQLite fallback for local development.
- **Security & Stability**: Hardened system with JWT checks, input sanitization, SlowAPI rate-limiting, and dynamic CORS matching for all `*.vercel.app` production and preview domains.
- **Production Deployment**: Live on Render (`https://syllabot-backend.onrender.com`) and Vercel (`https://syllabot-three.vercel.app`).
- **Validation**: 100% test coverage passing (65 out of 65 backend tests passing) and Next.js frontend building successfully without errors.

## Active Context
- The product is configured with smart fallback models (Gemini 3.5 Flash and Llama 3.3).
- Model routing dynamically chooses the optimal provider per task, reducing API costs and latency.
- In-memory conversation memory (`InMemoryMemory`) maintains ephemeral chat states, while `DatabaseMemory` persists user learning statistics.
- If API keys are missing, the system handles calls gracefully by raising structured exception payloads mapped to HTTP 503 Service Unavailable responses instead of crashing.
- `backend/alembic.ini` configured with `script_location = %(here)s/alembic` and `prepend_sys_path = %(here)s/..` to resolve Render root directory execution.
- `frontend/src/lib/api.ts` implements smart domain detection to automatically target the live Render backend when deployed on Vercel.

## Important Product Decisions
- The planner remains adaptive and updates dynamically based on student check-ins.
- Prompt injection protection sanitizes inputs at multiple layers before passing payloads to AI nodes.
- SQLite remains supported for single-file, Zero-Config local development setups.
- Supabase connection pooler (Session mode on port 5432) is required for Render deployments to avoid IPv6 unreachable errors.

## Next Steps
- Monitor live user traffic and syllabus uploads on Render & Vercel.
- Run end-to-end user-experience testing on plan adaptations and quiz generated structures.
- Expand analytics dashboard for student study streaks and topic mastery.

## AI Agent Notes
- Model router handles provider exceptions by dynamically switching to fallback providers.
- Graph compilation is thread-safe and cached via `lru_cache` to optimize memory and latency.

---

## Last Updated
- 2026-07-21