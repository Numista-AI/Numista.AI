import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  turbopack: {
    // Explicitly set the root to this package's directory to avoid the
    // "multiple lockfiles" warning caused by the Playwright package-lock.json
    // in the monorepo parent folder.
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
