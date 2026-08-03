import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', 
    port: 5173,
    allowedHosts: [
      'property-nemeses-encroach.ngrok-free.dev'
    ],
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/users': 'http://127.0.0.1:8000',
      '/categories': 'http://127.0.0.1:8000',
      '/body-info': 'http://127.0.0.1:8000',
    },
  }
})
