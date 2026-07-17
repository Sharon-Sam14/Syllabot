# Syllabot AI Context Ledger

> Strict instruction: Update this document after every major coding session so project context is never lost. Preserve decisions, progress, open questions, and next steps here.

## Current Status
- Project concept defined: Syllabot, an adaptive study planner for syllabi
- Core product idea established: parse syllabus input, generate daily plans, and adapt when the student falls behind
- Initial documentation scaffold created for product, architecture, phases, design, rules, and memory tracking
- The project is currently in early planning and scaffolding stages

## Active Context
- The product is being built as a modern web application with:
  - React/Next.js frontend
  - Python backend
  - PostgreSQL database
- The backend parsing engine must support deeply nested syllabus hierarchies
- The system will eventually include AI-driven planning and replanning behaviors
- The architecture should support future AI agents for parsing, planning, and review tasks

## Important Product Decisions
- The planner should be adaptive rather than static
- The experience should feel calm and supportive, not stressful
- Syllabus topics must be preserved from user input and never invented
- The initial implementation should prioritize correctness and reliability over overly aggressive automation

## Open Questions
- Which parsing strategy will be used for the first production version: deterministic parser, LLM-assisted parser, or hybrid?
- How much user input should be required for topic importance weighting?
- Which daily check-in signals should be collected first: hours studied, topics completed, or a simple yes/no progress marker?

## Next Steps
- Scaffold the frontend and backend project structure
- Implement initial syllabus ingestion and validation endpoints
- Build the first deterministic parsing pipeline for nested syllabus content
- Create the first static plan generation flow
- Add daily progress tracking and the initial replanning loop

## AI Agent Notes
- Future agents should be task-specific and bounded in responsibility
- Agent outputs should be validated and structured before influencing user-facing planning
- The system should remain deterministic where possible and degrade gracefully when AI services fail

---

## Last Updated
- 2026-07-17