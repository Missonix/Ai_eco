import { createRouter, createWebHistory } from 'vue-router'
import { checkIsLoggedIn } from '../utils/auth'
import Index from '../views/Index.vue'
import CheckPage from '../views/Home.vue'
import UserPage from '../views/User.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: Index
    },
    {
      path: '/check',
      name: 'check',
      component: CheckPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/user',
      name: 'user',
      component: UserPage
    }
  ]
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !checkIsLoggedIn()) {
    alert('请登录后使用此功能')
    next('/user')
  } else {
    next()
  }
})

export default router
