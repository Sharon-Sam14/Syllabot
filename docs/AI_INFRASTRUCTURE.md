# AI Infrastructure & Orchestration Refactor

This document explains the technical design and integration details of the refactored Agentic AI infrastructure in Syllabot.

---

## 1. Why the Refactoring was Required (Root Causes)

Before this refactoring, the AI orchestration layer faced multiple production issues under load:

1. **Payload Schema Failures (Gemini)**: 
   The legacy message converters only mapped `"user"` and `"assistant"` role contents, leaving `"tool"` roles unmapped or as null content. Gemini's API strictly rejects text parts containing null values, resulting in `GenerateContentRequest.contents[1].parts[0].data missing` failures.
   
2. **Correlation ID Mismatches (Groq)**: 
   Under the OpenAI/Groq tool-calling spec, a message with role `"tool"` MUST include a valid `tool_call_id` matching a tool call request in the preceding assistant message. The legacy payload serializations discarded this property, leading to API blocks.

3. **Lack of Resilient Failovers**: 
   When Gemini's free tier generated `429 (Rate Limit)` or `503 (Unavailable)` responses due to high demand, the service could not dynamically swap providers or put Gemini on a cooldown. This caused repeated client crashes.

---

## 2. Technical Architecture & Components

```
[Agent Graph Nodes]
        │  (Calls LLMService.generate_response)
        ▼
[LLMService]
        │  (Normalizes messages using ConversationNormalizer)
        ▼
[ModelRouter]
        │  (Resolves active, healthy provider checking _health_cache)
        ▼
[AIProvider Adapter] (GeminiProvider / GroqProvider)
        ├─ prepare_messages() (Serializes to provider-native schemas)
        ├─ execute()          (Calls ChatGoogleGenerativeAI / ChatGroq)
        ├─ parse_response()   (Builds unified ProviderResponse)
        └─ handle_errors()    (Maps exceptions to typed errors)
```

### 2.1 Unified Message Format
All message streams in Syllabot are parsed and normalized into a single typing contract defined in [base.py](file:///c:/Users/sharo/Desktop/Syllabot/backend/ai/providers/base.py):
```python
@dataclass
class Message:
    role: str                 # "system", "user", "assistant", "tool"
    content: Optional[str]
    tool_calls: Optional[List[ToolCall]]
    tool_call_id: Optional[str]
```

### 2.2 Serialization & Validation
The [serializer.py](file:///c:/Users/sharo/Desktop/Syllabot/backend/core/serializer.py) module houses the formatting logic:
* **`MessageSerializer`**: Converts raw JSON-like dicts to/from typed `Message` objects.
* **`ConversationNormalizer`**: Detects if tool responses are missing a `tool_call_id`, traces preceding assistant tool calls in history, and re-links them to guarantee API payload validation.

### 2.3 Provider Health Cache & Dynamic Routing
The [router.py](file:///c:/Users/sharo/Desktop/Syllabot/backend/ai/providers/router.py) module manages routing and transient failures:
* **Health Cache**: Maintains a thread-safe dictionary: `{"gemini": {"healthy": True, "cooldown_until": 0.0}}`.
* **Failover**: If a provider call fails with `RetryableError`, `RateLimitError`, or `QuotaExceededError`, `LLMService` registers a cooldown for that provider (60s) via `ModelRouter.mark_unhealthy()`.
* **Automatic Routing**: Subsequent calls automatically routing tasks to the healthy fallback provider (`Groq` or `Gemini`).
