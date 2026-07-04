import { loadEnv, defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())

  return {
    server: {
      host: '0.0.0.0',
      port: 8090,
      https: false,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:7860',
          changeOrigin: true,
        }
      },
    },
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    }
  }
})