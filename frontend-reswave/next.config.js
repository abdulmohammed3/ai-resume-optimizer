/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:3001/api/v1/:path*',
        // Allow file uploads through the rewrite
        has: [
          {
            type: 'header',
            key: 'content-type',
            value: '(.*)'
          }
        ]
      },
    ];
  },
};

module.exports = nextConfig;