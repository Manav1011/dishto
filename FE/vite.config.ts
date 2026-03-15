import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: [
      'dishto.in',
      '.dishto.in', // Allows all subdomains
      'lvh.me',
      '.lvh.me'
    ],
    // We don't need the proxy here anymore since Nginx is handling it
    // but keeping a placeholder for simplicity if you ever run without Nginx
    proxy: {
      '/api-local': {
        target: 'https://dishto.in',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
