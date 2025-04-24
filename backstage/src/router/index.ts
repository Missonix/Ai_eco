import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginView.vue'),
    meta: {
      requiresAuth: false,
    },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/LayoutView.vue'),
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/DashboardHome.vue'),
        meta: {
          requiresAuth: true,
        },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/user/UserList.vue'),
        meta: {
          requiresAuth: true,
        },
      },
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('@/views/course/CourseList.vue'),
        meta: {
          requiresAuth: true,
        },
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/product/ProductList.vue'),
        meta: {
          requiresAuth: true,
        },
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/order/OrderList.vue'),
        meta: {
          requiresAuth: true,
        },
      },
      {
        path: 'entitlements',
        name: 'Entitlements',
        component: () => import('@/views/entitlement/EntitlementList.vue'),
        meta: {
          requiresAuth: true,
        },
      },
      {
        path: 'user-entitlements',
        name: 'UserEntitlements',
        component: () => import('@/views/userEntitlement/UserEntitlementList.vue'),
        meta: {
          requiresAuth: true,
        },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

  if (requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
