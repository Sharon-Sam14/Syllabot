# Project Requirements Document (PRD)

## Project Name
Syllabot

## 1. Overview
Syllabot is an adaptive study planner designed to function as the “Google Maps for your syllabus.” It converts free-text syllabus inputs into structured learning plans, weighs topics by importance, and continuously recalculates the study path when a student falls behind. The system is built to support both self-directed learners and AI-assisted academic planning workflows.

## 2. Problem Statement
Static study schedules frequently fail in real life. Students often create ambitious plans at the start of a term, only to fall behind after a missed day, a busy week, or a difficult topic. In those moments, the plan becomes outdated and discouraging. Traditional planners do not autonomously re-route the learner; they require manual reset and often trigger abandonment.

This problem is especially severe for:
- College students preparing for semester finals
- Students preparing for internal sessional exams (ISE)
- Students preparing for vivas and oral assessments

## 3. Core Vision
Syllabot will provide an adaptive planning experience that:
- Parses unstructured syllabus content into a hierarchical topic model
- Generates realistic daily study plans with topic weighting
- Detects when a student is off-track
- Replans automatically using updated progress signals
- Encourages retention through lightweight review checks and daily check-ins

## 4. Target Audience
### Primary Users
- College students managing large syllabi across multiple subjects
- Students preparing for high-stakes examinations
- Learners who need structure without rigid, brittle scheduling

### Specific Use Cases
- Semester finals: Students need steady progress across many units and chapters
- Internal sessional exams (ISE): Students need short, high-priority planning loops
- Vivas: Students need revision depth, recall practice, and spaced review

## 5. Goals
### Business and Product Goals
- Reduce planning friction for students with overloaded academic schedules
- Improve adherence to study plans through adaptive guidance
- Increase confidence by replacing static plans with responsive scheduling
- Create a foundation for future premium capabilities such as retention quizzes, tutoring integrations, and institutional dashboards

### Functional Goals
- Accept syllabus text from a student or institution
- Create a structured representation of topics and subtopics
- Produce an initial daily plan grounded in topic importance and time available
- Recalculate plans when progress falls behind
- Support daily check-ins and learning retention review prompts

## 6. Core Features
### 6.1 Syllabus Parsing
- Accept free-text syllabus input
- Extract topics, subtopics, and nested hierarchy information
- Preserve the user’s original topic names and structure wherever possible
- Flag ambiguous or incomplete sections for review

### 6.2 Plan Generation
- Estimate topic complexity and importance
- Build a realistic daily study plan over a chosen time horizon
- Balance workload across days to avoid overload
- Weight topics according to user-defined or inferred importance

### 6.3 Adaptive Replanning
- Monitor if the student falls behind or misses planned sessions
- Recalculate the remaining study plan dynamically
- Rebalance upcoming workload while maintaining realistic daily targets
- Adjust pacing without causing unnecessary panic or overloading

### 6.4 Daily Check-ins
- Prompt the user for study progress each day
- Capture simple progress data such as completed hours or completed topics
- Use this signal to adapt future scheduling decisions

### 6.5 Retention Checks
- Insert short review prompts or retention checks at appropriate intervals
- Support future spaced-repetition style reinforcement
- Improve long-term recall rather than only topic coverage

## 7. User Stories
- As a college student, I want Syllabot to turn my syllabus into a daily schedule so I can study consistently without feeling overwhelmed.
- As a student preparing for ISE, I want the system to adjust quickly when I miss a day so I do not fall irreparably behind.
- As a viva candidate, I want the planner to include review points that strengthen recall and oral readiness.
- As a user, I want the system to preserve my syllabus language and not invent new topics.

## 8. Functional Requirements
1. The application must accept syllabus text as input from the user.
2. The system must parse syllabus content into a structured hierarchy.
3. The system must generate an initial study plan based on topic importance and available time.
4. The system must allow daily progress updates from the user.
5. The system must recompute the remaining plan when progress is behind schedule.
6. The system must provide clear, understandable planning output in the UI.
7. The system must avoid hallucinating topics and must rely strictly on the user-provided syllabus text.
8. The system must degrade gracefully when AI services are unavailable or rate-limited.

## 9. Non-Functional Requirements
- Performance: initial plan generation should complete within a reasonable time for typical syllabus sizes
- Reliability: the app must continue to function with fallback logic when AI services fail
- Security: user data must be stored and handled with appropriate access control
- Maintainability: the system must be modular, testable, and easy to extend
- Accessibility: the interface should be readable, calm, and usable for stressed students

## 10. Success Metrics
- Increase in study-plan adherence compared to manual planning
- Rate of successful automatic replanning after missed sessions
- User satisfaction with clarity and helpfulness of the planner
- Reduction in planning abandonment during high-stress academic periods

## 11. Constraints and Assumptions
- The system must not invent topics not present in the user’s syllabus text
- The initial version will prioritize correctness and reliability over perfect AI autonomy
- The product will evolve in phases, beginning with foundational planning and progressing to adaptive intelligence

## 12. Open Questions
- Should the initial version infer importance from the syllabus structure or require explicit user input?
- How much automation should be available for daily check-ins in the first release?
- Which premium features should be prioritized after the core replanning loop is working?

---

## Document Status
- Status: Draft
- Owner: Product and Engineering
- Last Updated: 2026-07-17