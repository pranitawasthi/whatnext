import type { Content, Interaction, InteractionStatus, Paginated, SearchResponse, User } from "../types/api";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type TokenResponse = {
  access_token: string;
  user: User;
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("whatnext_token");
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail ?? "Request failed");
  }
  return response.json();
}

export const api = {
  signup: (email: string, username: string, password: string) =>
    request<TokenResponse>("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, username, password }),
    }),
  login: (email: string, password: string) =>
    request<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<User>("/api/auth/me"),
  listContent: (contentType?: string) =>
    request<Paginated<Content>>(`/api/content?page=1&page_size=40${contentType ? `&content_type=${contentType}` : ""}`),
  search: (query: string, contentType?: string, includeInternet = true) =>
    request<SearchResponse>("/api/search", {
      method: "POST",
      body: JSON.stringify({ query, limit: 18, content_type: contentType || null, include_internet: includeInternet }),
    }),
  recommendations: (refresh = false, contentType?: string) =>
    request<Content[]>("/api/recommendations", {
      method: "POST",
      body: JSON.stringify({ limit: 18, refresh, content_type: contentType || null }),
    }),
  interactions: () => request<Interaction[]>("/api/interactions"),
  upsertInteraction: (content_id: string, rating: number | null, status: InteractionStatus) =>
    request<Interaction>("/api/interactions", {
      method: "PUT",
      body: JSON.stringify({ content_id, rating, status }),
    }),
};
