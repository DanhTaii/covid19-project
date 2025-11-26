import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  //Kết nối frontend với backend
 plugins: [react()],
 //Dùng để đặt alias cho các thư mục
 resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@pages": path.resolve(__dirname, "./src/pages"),
      "@services": path.resolve(__dirname, "./src/services"),
      // stream: path.resolve(__dirname, 'node_modules/stream-browserify/index.js'),

      stream: 'stream-browserify',
      buffer: 'buffer',
      util: 'util',
      process: 'process/browser',
      zlib: 'browserify-zlib',
    }
  },
  define: {
    global: 'window',
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // Django backend
        changeOrigin: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    }
  },
define: {
    global: 'window', // <-- Đây là giải pháp cho lỗi ReferenceError: global is not defined
  },
  
})
