import { SearchResponse } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchProducts(
  query: string,
  limit: number = 10
): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query, limit: limit.toString() });
  const res = await fetch(`${API_BASE}/api/search?${params}`, {
    signal: AbortSignal.timeout(30000),
  });

  if (!res.ok) {
    throw new Error(`Search failed: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export async function getSuggestions(query: string): Promise<string[]> {
  const params = new URLSearchParams({ q: query });
  const res = await fetch(`${API_BASE}/api/suggestions?${params}`, {
    signal: AbortSignal.timeout(5000),
  });
  if (!res.ok) return [];
  const data = await res.json();
  return data.suggestions ?? [];
}

export async function getPlatforms() {
  const res = await fetch(`${API_BASE}/api/platforms`);
  if (!res.ok) throw new Error("Failed to fetch platforms");
  return res.json();
}
