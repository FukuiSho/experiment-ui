import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 特定のパッケージをNext.jsに正しく処理させる設定
  transpilePackages: ["@chroma-core/default-embed", "@chroma-core/ai-embeddings-common"],
  experimental: {
    turbo: {
      // 警告が出ているファイルを無視、または適切に処理するための設定
      rules: {
        "*.md": ["raw-loader"],
      },
    },
  },
};

export default nextConfig;