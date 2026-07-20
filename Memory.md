# Syllabot AI Context Ledger

> Strict instruction: Update this document after every major coding session so project context is never lost. Preserve decisions, progress, open questions, and next steps here.

## Current Status
- **Core AI Backend Architecture**: Upgraded to a production-grade Agentic AI Study Planning Platform.
- **Workflow Orchestration**: Implemented LangGraph StateGraph engine with task-based routing (Gemini for reasoning/parsing, Groq for high-speed plan and quiz generation).
- **Persistent AI Memory**: Built user-specific learning profile memory (`UserMemory` database table and `DatabaseMemory` backend logic) tracking strengths, weaknesses, preferences, and streaks.
- **Database Layer**: Migrated database configurations to fully support production-ready PostgreSQL connection pooling while retaining SQLite fallback for local development.
- **Security & Stability**: Hardened system with JWT checks, input sanitization against prompt injection, SlowAPI rate-limiting, and locked CORS mappings.
- **Frontend Integration**: Fully wired Next.js dashboard with a functional "Neural Assist" AI Chat tab reusing the premium UI theme and design patterns.
- **Validation**: 100% test coverage passing (56 out of 56 backend tests passing) and Next.js frontend building successfully without errors.

## Active Context
- The product is configured with smart fallback models (Gemini 1.5 Flash and Llama 3.3).
- Model routing dynamically chooses the optimal provider per task, reducing API costs and latency.
- In-memory conversation memory (`InMemoryMemory`) maintains ephemeral chat states, while `DatabaseMemory` persists user learning statistics.
- If API keys are missing, the system handles calls gracefully by raising structured exception payloads mapped to HTTP 503 Service Unavailable responses instead of crashing.

## Important Product Decisions
- The planner remains adaptive and updates dynamically based on student check-ins.
- Prompt injection protection sanitizes inputs at multiple layers before passing payloads to AI nodes.
- SQLite remains supported for single-file, Zero-Config local development setups.

## Next Steps
- Obtain production Gemini/Groq API keys and configure them in `.env`.
- Deploy the PostgreSQL instance and set `DATABASE_URL` in the deployment environment.
- Run user-experience testing on plan adaptations and quiz generated structures.

## AI Agent Notes
- Model router handles provider exceptions by dynamically switching to fallback providers.
- Graph compilation is thread-safe and cached via `lru_cache` to optimize memory and latency.

---

## Last Updated
- 2026-07-20