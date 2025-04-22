import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/user',
  },
  {
    path: '/user',
    name: 'User',
    component: () => import('@/views/user/UserList.vue'),
  },
  {
    path: '/course',
    name: 'Course',
    component: () => import('@/views/course/CourseList.vue'),
  },
  {
    path: '/product',
    name: 'Product',
    component: () => import('@/views/product/ProductList.vue'),
  },
  {
    path: '/order',
    name: 'Order',
    component: () => import('@/views/order/OrderList.vue'),
  },
  {
    path: '/entitlement',
    name: 'Entitlement',
    component: () => import('@/views/entitlement/EntitlementList.vue'),
  },
  {
    path: '/user-entitlement',
    name: 'UserEntitlement',
    component: () => import('@/views/userEntitlement/UserEntitlementList.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
