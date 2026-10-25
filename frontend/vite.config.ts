
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Forward frontend API requests to the local FastAPI server.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/rag': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
