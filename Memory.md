# Syllabot AI Context Ledger

> Strict instruction: Update this document after every major coding session so project context is never lost. Preserve decisions, progress, open questions, and next steps here.

## Current Status
- Project concept defined: Syllabot, an adaptive study planner for syllabi
- Phase 1 backend scaffolding (FastAPI, SQLAlchemy models, JWT auth) is fully complete.
- Phase 2 backend (custom stack-based shift-reduce parser, static study planner, API integrations) is fully complete.
- Phase 3 backend (adaptive replanning loop engine, auto-replanning check-ins, manual replan API) is fully complete.
- 14/14 unit and integration tests are passing successfully.

## Active Context
- The product is being built as a modern web application with:
  - React/Next.js frontend
  - Python backend (FastAPI, SQLite for local dev, Postgres compatible)
- The backend parsing engine successfully extracts nested hierarchies deterministically.
- The planning engine automatically spreads topics over a start-end date range, grouping or spacing with review days.
- The replanner dynamically updates the database schedule when a student falls behind, preserving completed workload history.

## Important Product Decisions
- The planner should be adaptive rather than static
- The experience should feel calm and supportive, not stressful
- Syllabus topics must be preserved from user input and never invented
- The initial implementation should prioritize correctness and reliability over overly aggressive automation
- The application will strictly use open-source, free-tier compatible, and easy-to-deploy technologies (e.g. SQLite database, minimal runtime dependency footprint, zero-cost service structures)

## Open Questions
- What daily check-in signals will trigger the replanning threshold (e.g., how many days behind, or is it triggered on any deviation)?
- What visual cues should be used in the UI to present the changes of an adapted schedule without causing student panic?

## Next Steps
- Scaffold the Next.js frontend project structure
- Build frontend login, signup, and profile session views
- Implement syllabus upload and plan visualization dashboard
- Connect frontend components to backend endpoints (Auth, Ingestion, Plans, Progress, Replanning)

## AI Agent Notes
- Future agents should be task-specific and bounded in responsibility
- Agent outputs should be validated and structured before influencing user-facing planning
- The system should remain deterministic where possible and degrade gracefully when AI services fail

---

## Last Updated
- 2026-07-18