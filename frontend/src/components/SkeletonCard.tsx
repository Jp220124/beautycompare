"use client";

export default function SkeletonCard() {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 animate-pulse">
      <div className="flex items-center justify-between mb-3">
        <div className="h-6 w-16 rounded-full bg-gray-200" />
        <div className="h-5 w-14 rounded-full bg-gray-100" />
      </div>
      <div className="flex justify-center mb-3">
        <div className="h-28 w-28 rounded bg-gray-100" />
      </div>
      <div className="h-4 w-3/4 rounded bg-gray-200 mb-1" />
      <div className="h-4 w-1/2 rounded bg-gray-100 mb-3" />
      <div className="h-8 w-1/3 rounded bg-gray-200 mb-2" />
      <div className="h-10 w-full rounded-lg bg-gray-200" />
    </div>
  );
}

export function SkeletonTable() {
  return (
    <div className="w-full animate-pulse space-y-3">
      <div className="h-10 w-full rounded bg-gray-100" />
      {[...Array(4)].map((_, i) => (
        <div key={i} className="flex gap-4 py-3">
          <div className="h-12 w-12 rounded bg-gray-100 shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-3/4 rounded bg-gray-100" />
            <div className="h-3 w-1/4 rounded bg-gray-50" />
          </div>
          <div className="h-6 w-20 rounded bg-gray-100" />
          <div className="h-6 w-20 rounded bg-gray-100" />
          <div className="h-6 w-20 rounded bg-gray-100" />
        </div>
      ))}
    </div>
  );
}
