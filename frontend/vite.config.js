import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      // Proxy ALL backend routes directly
      '/sessions': { target: 'http://localhost:8000', changeOrigin: true },
      '/papers':   { target: 'http://localhost:8000', changeOrigin: true },
      '/qa':       { target: 'http://localhost:8000', changeOrigin: true },
      '/analysis': { target: 'http://localhost:8000', changeOrigin: true },
      '/auth':     { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})