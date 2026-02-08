export type Platform = "nykaa" | "amazon" | "tira";

export interface ProductResult {
  name: string;
  brand: string;
  price: number;
  mrp: number;
  discount_percent: number;
  image_url: string;
  product_url: string;
  platform: Platform;
  in_stock: boolean;
  rating: number;
  rating_count: number;
  variant: string;
}

export interface MatchedProduct {
  product_name: string;
  brand: string;
  variant: string;
  image_url: string;
  prices: ProductResult[];
  best_price: number;
  best_platform: string;
  savings: number;
}

export interface SearchResponse {
  query: string;
  results: MatchedProduct[];
  total_results: number;
  platforms_searched: string[];
  platforms_failed: string[];
  cached: boolean;
  search_time_ms: number;
  timestamp: string;
}

export interface PlatformInfo {
  id: Platform;
  name: string;
  color: string;
  url: string;
}

export const PLATFORM_CONFIG: Record<Platform, PlatformInfo> = {
  nykaa: { id: "nykaa", name: "Nykaa", color: "#FC2779", url: "https://www.nykaa.com" },
  amazon: { id: "amazon", name: "Amazon", color: "#FF9900", url: "https://www.amazon.in" },
  tira: { id: "tira", name: "Tira", color: "#1a1a2e", url: "https://www.tirabeauty.com" },
};
