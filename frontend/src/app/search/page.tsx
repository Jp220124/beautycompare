"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState, useCallback, Suspense } from "react";
import { LayoutGrid, Table, Clock, Zap } from "lucide-react";

import SearchBar from "@/components/SearchBar";
import PriceCard from "@/components/PriceCard";
import ComparisonTable from "@/components/ComparisonTable";
import SkeletonCard, { SkeletonTable } from "@/components/SkeletonCard";
import { ErrorState, EmptyState } from "@/components/ErrorState";
import { searchProducts } from "@/lib/api";
import { SearchResponse } from "@/types";
import { cn, formatPrice } from "@/lib/utils";

function SearchContent() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") || "";

  const [data, setData] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<"cards" | "table">("cards");

  const fetchResults = useCallback(async () => {
    if (!query || query.length < 2) return;
    setLoading(true);
    setError(null);
    try {
      const result = await searchProducts(query);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    fetchResults();
  }, [fetchResults]);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-gray-100 py-4 px-4">
        <div className="max-w-6xl mx-auto flex items-center gap-4">
          <a
            href="/"
            className="text-xl font-extrabold text-gray-900 shrink-0"
          >
            Beauty<span className="text-pink-500">Compare</span>
          </a>
          <SearchBar initialQuery={query} isLoading={loading} size="md" />
        </div>
      </header>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-4 py-6">
        {/* Results Meta Bar */}
        {data && !loading && (
          <div className="flex items-center justify-between mb-6 animate-fade-in">
            <div className="flex items-center gap-4 text-sm text-gray-500 flex-wrap">
              <span>
                <strong className="text-gray-800">{data.total_results}</strong>{" "}
                results for &quot;{data.query}&quot;
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                {data.search_time_ms}ms
              </span>
              {data.cached && (
                <span className="flex items-center gap-1 text-green-600">
                  <Zap className="w-3.5 h-3.5" />
                  cached
                </span>
              )}
              {data.platforms_failed.length > 0 && (
                <span className="text-amber-600">
                  ({data.platforms_failed.join(", ")} unavailable)
                </span>
              )}
            </div>

            {/* View Toggle */}
            <div className="flex items-center gap-1 rounded-lg border border-gray-200 bg-white p-1 shrink-0">
              <button
                onClick={() => setView("cards")}
                className={cn(
                  "rounded-md p-1.5 transition-colors",
                  view === "cards"
                    ? "bg-pink-50 text-pink-600"
                    : "text-gray-400 hover:text-gray-600"
                )}
              >
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setView("table")}
                className={cn(
                  "rounded-md p-1.5 transition-colors",
                  view === "table"
                    ? "bg-pink-50 text-pink-600"
                    : "text-gray-400 hover:text-gray-600"
                )}
              >
                <Table className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="animate-fade-in">
            {view === "cards" ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            ) : (
              <SkeletonTable />
            )}
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <ErrorState message={error} onRetry={fetchResults} />
        )}

        {/* Empty State */}
        {data && data.total_results === 0 && !loading && !error && (
          <EmptyState query={query} />
        )}

        {/* Results - Card View */}
        {data && data.total_results > 0 && !loading && view === "cards" && (
          <div className="space-y-8 animate-fade-in">
            {data.results.map((matched, idx) => (
              <div key={idx} className="space-y-3">
                {/* Product Group Header */}
                <div className="flex items-center gap-3">
                  {matched.image_url && (
                    <img
                      src={matched.image_url}
                      alt=""
                      className="w-10 h-10 object-contain rounded"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = "none";
                      }}
                    />
                  )}
                  <div>
                    <h2 className="text-base font-semibold text-gray-800">
                      {matched.product_name}
                    </h2>
                    {matched.brand && (
                      <p className="text-sm text-gray-500">{matched.brand}</p>
                    )}
                  </div>
                  {matched.savings > 0 && (
                    <span className="ml-auto rounded-full bg-green-50 px-3 py-1 text-sm font-semibold text-green-700">
                      Save up to {formatPrice(matched.savings)}
                    </span>
                  )}
                </div>

                {/* Price Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {matched.prices.map((price, pIdx) => (
                    <PriceCard
                      key={pIdx}
                      product={price}
                      isBestPrice={price.price === matched.best_price}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Results - Table View */}
        {data && data.total_results > 0 && !loading && view === "table" && (
          <div className="rounded-xl border border-gray-200 bg-white p-4 animate-fade-in">
            <ComparisonTable results={data.results} />
          </div>
        )}
      </main>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <div className="p-8 text-center text-gray-400">Loading...</div>
      }
    >
      <SearchContent />
    </Suspense>
  );
}
