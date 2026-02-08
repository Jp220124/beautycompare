import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static export for Cloudflare Pages / any static host
  output: "export",
  images: {
    unoptimized: true, // Required for static export (no server-side image optimization)
    remotePatterns: [
      { hostname: "images-static.nykaa.com" },
      { hostname: "*.nykaa.com" },
      { hostname: "images-eu.ssl-images-amazon.com" },
      { hostname: "m.media-amazon.com" },
      { hostname: "*.tirabeauty.com" },
      { hostname: "*.cloudfront.net" },
    ],
  },
};

export default nextConfig;
