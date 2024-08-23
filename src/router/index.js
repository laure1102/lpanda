import Vue from 'vue'
import VueRouter from 'vue-router'

// 注册路由插件
Vue.use(VueRouter)

// 
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../pages/App.vue')
  },
]

const router = new VueRouter({
  scrollBehavior: () => ({ y: 0 }),
  routes
})

export default router
