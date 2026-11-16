/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "qr.nspk.ru" },
    ],
  },
  output: "standalone",
};

export default nextConfig;
