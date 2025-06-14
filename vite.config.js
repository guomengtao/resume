import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  base: '/web-time-tracker/', // 👈 仓库名对应的路径，必须加！
  plugins: [vue()],
  server: {
    host: '0.0.0.0'
  }
});