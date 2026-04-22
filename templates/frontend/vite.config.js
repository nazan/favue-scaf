import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const hmrClientPort = process.env.VITE_HMR_CLIENT_PORT
  ? parseInt(process.env.VITE_HMR_CLIENT_PORT, 10)
  : undefined

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    ...(hmrClientPort
      ? {
          hmr: {
            protocol: 'ws',
            host: 'localhost',
            clientPort: hmrClientPort,
          },
        }
      : {}),
  },
})
