<template>
  <div class="max-w-md mx-auto p-4">
    <h1 class="text-xl font-bold text-center mb-6">个人中心</h1>

    <!-- 未登录状态 -->
    <div v-if="!isLoggedIn" class="bg-white rounded-lg shadow p-6">
      <!-- 登录/注册选项 -->
      <div v-if="!showLoginForm && !showRegisterForm" class="text-center space-y-4">
        <p class="text-gray-600 mb-4">您还未登录</p>
        <div class="flex justify-center space-x-4">
          <button
            @click="showLoginForm = true; showRegisterForm = false"
            class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
          >
            登录
          </button>
          <button
            @click="showRegisterForm = true; showLoginForm = false"
            class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
          >
            注册
          </button>
        </div>
      </div>

      <!-- 登录表单 -->
      <form v-if="showLoginForm" @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">手机号</label>
          <input
            id="phone"
            v-model="phone"
            type="text"
            required
            placeholder="请输入手机号"
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
            返回
          </button>
        </div>
      </form>

      <!-- 注册表单 -->
      <form v-if="showRegisterForm" @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label for="registerPhone" class="block text-sm font-medium text-gray-700 mb-1">手机号</label>
          <input
            id="registerPhone"
            v-model="registerPhone"
            type="text"
            required
            placeholder="请输入手机号"
            class="mt-1 block w-full px-4 py-2 rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label for="registerPassword" class="block text-sm font-medium text-gray-700 mb-1">密码</label>
          <input
            id="registerPassword"
            v-model="registerPassword"
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
            class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ loading ? '注册中...' : '注册' }}
          </button>
          <button
            type="button"
            @click="showRegisterForm = false"
            class="text-gray-600 hover:text-gray-800"
          >
            返回
          </button>
        </div>
      </form>
    </div>

    <!-- 已登录状态 -->
    <div v-else class="space-y-6">
      <!-- 用户基本信息 -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-center space-y-4">
          <div class="text-gray-600">欢迎您，{{ userInfo?.phone }}</div>
          <div class="text-sm text-gray-500">用户ID: {{ userInfo?.user_id }}</div>
        </div>
      </div>

      <!-- 用户权益信息 -->
      <div v-if="userInfo?.entitlements && userInfo.entitlements.length > 0" class="space-y-4">
        <h2 class="text-lg font-medium text-gray-900">我的权益</h2>
        <div v-for="entitlement in userInfo.entitlements" :key="entitlement.entitlement_id" 
             class="bg-white rounded-lg shadow p-4 space-y-3">
          <div class="flex justify-between items-start">
            <div class="space-y-1">
              <div class="font-medium text-gray-900">{{ entitlement.course_name }}</div>
              <div class="text-sm text-gray-500">产品：{{ entitlement.product_name }}</div>
            </div>
            <div :class="entitlement.is_active ? 'text-green-500' : 'text-red-500'" class="text-sm">
              {{ entitlement.is_active ? '生效中' : '已失效' }}
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div class="text-gray-500">生效时间</div>
              <div class="text-gray-900">{{ formatDate(entitlement.start_date) }}</div>
            </div>
            <div>
              <div class="text-gray-500">失效时间</div>
              <div class="text-gray-900">{{ formatDate(entitlement.end_date) }}</div>
            </div>
          </div>
          <div class="text-sm">
            <div class="text-gray-500">今日剩余额度</div>
            <div class="text-indigo-600 font-medium">{{ entitlement.daily_remaining }}次</div>
          </div>
        </div>
      </div>

      <!-- 退出登录按钮 -->
      <div class="text-center">
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
import { useRouter } from 'vue-router'

interface Entitlement {
  entitlement_id: string
  rule_id: string
  course_name: string
  product_name: string
  ai_product_id: string
  start_date: string
  end_date: string
  daily_remaining: number
  is_active: boolean
}

interface UserInfo {
  user_id: string
  phone: string
  access_token: string
  entitlements: Entitlement[]
}

const router = useRouter()
const isLoggedIn = ref(false)
const showLoginForm = ref(false)
const showRegisterForm = ref(false)
const loading = ref(false)
const phone = ref('')
const password = ref('')
const registerPhone = ref('')
const registerPassword = ref('')
const userInfo = ref<UserInfo | null>(null)

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 登录处理
const handleLogin = async () => {
  if (!phone.value || !password.value) {
    alert('请输入手机号和密码')
    return
  }

  loading.value = true
  try {
    const response = await axios.post('http://10.7.21.239:4455/users/login', {
      phone: phone.value,
      password: password.value
    })

    if (response.data.code === 200) {
      // 获取用户基本信息
      const userBasicInfo = response.data.data
      
      // 获取用户权益信息
      const entitlementsResponse = await axios.post('http://10.7.21.239:4455/user_entitlements/search', {
        phone: phone.value
      })

      if (entitlementsResponse.data.code === 200) {
        // 合并用户信息和权益信息
        userInfo.value = {
          ...userBasicInfo,
          entitlements: entitlementsResponse.data.data.items
        }
        isLoggedIn.value = true
        showLoginForm.value = false

        // 保存登录状态和用户信息
        if (userInfo.value) {
          localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
          localStorage.setItem('accessToken', userInfo.value.access_token)

          // 设置 axios 默认 headers
          axios.defaults.headers.common['Authorization'] = `Bearer ${userInfo.value.access_token}`
        }
      } else {
        throw new Error(entitlementsResponse.data.message || '获取用户权益失败')
      }
    } else {
      throw new Error(response.data.message || '登录失败')
    }
  } catch (error: any) {
    console.error('登录失败:', error)
    alert(error.response?.data?.message || '登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 注册处理
const handleRegister = async () => {
  if (!registerPhone.value || !registerPassword.value) {
    alert('请输入手机号和密码')
    return
  }

  loading.value = true
  try {
    const response = await axios.post('http://10.7.21.239:4455/users/register', {
      phone: registerPhone.value,
      password: registerPassword.value
    })

    if (response.data.code === 200) {
      alert('注册成功，请登录')
      showRegisterForm.value = false
      showLoginForm.value = true
    } else {
      throw new Error(response.data.message || '注册失败')
    }
  } catch (error: any) {
    console.error('注册失败:', error)
    alert(error.response?.data?.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await axios.get('http://10.7.21.239:4455/users/logout')
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    isLoggedIn.value = false
    userInfo.value = null
    phone.value = ''
    password.value = ''
    registerPhone.value = ''
    registerPassword.value = ''

    // 清除存储的信息
    localStorage.removeItem('userInfo')
    localStorage.removeItem('accessToken')

    // 清除 axios 默认 headers
    delete axios.defaults.headers.common['Authorization']
  }
}

// 检查登录状态
const checkLoginStatus = async () => {
  const savedUserInfo = localStorage.getItem('userInfo')
  const accessToken = localStorage.getItem('accessToken')

  if (savedUserInfo && accessToken) {
    const userData = JSON.parse(savedUserInfo)
    try {
      // 获取最新的用户权益信息
      const entitlementsResponse = await axios.post('http://10.7.21.239:4455/user_entitlements/search', {
        phone: userData.phone
      })

      if (entitlementsResponse.data.code === 200) {
        // 更新用户信息中的权益数据
        userInfo.value = {
          ...userData,
          entitlements: entitlementsResponse.data.data.items
        }
        localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
      }
    } catch (error) {
      console.error('获取用户权益失败:', error)
    }
    isLoggedIn.value = true
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
  }
}

// 页面加载时检查登录状态
checkLoginStatus()
</script>
