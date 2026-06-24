import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: {
        enabled: true
      },
      manifest: {
        name: 'PyMeet',
        short_name: 'PyMeet',
        description: 'PyMeet Video Conferencing Application',
        theme_color: '#121212',
        background_color: '#121212',
        display: "standalone",
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  server: {
    host: true,
    port: 5173,
    allowedHosts: true,
    proxy: {
      "/api": "http://backend:8000",
      "/socket.io": {
        target: "http://backend:8000",
        ws: true
      }
    }
  },
  preview: {
    host: true,
    port: 5173,
    allowedHosts: true,
    proxy: {
      "/api": "http://backend:8000",
      "/socket.io": {
        target: "http://backend:8000",
        ws: true
      }
    }
  }
});
