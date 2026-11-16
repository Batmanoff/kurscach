import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#141414",
        paper: "#F3EFE7",
        mist: "#E6E1D6",
        accent: "#1F3A34",
        muted: "#6B6B6B",
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "Helvetica Neue", "Arial", "sans-serif"],
      },
      letterSpacing: {
        brand: "0.28em",
      },
    },
  },
  plugins: [],
};

export default config;
