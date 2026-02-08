"use client";

import { AlertTriangle, RefreshCw, SearchX } from "lucide-react";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  message = "Something went wrong. Please try again.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <AlertTriangle className="w-12 h-12 text-red-400 mb-4" />
      <h3 className="text-lg font-semibold text-gray-800 mb-2">Oops!</h3>
      <p className="text-gray-500 mb-6 max-w-md">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 rounded-lg bg-pink-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-pink-600 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Try Again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ query }: { query: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <SearchX className="w-12 h-12 text-gray-300 mb-4" />
      <h3 className="text-lg font-semibold text-gray-800 mb-2">
        No products found
      </h3>
      <p className="text-gray-500 mb-4 max-w-md">
        We couldn&apos;t find any results for &quot;{query}&quot;. Try a different search
        term.
      </p>
      <div className="flex flex-wrap gap-2 justify-center">
        {["Maybelline Foundation", "MAC Lipstick", "Lakme Kajal", "Neutrogena Sunscreen"].map(
          (suggestion) => (
            <a
              key={suggestion}
              href={`/search?q=${encodeURIComponent(suggestion)}`}
              className="rounded-full border border-gray-200 bg-white px-4 py-1.5 text-sm text-gray-600 hover:border-pink-300 hover:text-pink-600 transition-colors"
            >
              {suggestion}
            </a>
          )
        )}
      </div>
    </div>
  );
}
