import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
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
