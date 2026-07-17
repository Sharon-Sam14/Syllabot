# AI Generation Rules for Syllabot

## 1. Purpose
These rules define the boundaries for all future AI-assisted development on Syllabot. They are intended to keep the project correct, maintainable, and aligned with the product vision.

## 2. Core Engineering Rules
- Write modular, DRY, and well-structured code.
- Prefer standard library solutions before introducing unnecessary dependencies.
- Keep functions small, composable, and readable.
- Favor explicit logic over hidden magic.
- Write code that is easy to test and easy to extend.

## 3. Syllabus Integrity Rules
- Do not hallucinate syllabus topics, chapters, modules, or learning outcomes.
- Adhere strictly to the user-provided syllabus input.
- If information is ambiguous, preserve uncertainty rather than inventing structure.
- When confidence is low, mark the content as low-confidence instead of fabricating detail.

## 4. AI Reliability Rules
- Implement graceful degradation for LLM API failures.
- Use exponential backoff and retry logic for transient failures.
- Fallback to deterministic, rule-based behavior when AI services are unavailable or rate-limited.
- Avoid unnecessary AI calls when the task can be completed safely with local logic.

## 5. Phase Discipline Rules
- Do not jump ahead to future phases defined in the project phases document.
- Implement the current phase fully before moving to the next.
- Keep feature scope aligned with the active milestone.
- Avoid premature premium or enterprise features unless explicitly approved.

## 6. Product and UX Rules
- Keep the experience calm, helpful, and low-friction.
- Do not create interfaces that increase exam stress or overwhelm the user.
- Favor clear progress and simple direction over aggressive gamification.

## 7. Testing and Verification Rules
- Add or update tests when introducing meaningful behavior changes.
- Verify that parsing, planning, and replanning logic behave correctly on realistic examples.
- Prefer deterministic tests over brittle AI-dependent assertions.

## 8. Agent-Specific Rules
- If building AI agents, keep them bounded to clear responsibilities.
- Ensure agent outputs are structured and validated.
- Never allow an agent to silently invent knowledge that was not supplied by the user or the system prompt.
- Maintain a clear separation between planning, execution, and validation logic.

## 9. Final Rule
If a requirement is unclear, ask for clarification rather than guessing.

---

## Document Status
- Status: Draft
- Owner: Engineering
- Last Updated: 2026-07-17