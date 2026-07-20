# AI Architecture Debug: Request Lifecycle and Failure Analysis

This document details the trace of the AI request lifecycle in Syllabot, explains the serialization format mapping, and diagnoses the root causes of formatting errors and transient provider failures.

---

## 1. Trace of the request lifecycle

```
[Frontend Dashboard]
       │  (POST /api/v1/ai/chat)
       ▼
[FastAPI Route Router] (router.py)
       │  (Calls SyllabotAgent.execute)
       ▼
[SyllabotAgent] (agent.py)
       │  (Loads memory and bootstraps context)
       ▼
[LangGraph Workflow] (workflow.py)
       │  (Invokes nodes.py)
       ▼
[chat_node / parse_node / quiz_node] (nodes.py)
       │  (Calls LLMService / ModelRouter)
       ▼
[ModelRouter] (router.py)
       │  (Resolves best healthy provider)
       ▼
[GeminiProvider / GroqProvider] (gemini.py / groq.py)
       │  (Translates prompts/tools and invokes SDK)
       ▼
[AI Model Provider API] (Google Gemini / Groq Cloud)
```

---

## 2. Analysis of failure points

### 2.1 Gemini `GenerateContentRequest.contents.parts.data` Missing (Problem 3)
- **Where it occurs**: In `GeminiProvider._convert_messages` and raw `_call_gemini` inside `services.py`.
- **Why it occurs**: 
  - Standard chat histories contain messages representing tool execution results (`role: "tool"` or helper states). 
  - The legacy converter only checks for `user` and `assistant` roles, dropping the `tool` message completely or leaving its `content` as empty/null.
  - When Gemini's endpoint receives a message part without a valid data type (like a text part where content is null, or a function response without the correct schema fields), it fails payload validation and rejects it with `GenerateContentRequest.contents[1].parts[0].data: required oneof field 'data' must have one initialized field`.

### 2.2 Groq `role: tool`, `tool_call_id` Missing (Problem 2)
- **Where it occurs**: In `LLMService._call_groq` and `GroqProvider._convert_messages`.
- **Why it occurs**:
  - The Groq API adheres strictly to the OpenAI Tool-Calling spec. 
  - Under this spec, every message with `role: "tool"` must have a corresponding `tool_call_id` that references the `id` of the tool call requested in the preceding assistant message.
  - The serialization loop only mapped `{"role": msg["role"], "content": msg["content"]}` and completely dropped the `tool_call_id` parameter, causing Groq's gateway validation to fail before reaching the model.

### 2.3 Transient Key & Quota Limits (Problem 1)
- **Where it occurs**: In `ModelRouter.get_provider_for_task` and provider invocation points.
- **Why it occurs**: 
  - Gemini's free tier has strict quotas (limit 0 on some models, or low requests-per-minute). When these are reached, Gemini returns HTTP 429 or 503.
  - The current router only checks for the existence of keys (`is_available`), but doesn't track provider health at runtime. If a provider is rate-limited, the system repeatedly routes subsequent calls to it, resulting in cascading failures.
