# Architecture Overview

## 1. Product Vision
Syllabot is a multi-layered learning platform that combines a modern web frontend, a robust Python backend, and an intelligent planning engine. The architecture is designed to support three core capabilities:
- parsing free-text syllabus input
- generating initial study plans
- continuously adapting the plan when a student falls behind

The system is also designed with an AI-agent-oriented future in mind, where planning, review, and coaching tasks can be delegated to specialized agents.

## 2. High-Level Application Flow
1. A user enters a syllabus in free text through the web app.
2. The frontend sends the input to the backend API.
3. The backend parsing engine converts the syllabus into a structured hierarchy.
4. The planning engine generates an initial daily study plan.
5. The user updates progress through daily check-ins.
6. The backend evaluates whether the student is behind and triggers replanning.
7. The UI displays the revised plan and any retention or review prompts.

## 3. System Architecture
### 3.1 Frontend
- Framework: React with Next.js
- Rendering: server-rendered and client-rendered components where appropriate
- Primary responsibilities:
  - syllabus input capture
  - plan visualization
  - daily progress logging
  - reminder and review presentation

### 3.2 Backend
- Language: Python
- Framework: FastAPI (recommended) or Flask if a lighter footprint is preferred
- Primary responsibilities:
  - syllabus ingestion and validation
  - parsing orchestration
  - planning logic
  - adaptive replanning
  - persistence and retrieval of study state

### 3.3 Data Layer
- Database: PostgreSQL
- Storage responsibilities:
  - users and authentication state
  - syllabi and parsed topic trees
  - study plans and daily progress records
  - review checkpoints and retention data

### 3.4 AI/Agent Layer
- The backend will host a planning agent and, later, supporting agents for:
  - parsing and structure extraction
  - plan adjustment and prioritization
  - review prompt generation
- These agents should interact through structured interfaces, not ad hoc prompting.

## 4. Core Modules
### 4.1 Auth Module
- Handles sign-in, sign-up, session management, and identity context
- Supports future integration with OAuth providers

### 4.2 Syllabus Intake Module
- Receives raw syllabus text
- Validates input quality and length
- Passes content to parsing services

### 4.3 Parsing Engine
- Converts free text into a structured topic tree
- Maintains topic ordering, depth, and dependencies where possible
- Supports ambiguity handling and fallback behavior

### 4.4 Planning Engine
- Converts the parsed syllabus into a study plan
- Weights topics by importance and complexity
- Allocates daily sessions across a time horizon

### 4.5 Replanning Engine
- Evaluates whether current progress deviates from the intended schedule
- Rebalances workload and adjusts upcoming study targets
- Produces a revised plan while preserving previously completed work

### 4.6 Progress & Review Module
- Stores daily check-in data
- Determines whether a review prompt is necessary
- Supports later retention quiz logic

## 5. Suggested Folder Structure
```text
syllabot/
  app/
    frontend/
      components/
      pages/ or app/
      lib/
      styles/
    backend/
      api/
        v1/
      core/
      services/
      agents/
      parsers/
      planners/
      models/
      schemas/
      tests/
      utils/
  infra/
    docker/
    postgres/
    env/
  docs/
    PRD.md
    Architecture.md
    Phases.md
    Design.md
    Rules.md
    Memory.md
```

## 6. Recommended Tech Stack
### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS
- React Query / TanStack Query for API state management

### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy or Django ORM
- Alembic for migrations
- Uvicorn for serving

### Data / Infra
- PostgreSQL
- Redis (optional for caching and background jobs)
- Docker for local development
- GitHub Actions or similar CI/CD pipeline

## 7. Parsing Engine Specification
The parsing engine must be robust enough to handle deeply nested syllabus hierarchies and messy formatting. The initial implementation should prioritize deterministic behavior over cleverness.

### 7.1 Parsing Requirements
- Preserve the original wording of topics wherever possible
- Support nested section/subsection/sub-subsection structures
- Detect list-like and paragraph-based formatting
- Handle inconsistent punctuation and indentation
- Avoid inventing missing topics

### 7.2 Proposed Algorithm
Use a custom stack-based shift-reduce parser with an operator precedence dictionary.

### 7.3 Why This Approach
A shift-reduce parser is appropriate because syllabus text naturally contains hierarchical structure with explicit and implicit delimiters. The parser can:
- push tokens onto a stack
- reduce completed grammar fragments into structured nodes
- resolve nesting based on precedence rules
- build a tree representing the syllabus hierarchy

### 7.4 Parser Design Details
- Tokenization layer:
  - split raw text into lexical tokens such as headings, bullets, numbering, punctuation, and free-text content
- Grammar layer:
  - define grammar rules for sections, topics, subtopics, and list items
- Operator precedence dictionary:
  - assign precedence values to delimiters such as `:`, `-`, `.` and section markers
  - use precedence to resolve ambiguous nesting and ordering
- Reduce actions:
  - combine tokens into structured nodes when a production rule is satisfied
- Fallback behavior:
  - if a structure is unclear, preserve the content as a low-confidence node and require human review or later refinement

### 7.5 Data Output Model
The parser should emit a structured object with at least:
- `id`
- `title`
- `parent_id`
- `level`
- `raw_text`
- `confidence`
- `children`
- `importance_hint`

## 8. Data Model Highlights
### Users
- id
- email
- name
- created_at

### Syllabi
- id
- user_id
- raw_text
- parsed_tree_json
- created_at

### Study Plans
- id
- syllabus_id
- start_date
- end_date
- plan_json
- status

### Daily Progress
- id
- plan_id
- date
- completed_hours
- completed_topics
- check_in_note

## 9. Non-Functional Considerations
- The parser must be deterministic and auditable
- AI usage should be optional and guarded by fallback logic
- Error states should be visible in the UI without breaking the app
- The system should be modular enough to evolve from static planning to more autonomous agents
- The application architecture and dependencies must support free-tier hosting limits and simple resource deployment (e.g. SQLite database file storage capability, minimal memory usage, zero mandatory SaaS pricing plans)

---

## Document Status
- Status: Draft
- Owner: Engineering
- Last Updated: 2026-07-17
