# Architecture Audit: Syllabot v2

This document provides a comprehensive audit of the Syllabot codebase before and after the transition to the **Agentic AI Study Planning Platform**.

---

## 1. Folder Structure & Modularization

### Original Structure
- Core AI code was located in a single directory `backend/ai/`.
- Logic was heavily coupled in `agent.py` and `services.py` with direct HTTP calls and manually managed loops.
- SQLite was hardcoded directly in database connection pools.

### Audited & Refactored Structure
```
backend/
├── ai/
│   ├── graph/           # LangGraph StateGraph, nodes, and conditional edges
│   │   ├── __init__.py
│   │   ├── edges.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   └── workflow.py
│   ├── providers/       # Abstraction layer for AI model providers
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── gemini.py
│   │   ├── groq.py
│   │   └── router.py
│   ├── agent.py         # Refactored Orchestrator forwarding to LangGraph
│   ├── memory.py        # Ephemeral (In-Memory) & Persistent (Database-backed) Memory
│   ├── prompts.py       # Centralized system and tool declarations
│   └── tools.py         # Modular DB-layer tools called by AI
├── core/
│   ├── config.py        # Centralized settings (Pydantic-Settings)
│   ├── database.py      # PostgreSQL pooling with SQLite fallback
│   ├── logging_config.py# Structured JSON logging pipeline
│   └── sanitizer.py     # Input sanitization and prompt injection protection
```

---

## 2. Dependency Graph & AI Stack

The platform's external packages were audited and updated in `backend/requirements.txt`:
1. **LangGraph (`langgraph`)**: Used to replace the legacy iterative loop in `agent.py` with a StateGraph workflow.
2. **Google GenAI (`langchain-google-genai`)**: Used for Gemini reasoning, syllabus semantic parsing, and topic categorization.
3. **Groq (`langchain-groq`)**: Used for high-speed, hardware-accelerated study plan and quiz generation.
4. **SlowAPI (`slowapi`)**: Used for rate-limiting public-facing endpoints (100 req/min global, 20 req/min for AI).
5. **Python-JSON-Logger (`python-json-logger`)**: Used to implement production-grade structured JSON logging.
6. **Psycopg2 (`psycopg2-binary`)**: Added for production PostgreSQL connectivity.

---

## 3. API Routes & Communication Contracts

The API layer utilizes FastAPI and validates all payloads via Pydantic schemas:
- `/api/v1/auth`: JWT-based user authentication.
- `/api/v1/syllabi`: Syllabus ingestion, file uploads, and parsing triggers.
- `/api/v1/plans`: Study plan CRUD and scheduling.
- `/api/v1/progress`: Log completed topics, study hours, and check-in notes.
- `/api/v1/ai/chat`: Primary chat gateway (now routes through LangGraph).
- `/api/v1/ai/status`: Health check returning Gemini/Groq model status to the frontend.

---

## 4. Security & Vulnerability Analysis

The security review identified and patched the following areas:
- **Prompt Injection**: Created `backend/core/sanitizer.py` with case-insensitive regular expressions to strip system-instruction overrides.
- **Context Denial of Service**: Set character caps (4,000 for chat, 1,000 for check-in notes, 50,000 for syllabus files) to prevent LLM context-window exhaustion.
- **CORS Configuration**: Restrained middleware to `FRONTEND_URL` in production (defaulting to wildcards only in development).
- **Authentication**: Verified JWT signatures on every request using standard dependency injection.

---

## 5. Performance & Resource Bottlenecks

- **Model Routing**: Implemented a singleton `ModelRouter` with task-based mapping (`TASK_PROVIDER_MAP`) to send lightweight requests to Groq (Llama 3.3) and reasoning tasks to Gemini (Gemini 1.5 Flash).
- **Lazy Compilations**: Compiled the LangGraph `StateGraph` as an `lru_cache` singleton so it only compiles on startup or on the first request and is reused instantly.
- **Connection Pools**: Configured SQLAlchemy connection pooling with `pool_size` and `max_overflow` for PostgreSQL to handle high concurrent traffic.
