# System Architecture: Syllabot v2

This document describes the end-to-end architecture, routing flows, and component interactions of the **Syllabot Agentic AI Study Planning Platform**.

---

## 1. High-Level Flow Diagram

The diagram below maps the interaction between the frontend dashboard, the FastAPI backend controllers, the LangGraph state machine workflow, and the AI model providers (Gemini & Groq).

```mermaid
graph TD
    A[Next.js Frontend Dashboard] -- HTTP Requests --> B[FastAPI API Gateways]
    B -- Bootstraps State --> C[LangGraph StateGraph Engine]
    C -- Conditional Intent Edge --> D{ModelRouter Task Map}
    D -- Preferred Task Node --> E[AI Task Node Executions]
    E -- AI Prompt Completion --> F[AI Provider Gateways]
    F -- API Payload --> G[Google Gemini API]
    F -- API Payload --> H[Groq Cloud API]
    E -- DB Operations --> I[SyllabotTools DB Access]
    I -- Read / Write --> J[(PostgreSQL / SQLite Database)]
```

---

## 2. Sequence Diagram: Intake & Study Plan Generation

The sequence diagram below details the end-to-end lifecycle when a user submits a syllabus and generates a personalized study plan.

```mermaid
sequenceDiagram
    autonumber
    actor Student as Student
    participant FE as Frontend Dashboard
    participant API as FastAPI Backend
    participant Graph as LangGraph workflow
    participant Router as ModelRouter
    participant AI as AI Provider (Gemini/Groq)
    participant DB as SQLAlchemy / DB

    Student->>FE: Ingest Syllabus File
    FE->>API: POST /api/v1/syllabi (raw_text)
    API->>DB: Save Syllabus JSON Structure
    DB-->>API: Syllabus ID
    API-->>FE: Return Syllabus Metadata
    
    Student->>FE: Click "Generate Study Plan"
    FE->>API: POST /api/v1/ai/chat ("Create a plan...")
    API->>Graph: Invoke Compiled StateGraph
    Graph->>Graph: node:route_intent (Intent detected: "plan")
    Graph->>Router: get_provider_for_task("generate_plan")
    Router-->>Graph: Returns GroqProvider (Speed & MCQs)
    Graph->>AI: generate(plan_generation_prompt)
    AI-->>Graph: AI Study Plan JSON structure
    Graph->>DB: SyllabotTools.generate_plan() (Save Plan & Days)
    DB-->>Graph: Plan Created
    Graph-->>API: Final Response (State Update)
    API-->>FE: AIChatResponse (Response + Actions + Sources)
    FE-->>Student: Update Treatment Dynamics UI (Visual Study Plan)
```

---

## 3. LangGraph Workflow Routing Topology

The AI Orchestrator uses a stateful directed acyclic graph built via LangGraph's `StateGraph`. 

```mermaid
graph LR
    START([START]) --> route_intent[Node: route_intent]
    
    route_intent --> route_edge{Edge: route_by_intent}
    
    route_edge -- "intent = parse" --> parse_node[Node: parse_node]
    route_edge -- "intent = plan" --> plan_node[Node: plan_node]
    route_edge -- "intent = progress" --> progress_node[Node: progress_node]
    route_edge -- "intent = replan" --> replan_node[Node: replan_node]
    route_edge -- "intent = quiz" --> quiz_node[Node: quiz_node]
    route_edge -- "intent = summarize" --> summarize_node[Node: summarize_node]
    route_edge -- "intent = chat" --> chat_node[Node: chat_node]
    
    parse_node --> END([END])
    plan_node --> END
    progress_node --> END
    replan_node --> END
    quiz_node --> END
    summarize_node --> END
    chat_node --> END
    
    %% Error Fallback Node
    error_node[Node: error_node] --> END
```

---

## 4. Component Details & Database Flows

### 4.1 Database Layer (SQLAlchemy / Alembic)
- **Database Connection pooling**: Leverages SQLAlchemy connection pools to allow high-throughput PostgreSQL queries in production, with fallback to file-based SQLite databases for local environments.
- **JSON Column mapping**: Uses native SQLAlchemy `JSON` types for syllabus parse trees and study schedules, guaranteeing seamless compatibility between SQLite's text-based JSON mapping and PostgreSQL's native `JSONB` binary formats.

### 4.2 Security & Rate Limiting Pipeline
- **Input Sanitizer**: Filters prompt payloads for keywords related to character overrides or command bypasses, mapping raw inputs to safe, sanitized content.
- **SlowAPI Gatekeepers**: Applies global client limits and stricter sub-limits on agent endpoints (such as `POST /api/v1/ai/chat`) to protect AI resources from malicious spamming.
