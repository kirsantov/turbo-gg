import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  transpilePackages: ['@frontend/types', '@frontend/ui']
}

export default nextConfig
