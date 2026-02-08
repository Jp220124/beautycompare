"use client";

import { WifiOff } from "lucide-react";

export default function OfflinePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#fafafa] px-4">
      <div className="text-center max-w-md">
        <WifiOff className="w-16 h-16 text-gray-300 mx-auto mb-6" />
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          You&apos;re Offline
        </h1>
        <p className="text-gray-500 mb-6">
          BeautyCompare needs an internet connection to fetch live prices from
          Nykaa, Tira, and Amazon. Please check your connection and try again.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-3 bg-pink-500 text-white rounded-xl font-medium hover:bg-pink-600 transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}
