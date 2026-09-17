import path from "node:path"
import { fileURLToPath } from "node:url"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

const root = path.dirname(fileURLToPath(import.meta.url))
// Same variable Django reads (main/settings.py), so both sides agree on the dev server address.
const DEV_SERVER_URL = new URL(process.env.VITE_DEV_SERVER_URL ?? "http://localhost:5173")

export default defineConfig(({ command }) => ({
  plugins: [react()],
  // Built files are served by Django under STATIC_URL; the dev server serves from its root.
  base: command === "build" ? "/static/" : "/",
  resolve: {
    alias: {
      "@": root,
    },
  },
  server: {
    port: Number(DEV_SERVER_URL.port) || 5173,
    strictPort: true,
    // Django serves the HTML, so asset URLs must point back at the dev server.
    origin: DEV_SERVER_URL.origin,
  },
  build: {
    outDir: "../static",
    emptyOutDir: true,
    // Read by the {% vite_assets %} template tag (VITE_MANIFEST_PATH).
    manifest: "manifest.json",
    rollupOptions: {
      input: path.resolve(root, "app.jsx"),
    },
  },
  test: {
    include: ["**/*.test.js"],
    exclude: ["node_modules/**"],
  },
}))
