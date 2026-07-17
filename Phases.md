# Development Phases

## Phase 1: Foundation & Auth
### Objective
Build the base product shell, user accounts, and the core application skeleton.

### Deliverables
- Project scaffolding for Next.js frontend and Python backend
- Authentication flow for sign-up, login, and session handling
- Basic dashboard and onboarding screens
- Database schema for users, syllabi, plans, and progress
- API foundation for future planning services

### Success Criteria
- A user can create an account and access a personalized workspace
- The app stores and retrieves basic user state reliably
- The architecture is ready for parsing and plan generation features

## Phase 2: Parsing Engine & Initial Static Plans
### Objective
Turn raw syllabus text into structured topics and generate an initial study plan.

### Deliverables
- Syllabus ingestion endpoint
- Hierarchical parsing engine for nested content
- Topic tree representation with confidence scoring
- Static study plan generator based on importance and time horizon
- Initial UI for viewing the generated study plan

### Success Criteria
- The system can parse a realistic syllabus into a nested topic structure
- The generated plan is understandable and useful to a student
- The output respects the user’s original syllabus content without invented topics

## Phase 3: The Adaptive Replanning Loop
### Objective
Make the planner dynamic and useful in real student behavior.

### Deliverables
- Daily check-in workflow
- Progress tracking and missed-session detection
- Replanning engine that recalculates remaining workload
- Visual indicators for plan changes and urgency
- Review prompts for retention and catch-up support

### Success Criteria
- When a student falls behind, the system produces a revised plan automatically
- The plan remains realistic and motivating rather than punitive
- Students can understand why the plan changed

## Phase 4: Premium Features
### Objective
Expand into monetizable and institutional value.

### Deliverables
- Retention quizzes and spaced review prompts
- Premium dashboard for tracking study consistency and recall strength
- B2B features for coaching institutes and schools
- Admin-style reporting and institutional planning views

### Success Criteria
- The platform supports value-added features beyond basic planning
- Premium users receive clear, measurable learning benefits
- Institutional users can monitor cohorts or class-level study progress

## Implementation Principles Across All Phases
- Build in small increments and validate each layer before moving further
- Keep the architecture modular so later features fit naturally
- Avoid implementing premium features before the core planning loop is reliable

---

## Document Status
- Status: Draft
- Owner: Product and Engineering
- Last Updated: 2026-07-17