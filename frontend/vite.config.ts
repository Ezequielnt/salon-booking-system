import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // Necesario para que el hot-reload funcione con el bind mount de Docker.
    watch: { usePolling: true },
  },
});
