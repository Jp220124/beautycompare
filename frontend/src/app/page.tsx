import SearchBar from "@/components/SearchBar";
import { PLATFORM_CONFIG } from "@/types";

const TRENDING = [
  "Maybelline Fit Me Foundation",
  "MAC Ruby Woo",
  "Lakme Kajal",
  "Neutrogena Sunscreen",
  "The Ordinary Niacinamide",
  "Minimalist Salicylic Acid",
];

export default function Home() {
  const platforms = Object.values(PLATFORM_CONFIG);

  return (
    <main className="flex flex-col items-center justify-center min-h-screen px-4 py-16">
      {/* Hero */}
      <div className="text-center mb-10 animate-fade-in">
        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight text-gray-900 mb-4">
          Beauty<span className="text-pink-500">Compare</span>
        </h1>
        <p className="text-lg text-gray-500 max-w-lg mx-auto">
          Compare beauty product prices across Nykaa, Tira & Amazon India.
          Find the best deal instantly.
        </p>
      </div>

      {/* Search */}
      <div className="w-full max-w-2xl mb-10 animate-fade-in">
        <SearchBar size="lg" />
      </div>

      {/* Platform Badges */}
      <div className="flex items-center gap-3 mb-10 animate-fade-in">
        <span className="text-sm text-gray-400">Comparing across</span>
        {platforms.map((p) => (
          <span
            key={p.id}
            className="rounded-full px-3 py-1 text-xs font-bold text-white"
            style={{ backgroundColor: p.color }}
          >
            {p.name}
          </span>
        ))}
      </div>

      {/* Trending Searches */}
      <div className="text-center animate-fade-in">
        <p className="text-sm text-gray-400 mb-3">Popular searches</p>
        <div className="flex flex-wrap justify-center gap-2">
          {TRENDING.map((term) => (
            <a
              key={term}
              href={`/search?q=${encodeURIComponent(term)}`}
              className="rounded-full border border-gray-200 bg-white px-4 py-1.5 text-sm text-gray-600 hover:border-pink-300 hover:text-pink-600 transition-colors shadow-sm"
            >
              {term}
            </a>
          ))}
        </div>
      </div>
    </main>
  );
}
