import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  root: "./src",
  build: {
    outDir: "../build", // Output folder for production build
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, "src/index.html"),
        preload: path.resolve(__dirname, "src/preload.js"),
        renderer: path.resolve(__dirname, "src/renderer.js"), // Explicitly add renderer.js
      },
      output: {
        entryFileNames: "[name].js", // Keeps original filenames
      },
    },
  },
  publicDir: "../public",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
});
