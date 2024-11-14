import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path, { resolve } from "path";

export default defineConfig({
  plugins: [react()],
  root: "./src",
  build: {
    outDir: "../build",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        preload: path.resolve(__dirname, "src/preload.js"),
      },
    },
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
});
