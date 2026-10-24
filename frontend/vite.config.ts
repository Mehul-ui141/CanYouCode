import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy all /api requests to the backend dev server.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
