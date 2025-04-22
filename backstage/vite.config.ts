import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
// 这一行setup配置
import vueSetupExtend from 'vite-plugin-vue-setup-extend'

// 配置vite
// https://vite.dev/config/
export default defineConfig({
  // 还有这里
  plugins: [vue(), vueJsx(), vueDevTools(), vueSetupExtend()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
