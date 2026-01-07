import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    allowedHosts: [
      'meihuayishu.vip.cpolar.cn',
      '127.0.0.1',
      'localhost',
      '116.62.45.105'
    ],
    // 添加代理配置
    proxy: {
      '/api': {
        target: 'http://116.62.45.105:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
    // 或者使用 'all' 允许所有主机（不推荐生产环境）
    // allowedHosts: 'all'
  }
})
