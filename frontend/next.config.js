/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
    ];
  },
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
  },
};

module.exports = nextConfig; 