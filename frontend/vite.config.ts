/// <reference types="vite/client" />

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api/v1': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.error('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            proxyReq.setHeader('Origin', 'http://localhost:3000');
            console.log('Proxying request:', {
              originalUrl: req.url,
              modifiedPath: proxyReq.path,
              method: req.method,
              headers: proxyReq.getHeaders()
            });
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received response:', {
              path: req.url,
              status: proxyRes.statusCode,
              headers: proxyRes.headers
            });
          });
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
}); 