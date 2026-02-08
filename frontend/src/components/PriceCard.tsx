"use client";

import { ProductResult, PLATFORM_CONFIG, Platform } from "@/types";
import { formatPrice, cn } from "@/lib/utils";
import { ExternalLink, Star, Tag } from "lucide-react";

interface PriceCardProps {
  product: ProductResult;
  isBestPrice?: boolean;
}

export default function PriceCard({ product, isBestPrice = false }: PriceCardProps) {
  const platform = PLATFORM_CONFIG[product.platform as Platform];

  return (
    <div
      className={cn(
        "relative rounded-xl border bg-white p-4 transition-all hover:shadow-md",
        isBestPrice
          ? "border-green-400 ring-2 ring-green-100"
          : "border-gray-200"
      )}
    >
      {isBestPrice && (
        <span className="absolute -top-3 left-4 rounded-full bg-green-500 px-3 py-0.5 text-xs font-semibold text-white">
          Best Price
        </span>
      )}

      {/* Platform Badge */}
      <div className="flex items-center justify-between mb-3">
        <span
          className="rounded-full px-3 py-1 text-xs font-bold text-white"
          style={{ backgroundColor: platform?.color || "#666" }}
        >
          {platform?.name || product.platform}
        </span>
        {product.discount_percent > 0 && (
          <span className="flex items-center gap-1 rounded-full bg-green-50 px-2 py-0.5 text-xs font-semibold text-green-700">
            <Tag className="w-3 h-3" />
            {product.discount_percent.toFixed(0)}% OFF
          </span>
        )}
      </div>

      {/* Product Image */}
      {product.image_url && (
        <div className="flex justify-center mb-3">
          <img
            src={product.image_url}
            alt={product.name}
            className="h-28 w-28 object-contain rounded"
            loading="lazy"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = "none";
            }}
          />
        </div>
      )}

      {/* Product Name */}
      <h3 className="text-sm font-medium text-gray-800 line-clamp-2 mb-2 min-h-[2.5rem]">
        {product.name}
      </h3>

      {/* Price */}
      <div className="flex items-baseline gap-2 mb-2">
        <span className="text-2xl font-bold text-gray-900">
          {formatPrice(product.price)}
        </span>
        {product.mrp > product.price && (
          <span className="text-sm text-gray-400 line-through">
            {formatPrice(product.mrp)}
          </span>
        )}
      </div>

      {/* Rating */}
      {product.rating > 0 && (
        <div className="flex items-center gap-1 mb-3 text-sm text-gray-500">
          <Star className="w-3.5 h-3.5 fill-yellow-400 text-yellow-400" />
          <span>{product.rating.toFixed(1)}</span>
          {product.rating_count > 0 && (
            <span className="text-gray-400">({product.rating_count.toLocaleString()})</span>
          )}
        </div>
      )}

      {/* Stock Status */}
      {!product.in_stock && (
        <p className="text-xs text-red-500 font-medium mb-2">Out of Stock</p>
      )}

      {/* Buy Button */}
      {product.product_url && (
        <a
          href={product.product_url}
          target="_blank"
          rel="noopener noreferrer"
          className={cn(
            "flex items-center justify-center gap-2 w-full rounded-lg py-2.5 text-sm font-semibold text-white transition-colors",
            isBestPrice
              ? "bg-green-500 hover:bg-green-600"
              : "bg-gray-800 hover:bg-gray-900"
          )}
        >
          Buy on {platform?.name || product.platform}
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      )}
    </div>
  );
}
