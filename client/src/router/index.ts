import { createRouter, createWebHistory } from 'vue-router'
import { checkIsLoggedIn, checkFeatureAccess } from '../utils/auth'
import Index from '../views/Index.vue'
import UserPage from '../views/User.vue'
import { aiProducts } from '../config/aiProducts'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: Index
    },
    {
      path: '/user',
      name: 'user',
      component: UserPage
    },
    // 动态添加AI产品路由
    ...aiProducts.map(product => ({
      path: `/${product.id}`,
      name: product.id,
      component: product.component,
      meta: { 
        requiresAuth: true,
        ruleId: product.rule_id
      }
    }))
  ]
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    if (!checkIsLoggedIn()) {
      alert('请登录后使用此功能')
      next('/user')
    } else if (to.meta.ruleId && !checkFeatureAccess(to.meta.ruleId as string)) {
      alert('您暂无此功能的使用权限')
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
