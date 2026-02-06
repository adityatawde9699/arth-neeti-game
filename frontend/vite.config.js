import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: true,
    headers: {
      // Keep this to allow the popup to communicate
      // "Cross-Origin-Opener-Policy": "same-origin-allow-popups",
      // REMOVE the Embedder-Policy to stop the browser from blocking the popup
      // "Cross-Origin-Embedder-Policy": "require-corp", 
    },
  },
  preview: {
    allowedHosts: true,
    headers: {
      "Cross-Origin-Opener-Policy": "same-origin-allow-popups",
    },
  },
})