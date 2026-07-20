# Syllabot

Syllabot is an adaptive study planner designed to act as the “Google Maps for your syllabus.” It helps students turn free-text syllabus content into structured study plans, track daily progress, and automatically replan when they fall behind.

## What Syllabot Does
- Parses syllabus input into a structured topic hierarchy
- Generates realistic daily study plans weighted by importance
- Supports adaptive replanning when progress slips
- Encourages retention through review and check-in workflows
- Builds toward future AI-agent-based planning and coaching features

## Project Documentation
The project documentation is organized as follows:
- [PRD.md](PRD.md) – product requirements and scope
- [Architecture.md](Architecture.md) – system architecture and technical design
- [Phases.md](Phases.md) – development roadmap
- [Design.md](Design.md) – visual and UX guidance
- [Rules.md](Rules.md) – AI and engineering guardrails
- [Memory.md](Memory.md) – project context and state tracker
- [docs/AI_INFRASTRUCTURE.md](docs/AI_INFRASTRUCTURE.md) – refactored AI module, fallback, and serialization architecture
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) – production deployment guide for Supabase, Render, and Vercel

## Vision
Syllabot aims to reduce the stress of exam preparation by making study planning adaptive, intelligent, and calm rather than rigid and discouraging.

## Status
Current status: backend planning engine, parser, database models, and API endpoints are fully completed, tested, and ready.

## Next Steps
- Scaffolding and integration of the frontend application (which will reside under the `/frontend` directory).
- Build Phase 4 premium reinforcement quizzes and institutional dashboard reporting.
