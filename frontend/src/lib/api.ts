const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");

export interface UserResponse {
  id: number;
  email: string;
  name: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface SyllabusResponse {
  id: number;
  user_id: number;
  raw_text: string;
  parsed_tree_json: ParsedTreeNode[];
  created_at: string;
}

export interface ParsedTreeNode {
  id: string;
  title: string;
  parent_id: string | null;
  level: number;
  confidence: number;
  importance_hint: number;
  children: ParsedTreeNode[];
}

export interface StudyPlanTopic {
  id: string;
  title: string;
  full_path: string;
  importance_hint: number;
  complexity: number;
}

export interface StudyPlanDay {
  day_number: number;
  date: string;
  topics: StudyPlanTopic[];
  is_review: boolean;
  notes: string;
}

export interface StudyPlanResponse {
  id: number;
  syllabus_id: number;
  start_date: string;
  end_date: string;
  status: string;
  plan_json: StudyPlanDay[];
  created_at: string;
}

export interface DailyProgressCreate {
  date: string;
  completed_hours: number;
  completed_topics: string[];
  check_in_note?: string;
}

export interface DailyProgressResponse {
  id: number;
  plan_id: number;
  date: string;
  completed_hours: number;
  completed_topics: string[];
  check_in_note: string | null;
}

// Helpers
function getAuthHeader(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("syllabot_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = {
    "Content-Type": "application/json",
    ...getAuthHeader(),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = "An error occurred";
    try {
      const errData = await response.json();
      errorMessage = errData.detail || errData.message || errorMessage;
    } catch {
      errorMessage = response.statusText;
    }
    throw new Error(errorMessage);
  }

  return response.json() as Promise<T>;
}

// API functions
export const authApi = {
  async signup(data: any): Promise<UserResponse> {
    return apiRequest<UserResponse>("/api/v1/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async login(data: FormData): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: "POST",
      body: data, // Form data contains username and password
    });

    if (!response.ok) {
      let errorMessage = "Login failed";
      try {
        const errData = await response.json();
        errorMessage = errData.detail || errorMessage;
      } catch {}
      throw new Error(errorMessage);
    }

    const resData = await response.json();
    if (typeof window !== "undefined" && resData.access_token) {
      localStorage.setItem("syllabot_token", resData.access_token);
    }
    return resData;
  },

  async getMe(): Promise<UserResponse> {
    return apiRequest<UserResponse>("/api/v1/auth/me");
  },

  logout() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("syllabot_token");
    }
  },

  isLoggedIn(): boolean {
    if (typeof window === "undefined") return false;
    return !!localStorage.getItem("syllabot_token");
  },
};

export const syllabiApi = {
  async ingest(rawText: string): Promise<SyllabusResponse> {
    return apiRequest<SyllabusResponse>("/api/v1/syllabi/", {
      method: "POST",
      body: JSON.stringify({ raw_text: rawText }),
    });
  },
};

export const plansApi = {
  async create(data: {
    syllabus_id: number;
    start_date: string;
    end_date: string;
  }): Promise<StudyPlanResponse> {
    return apiRequest<StudyPlanResponse>("/api/v1/plans/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getAll(): Promise<StudyPlanResponse[]> {
    return apiRequest<StudyPlanResponse[]>("/api/v1/plans/");
  },

  async getOne(planId: number): Promise<StudyPlanResponse> {
    return apiRequest<StudyPlanResponse>(`/api/v1/plans/${planId}`);
  },

  async replan(planId: number, fromDate?: string): Promise<StudyPlanResponse> {
    const query = fromDate ? `?from_date=${fromDate}` : "";
    return apiRequest<StudyPlanResponse>(`/api/v1/plans/${planId}/replan${query}`, {
      method: "POST",
    });
  },
};

export const progressApi = {
  async log(planId: number, data: DailyProgressCreate): Promise<DailyProgressResponse> {
    return apiRequest<DailyProgressResponse>(`/api/v1/progress/${planId}`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getHistory(planId: number): Promise<DailyProgressResponse[]> {
    return apiRequest<DailyProgressResponse[]>(`/api/v1/progress/${planId}`);
  },
};

// ─────────────────────────────────────────────────────────────────
// AI Chat API
// ─────────────────────────────────────────────────────────────────

export interface AIChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface AIChatResponse {
  response: string;
  actions: Array<{
    tool: string;
    arguments: Record<string, unknown>;
    output: unknown;
  }>;
  sources: string[];
}

export interface AIProviderStatus {
  gemini: { available: boolean; default_model: string };
  groq: { available: boolean; default_model: string };
  any_available: boolean;
}

export const aiApi = {
  /**
   * Send a message to the Syllabot AI agent.
   * The agent routes the request through LangGraph to the appropriate node.
   *
   * @param message        - The user's natural language message.
   * @param conversationId - Session identifier for conversation memory.
   * @returns AIChatResponse with response text, tool actions, and sources.
   */
  async chat(message: string, conversationId: string): Promise<AIChatResponse> {
    return apiRequest<AIChatResponse>("/api/v1/ai/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });
  },

  /**
   * Check which AI providers are currently configured and available.
   */
  async getStatus(): Promise<AIProviderStatus> {
    return apiRequest<AIProviderStatus>("/api/v1/ai/status");
  },
};
