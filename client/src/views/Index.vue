<template>
  <div class="max-w-md mx-auto p-4">
    <!-- Logo区域 -->
    <header class="text-center py-8">
      <div class="flex justify-center">
        <img src="@/assets/logo.png" alt="公司Logo" class="h-16 object-contain" />
      </div>
    </header>

    <!-- 功能列表区域 -->
    <main class="space-y-4">
      <h2 class="text-lg font-medium text-gray-900 mb-4">功能列表</h2>

      <!-- 功能卡片 -->
      <div
        v-for="product in aiProducts"
        :key="product.id"
        class="block bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-300 cursor-pointer"
        @click="handleFeatureClick(product)"
      >
        <div class="p-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-medium text-gray-900">{{ product.name }}</h3>
              <p class="mt-1 text-sm text-gray-500">{{ product.description }}</p>
            </div>
            <div class="flex items-center">
              <span v-if="!checkFeatureAccess(product.ai_product_id)" class="text-sm text-red-500 mr-2">
                无使用权限
              </span>
              <div class="text-indigo-600">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 免责声明 -->
    <footer class="mt-8 text-xs text-gray-400 text-center px-4">内容由 AI 生成，请仔细甄别</footer>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { checkIsLoggedIn } from '../utils/auth'
import { aiProducts } from '../config/aiProducts'

const router = useRouter()

// 检查用户是否有特定功能的访问权限
const checkFeatureAccess = (aiProductId: string): boolean => {
  const userInfo = localStorage.getItem('userInfo')
  if (!userInfo) return false
  
  const userData = JSON.parse(userInfo)
  if (!userData.entitlements || !userData.entitlements.length) return false
  
  return userData.entitlements.some(
    (ent: any) => ent.is_active && ent.ai_product_id === aiProductId
  )
}

const handleFeatureClick = (product: any) => {
  if (!checkIsLoggedIn()) {
    alert('请登录后使用此功能')
    router.push('/user')
  } else if (!checkFeatureAccess(product.ai_product_id)) {
    alert('您暂无此功能的使用权限')
  } else {
    router.push(`/${product.id}`)
  }
}
</script>
