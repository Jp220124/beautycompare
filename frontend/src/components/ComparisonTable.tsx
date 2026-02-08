"use client";

import { MatchedProduct, PLATFORM_CONFIG, Platform } from "@/types";
import { formatPrice, cn } from "@/lib/utils";
import { ExternalLink, TrendingDown } from "lucide-react";

interface ComparisonTableProps {
  results: MatchedProduct[];
}

const PLATFORMS: Platform[] = ["nykaa", "amazon", "tira"];

export default function ComparisonTable({ results }: ComparisonTableProps) {
  if (!results.length) return null;

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b-2 border-gray-200">
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-600">
              Product
            </th>
            {PLATFORMS.map((p) => (
              <th key={p} className="py-3 px-4 text-center text-sm font-semibold">
                <span
                  className="inline-block rounded-full px-3 py-1 text-xs font-bold text-white"
                  style={{ backgroundColor: PLATFORM_CONFIG[p].color }}
                >
                  {PLATFORM_CONFIG[p].name}
                </span>
              </th>
            ))}
            <th className="py-3 px-4 text-center text-sm font-semibold text-green-600">
              Savings
            </th>
          </tr>
        </thead>
        <tbody>
          {results.map((item, idx) => {
            const priceMap: Record<string, typeof item.prices[0] | undefined> = {};
            item.prices.forEach((p) => {
              priceMap[p.platform] = p;
            });

            return (
              <tr
                key={idx}
                className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
              >
                {/* Product Info */}
                <td className="py-4 px-4">
                  <div className="flex items-center gap-3">
                    {item.image_url && (
                      <img
                        src={item.image_url}
                        alt={item.product_name}
                        className="w-12 h-12 object-contain rounded shrink-0"
                        loading="lazy"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = "none";
                        }}
                      />
                    )}
                    <div>
                      <p className="text-sm font-medium text-gray-800 line-clamp-2">
                        {item.product_name}
                      </p>
                      {item.brand && (
                        <p className="text-xs text-gray-500">{item.brand}</p>
                      )}
                    </div>
                  </div>
                </td>

                {/* Platform Prices */}
                {PLATFORMS.map((platform) => {
                  const entry = priceMap[platform];
                  const isBest = entry && entry.price === item.best_price;

                  return (
                    <td key={platform} className="py-4 px-4 text-center">
                      {entry ? (
                        <div className="flex flex-col items-center gap-1">
                          <span
                            className={cn(
                              "text-lg font-bold",
                              isBest ? "text-green-600" : "text-gray-800"
                            )}
                          >
                            {formatPrice(entry.price)}
                          </span>
                          {entry.mrp > entry.price && (
                            <span className="text-xs text-gray-400 line-through">
                              {formatPrice(entry.mrp)}
                            </span>
                          )}
                          {entry.product_url && (
                            <a
                              href={entry.product_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-xs text-blue-500 hover:underline mt-1"
                            >
                              Visit <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                        </div>
                      ) : (
                        <span className="text-sm text-gray-300">N/A</span>
                      )}
                    </td>
                  );
                })}

                {/* Savings */}
                <td className="py-4 px-4 text-center">
                  {item.savings > 0 ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-green-50 px-3 py-1 text-sm font-semibold text-green-700">
                      <TrendingDown className="w-3.5 h-3.5" />
                      {formatPrice(item.savings)}
                    </span>
                  ) : (
                    <span className="text-sm text-gray-300">-</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
