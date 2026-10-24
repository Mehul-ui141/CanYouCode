/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Original zinc palette (preserved for compatibility)
        zinc: {
          50: "#fafafa",
          100: "#f4f4f5",
          200: "#e4e4e7",
          300: "#d4d4d8",
          400: "#a1a1aa",
          500: "#71717a",
          600: "#52525b",
          700: "#27272a",
          800: "#18181b",
          900: "#09090b",
          950: "#000000",
        },
        // Luxury brand palette
        luxury: {
          // Dark mode base
          obsidian: "#1C1B19",
          champagne: "#C6AE83",      // Primary accent (champagne)
          sageGrey: "#777B70",         // Secondary accent
          // Light mode base
          ivory: "#F5F0E8",
          mocha: "#80664D",             // Primary accent (mocha)
          mushroom: "#B6A99A",         // Secondary accent
          // Supporting shades
          textPrimaryDark: "#F5F0E8",
          textSecondaryDark: "#B8B1A5",
          textMutedDark: "#777B70",
          cardDark: "#252421",
          borderDark: "#3A3731",
          textPrimaryLight: "#332A24",
          textSecondaryLight: "#6E6257",
          textMutedLight: "#B6A99A",
          cardLight: "#FFFCF7",
          borderLight: "#E3D9CC",
        },
        // Keep red palette for personality themes (compatible)
        red: {
          400: "#f87171",
          500: "#ef4444",
          600: "#dc2626",
          700: "#b91c1c",
          800: "#991b1b",
        },
        // Keep other color palettes for compatibility
        rose: { 400: "#fb7185", 500: "#f43f5e", 600: "#e11d48" },
        amber: { 400: "#fbbf24", 500: "#f59e0b", 600: "#d97706" },
        emerald: { 400: "#34d399", 500: "#10b981", 600: "#059669" },
        sky: { 400: "#38bdf8", 500: "#0ea5e9", 600: "#0284c7" },
        indigo: { 400: "#818cf8", 500: "#6366f1", 600: "#4f46e5" },
        violet: { 400: "#a78bfa", 500: "#8b5cf6", 600: "#7c3aed" },
        pink: { 400: "#f472b6", 500: "#ec4899", 600: "#db2777" },
        green: { 400: "#4ade80", 500: "#22c55e", 600: "#16a34a" },
        orange: { 400: "#fb923c", 500: "#f97316", 600: "#ea580c" },
      },
      animation: {
        "cursor-blink": "cursor-blink 1s step-end infinite",
        shimmer: "shimmer 3s linear infinite",
      },
      keyframes: {
        "cursor-blink": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% center" },
          "100%": { backgroundPosition: "200% center" },
        },
      },
      backgroundSize: {
        "200": "200% auto",
      },
      boxShadow: {
        luxury: "0 4px 20px rgba(28, 27, 25, 0.08)", // Subtle luxury shadow
        "luxury-light": "0 4px 20px rgba(245, 240, 232, 0.08)",
      },
    },
  },
  plugins: [],
};
