import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://go84sgscs4ckcs08wog84o0o.app.generaia.site',
        changeOrigin: true,
      },
    },
  },
})
