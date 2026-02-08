"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Search, Loader2, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { getSuggestions } from "@/lib/api";

const PLACEHOLDERS = [
  "Maybelline Fit Me Foundation...",
  "MAC Ruby Woo Lipstick...",
  "Lakme Kajal...",
  "Neutrogena Sunscreen SPF 50...",
  "The Ordinary Niacinamide...",
  "Minimalist Salicylic Acid...",
];

interface SearchBarProps {
  initialQuery?: string;
  isLoading?: boolean;
  size?: "lg" | "md";
}

export default function SearchBar({
  initialQuery = "",
  isLoading = false,
  size = "lg",
}: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [isTrending, setIsTrending] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const blurTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const router = useRouter();

  // Rotate placeholders
  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((i) => (i + 1) % PLACEHOLDERS.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Ctrl+K shortcut
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Fetch suggestions with debounce
  const fetchSuggestions = useCallback((value: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    const trimmed = value.trim();
    if (trimmed.length < 1) {
      // Fetch trending when empty
      getSuggestions("").then((items) => {
        setSuggestions(items);
        setIsTrending(true);
        setShowDropdown(items.length > 0);
        setActiveIndex(-1);
      }).catch(() => {});
      return;
    }

    debounceRef.current = setTimeout(() => {
      getSuggestions(trimmed).then((items) => {
        setSuggestions(items);
        setIsTrending(false);
        setShowDropdown(items.length > 0);
        setActiveIndex(-1);
      }).catch(() => {
        setSuggestions([]);
        setShowDropdown(false);
      });
    }, 300);
  }, []);

  // Cleanup debounce on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      if (blurTimeoutRef.current) clearTimeout(blurTimeoutRef.current);
    };
  }, []);

  const navigateToSearch = (searchQuery: string) => {
    const trimmed = searchQuery.trim();
    if (trimmed.length >= 2) {
      setShowDropdown(false);
      setQuery(trimmed);
      router.push(`/search?q=${encodeURIComponent(trimmed)}`);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeIndex >= 0 && activeIndex < suggestions.length) {
      navigateToSearch(suggestions[activeIndex]);
    } else {
      navigateToSearch(query);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    fetchSuggestions(value);
  };

  const handleFocus = () => {
    if (blurTimeoutRef.current) clearTimeout(blurTimeoutRef.current);
    fetchSuggestions(query);
  };

  const handleBlur = () => {
    // Delay hide so clicks on suggestions register
    blurTimeoutRef.current = setTimeout(() => {
      setShowDropdown(false);
    }, 200);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showDropdown || suggestions.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((prev) =>
        prev < suggestions.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) =>
        prev > 0 ? prev - 1 : suggestions.length - 1
      );
    } else if (e.key === "Escape") {
      setShowDropdown(false);
      setActiveIndex(-1);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    navigateToSearch(suggestion);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto relative">
      <div
        className={cn(
          "relative flex items-center rounded-2xl border-2 border-gray-200 bg-white shadow-lg transition-all focus-within:border-pink-400 focus-within:shadow-pink-100",
          size === "lg" ? "px-5 py-4" : "px-4 py-3",
          showDropdown && suggestions.length > 0 && "rounded-b-none border-b-0"
        )}
      >
        {isLoading ? (
          <Loader2 className="w-5 h-5 text-pink-500 animate-spin shrink-0" />
        ) : (
          <Search className="w-5 h-5 text-gray-400 shrink-0" />
        )}
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={PLACEHOLDERS[placeholderIndex]}
          autoComplete="off"
          className={cn(
            "flex-1 ml-3 bg-transparent outline-none text-gray-800 placeholder-gray-400",
            size === "lg" ? "text-lg" : "text-base"
          )}
        />
        <kbd className="hidden sm:inline-flex items-center gap-1 rounded border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs text-gray-400">
          Ctrl K
        </kbd>
      </div>

      {/* Suggestions dropdown */}
      {showDropdown && suggestions.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full bg-white border-2 border-t-0 border-pink-400 rounded-b-2xl shadow-lg overflow-hidden"
        >
          {isTrending && (
            <div className="flex items-center gap-2 px-5 pt-3 pb-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
              <TrendingUp className="w-3.5 h-3.5" />
              Trending searches
            </div>
          )}
          <ul className="py-1">
            {suggestions.map((suggestion, index) => (
              <li key={suggestion}>
                <button
                  type="button"
                  onMouseDown={(e) => {
                    e.preventDefault(); // Prevent blur
                    handleSuggestionClick(suggestion);
                  }}
                  onMouseEnter={() => setActiveIndex(index)}
                  className={cn(
                    "w-full flex items-center gap-3 px-5 py-2.5 text-left transition-colors cursor-pointer",
                    size === "lg" ? "text-base" : "text-sm",
                    index === activeIndex
                      ? "bg-pink-50 text-pink-700"
                      : "text-gray-700 hover:bg-gray-50"
                  )}
                >
                  <Search className="w-4 h-4 text-gray-300 shrink-0" />
                  <span>{suggestion}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </form>
  );
}
