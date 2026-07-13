const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    cache: "no-store",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(
      typeof err.detail === "string"
        ? err.detail
        : err.detail?.message || "Request failed"
    );
  }

  return res.json();
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  getPapers: () => request<Paper[]>("/api/papers"),

  deletePaper: (id: number) =>
    request<{ message: string }>(`/api/papers/${id}`, { method: "DELETE" }),

  getOverview: () => request<AnalyticsOverview>("/api/analytics/overview"),

  getAgentInsights: () => request<AgentInsights>("/api/analytics/agent-insights"),

  getAgentSuggestions: () =>
    request<{ suggestions: AgentSuggestion[] }>("/api/analytics/agent-suggestions"),

  uploadPaper: (formData: FormData) =>
    fetch(`${API_BASE}/api/papers/upload`, {
      method: "POST",
      body: formData,
    }).then(async (res) => {
      const data = await res.json();
      if (!res.ok) throw { status: res.status, data };
      return data as Paper & { plagiarism_report: PlagiarismReport };
    }),

  checkPlagiarism: (formData: FormData) =>
    fetch(`${API_BASE}/api/papers/check-plagiarism`, {
      method: "POST",
      body: formData,
    }).then(async (res) => {
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Check failed");
      return data as PlagiarismReport;
    }),
};

export interface Paper {
  id: number;
  title: string;
  author: string | null;
  department: string | null;
  publication_year: number | null;
  filename: string;
  file_type: string;
  primary_field: string | null;
  secondary_fields: string[];
  keywords: string[];
  word_count: number | null;
  created_at: string | null;
}

export interface PlagiarismMatch {
  paper_id: number;
  title: string;
  author: string | null;
  similarity_percent: number;
  is_duplicate: boolean;
  matching_passages?: { similarity_percent: number; source_excerpt: string }[];
}

export interface PlagiarismReport {
  status: string;
  highest_similarity: number;
  matches: PlagiarismMatch[];
  total_matches: number;
}

export interface AnalyticsOverview {
  total_papers: number;
  field_distribution: { field: string; count: number }[];
  top_researched_fields: { field: string; count: number }[];
  underexplored_fields: { field: string; count: number; scope_note: string }[];
  opportunity_fields: {
    field: string;
    signal_strength: string;
    reason: string;
    suggested_action: string;
  }[];
  trending_keywords: { keyword: string; count: number }[];
  department_activity: { department: string; count: number }[];
  papers_by_year: { year: number; count: number }[];
  summary: {
    total_papers: number;
    unique_fields: number;
    departments_represented: number;
  };
}

export interface AgentInsights {
  agent_used: string;
  agent_label: string;
  executive_summary: string;
  active_research_areas: {
    field: string;
    paper_count: number;
    summary: string;
    key_themes: string[];
    sample_papers?: string[];
  }[];
  underexplored_areas: {
    field: string;
    paper_count: number;
    gap_analysis: string;
    research_scope: string;
  }[];
  emerging_opportunities: {
    field: string;
    rationale: string;
    suggested_projects: string[];
  }[];
  strategic_recommendations: string[];
  integration_suggestions: AgentSuggestion[];
}

export interface AgentSuggestion {
  name: string;
  type: string;
  env_var: string | null;
  best_for: string;
  setup: string;
}
