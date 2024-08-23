// 配置说明：https://cn.vitejs.dev/config/

import { createVuePlugin } from 'vite-plugin-vue2'
import path from 'path'

export default {
  resolve: {
    alias: {
      '@': path.join(__dirname, './src'),
    },
    extensions: ['.js', '.vue', '.json', '.css', '.ts', '.jsx']
  },
  base: './',
  plugins: [createVuePlugin()]
}
