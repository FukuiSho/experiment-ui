import type { NextConfig } from "next";
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const configRoot = path.dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
  turbopack: {
    root: configRoot,
  },
};

export default nextConfig;
