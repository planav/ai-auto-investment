import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // VITE_BASE_URL is set to '/ai-auto-investment/' when building for GitHub Pages
  // so that all asset paths are correct under the project subdirectory.
  base: process.env.VITE_BASE_URL || '/',
})
