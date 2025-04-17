<template>
  <div class="max-w-md mx-auto p-4">
    <h1 class="text-xl font-bold text-center mb-6">个人中心</h1>

    <!-- 未登录状态 -->
    <div v-if="!isLoggedIn" class="bg-white rounded-lg shadow p-6">
      <template v-if="!showLoginForm">
        <div class="text-center">
          <p class="text-gray-600 mb-4">您还未登录</p>
          <button
            @click="showLoginForm = true"
            class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
          >
            立即登录
          </button>
        </div>
      </template>

      <!-- 登录表单 -->
      <form v-else @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label for="account" class="block text-sm font-medium text-gray-700 mb-1">账号</label>
          <input
            id="account"
            v-model="account"
            type="text"
            required
            placeholder="请输入用户名"
            class="mt-1 block w-full px-4 py-2 rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-1">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            placeholder="请输入密码"
            class="mt-1 block w-full px-4 py-2 rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div class="flex items-center justify-between pt-2">
          <button
            type="submit"
            :disabled="loading"
            class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>
          <button
            type="button"
            @click="showLoginForm = false"
            class="text-gray-600 hover:text-gray-800"
          >
            取消
          </button>
        </div>
      </form>
    </div>

    <!-- 已登录状态 -->
    <div v-else class="bg-white rounded-lg shadow p-6">
      <div class="text-center space-y-4">
        <div class="text-gray-600">欢迎您，{{ userInfo.username }}</div>

        <!-- 用户信息展示 -->
        <div class="bg-gray-50 rounded-lg p-4 space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-500">用户等级</span>
            <span class="font-medium text-indigo-600">Level {{ userInfo.level }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-500">剩余使用次数</span>
            <span class="font-medium text-indigo-600">{{ userInfo.usage_count }} 次</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-500">用户ID</span>
            <span class="font-medium text-gray-600">{{ userInfo.user_id }}</span>
          </div>
        </div>

        <button @click="handleLogout" class="text-indigo-600 hover:text-indigo-800">
          退出登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

interface UserInfo {
  user_id: string
  username: string
  is_admin: boolean
  is_active: boolean
  access_token: string
  level: number
  usage_count: number
}

const isLoggedIn = ref(false)
const showLoginForm = ref(false)
const loading = ref(false)
const account = ref('')
const password = ref('')
const userInfo = ref<UserInfo | null>(null)

// 登录处理
const handleLogin = async () => {
  if (!account.value || !password.value) {
    alert('请输入账号和密码')
    return
  }

  loading.value = true
  try {
    const response = await axios.post('http://10.7.21.239:4455/users/login', {
      account: account.value,
      password: password.value,
    })

    if (response.data.code === 200) {
      const userData = response.data.data
      // 保存完整的用户信息
      userInfo.value = {
        user_id: userData.user_id,
        username: userData.username,
        is_admin: userData.is_admin,
        is_active: userData.is_active,
        access_token: userData.access_token,
        level: userData.level,
        usage_count: userData.usage_count,
      }
      isLoggedIn.value = true
      showLoginForm.value = false

      // 保存登录状态和用户信息
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
      localStorage.setItem('accessToken', userData.access_token)

      // 设置 axios 默认 headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${userData.access_token}`
    } else {
      throw new Error('登录失败')
    }
  } catch (error) {
    console.error('登录失败:', error)
    alert('用户名或密码错误')
  } finally {
    loading.value = false
  }
}

// 退出登录
const handleLogout = () => {
  isLoggedIn.value = false
  userInfo.value = null
  account.value = ''
  password.value = ''

  // 清除存储的信息
  localStorage.removeItem('userInfo')
  localStorage.removeItem('accessToken')

  // 清除 axios 默认 headers
  delete axios.defaults.headers.common['Authorization']
}

// 检查登录状态
const checkLoginStatus = () => {
  const savedUserInfo = localStorage.getItem('userInfo')
  const accessToken = localStorage.getItem('accessToken')

  if (savedUserInfo && accessToken) {
    userInfo.value = JSON.parse(savedUserInfo)
    isLoggedIn.value = true
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
  }
}

// 页面加载时检查登录状态
checkLoginStatus()
</script>
