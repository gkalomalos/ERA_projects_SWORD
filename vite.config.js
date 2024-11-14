import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  root: "./src",
  build: {
    outDir: "../build",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, "src/index.html"),
        preload: path.resolve(__dirname, "src/preload.js"),
        renderer: path.resolve(__dirname, "src/renderer.js"),
      },
      output: {
        entryFileNames: "[name].js",
      },
    },
  },
  publicDir: "../public",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
    extensions: [".js", ".jsx"],
  },
});
