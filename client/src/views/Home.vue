<template>
  <div class="max-w-md mx-auto p-4 pb-16">
    <!-- 头部 -->
    <header class="py-4">
      <div class="flex items-center mb-4">
        <router-link to="/" class="text-indigo-600 hover:text-indigo-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </router-link>
        <h1 class="text-xl font-bold text-center flex-1 pr-6">直播话术违规词AI检测</h1>
        <button @click="showHistory = true" class="text-indigo-600 hover:text-indigo-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>
    </header>

    <!-- 主要内容区 -->
    <main class="space-y-6">
      <!-- 输入框部分 -->
      <div class="bg-white rounded-lg p-4 shadow">
        <textarea
          v-model="inputText"
          class="w-full h-32 p-3 border rounded-lg resize-none"
          placeholder="请输入要检测的直播话术"
        ></textarea>
        <button
          @click="startCheck"
          :disabled="loading"
          class="w-full mt-4 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400"
        >
          {{ loading ? '检测中...' : '开始检测' }}
        </button>
        <p class="text-sm text-gray-500 text-center mt-2">
          AI检测完成后，将给您详细报告
        </p>
      </div>

      <!-- 检测报告部分 -->
      <div v-if="checkResult" class="bg-white rounded-lg p-4 shadow space-y-6">
        <h2 class="font-bold text-lg border-b pb-2">检测报告</h2>
        
        <!-- 基础信息 -->
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-gray-600">是否违规:</span>
            <span :class="checkResult.is_Violations === '是' ? 'text-red-500' : 'text-green-500'" class="font-medium">
              {{ checkResult.is_Violations === '是' ? '违规' : '合规' }}
            </span>
          </div>
          
          <!-- 评分对比 -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="grid grid-cols-2 gap-4">
              <div class="text-center">
                <div class="text-gray-500">优化前</div>
                <div class="text-2xl font-bold text-red-500">{{ checkResult.old_score }}分</div>
                <div class="text-sm text-gray-500">{{ checkResult.old_rating }}</div>
              </div>
              <div class="text-center">
                <div class="text-gray-500">优化后</div>
                <div class="text-2xl font-bold text-green-500">{{ checkResult.new_score }}分</div>
                <div class="text-sm text-gray-500">{{ checkResult.new_rating }}</div>
              </div>
            </div>
          </div>

          <!-- 违规词列表 -->
          <div v-if="checkResult.words" class="space-y-2">
            <div class="font-medium">违规词:</div>
            <div class="flex flex-wrap gap-2">
              <span v-for="word in checkResult.words.split(',')" :key="word"
                class="bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm">
                {{ word }}
              </span>
            </div>
          </div>

          <!-- 违规原因 -->
          <div v-if="checkResult.reason" class="space-y-2">
            <div class="font-medium">违规原因:</div>
            <div class="text-gray-600 text-sm whitespace-pre-line">{{ checkResult.reason }}</div>
          </div>

          <!-- 优化建议 -->
          <div class="space-y-4">
            <div class="font-medium">优化建议:</div>
            <div v-for="(suggestion, index) in [
              checkResult.op,
            ]" :key="index" class="bg-green-50 p-3 rounded-lg text-sm text-gray-600">
              {{ suggestion }}
            </div>
          </div>

          <!-- 优化思路 -->
          <div v-if="checkResult.ideas" class="space-y-2">
            <div class="font-medium">优化思路:</div>
            <div class="text-gray-600 text-sm whitespace-pre-line">{{ checkResult.ideas }}</div>
          </div>
        </div>
      </div>
    </main>

    <!-- 历史报告弹窗 -->
    <div v-if="showHistory" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg w-full max-w-md max-h-[80vh] overflow-hidden">
        <div class="p-4 border-b flex justify-between items-center">
          <h2 class="text-lg font-bold">历史检测报告</h2>
          <button @click="showHistory = false" class="text-gray-500 hover:text-gray-700">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-4 overflow-y-auto max-h-[calc(80vh-4rem)]">
          <div v-if="loadingHistory" class="text-center py-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
            <p class="mt-2 text-gray-600">加载中...</p>
          </div>
          <div v-else-if="historyRecords.length === 0" class="text-center py-4 text-gray-500">
            暂无历史记录
          </div>
          <div v-else class="space-y-4">
            <div v-for="record in historyRecords" :key="record.id" class="bg-gray-50 rounded-lg p-4">
              <div class="flex justify-between items-start mb-2">
                <div class="text-sm text-gray-500">{{ formatDate(record.created_at) }}</div>
                <span :class="record.is_violation ? 'text-red-500' : 'text-green-500'" class="text-sm font-medium">
                  {{ record.is_violation ? '违规' : '合规' }}
                </span>
              </div>
              <div class="space-y-2">
                <div class="text-sm">
                  <div class="font-medium text-gray-700">原文：</div>
                  <div class="text-gray-600">{{ record.input }}</div>
                </div>
                <div v-if="record.words" class="text-sm">
                  <div class="font-medium text-gray-700">违规词：</div>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="word in record.words.split(',')" :key="word"
                      class="bg-red-100 text-red-800 px-2 py-0.5 rounded-full text-xs">
                      {{ word }}
                    </span>
                  </div>
                </div>
                <div v-if="record.op" class="text-sm">
                  <div class="font-medium text-gray-700">优化建议：</div>
                  <div class="text-gray-600">{{ record.op }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 免责声明 -->
    <footer class="mt-8 text-xs text-gray-400 text-center px-4">
      提示：当前检测依据为平台过往违规话术特征库，因政策动态调整可能存在偏差，最终违规判定请以官方审核结果为准，本工具结果仅作学习参考。
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { aiProducts, type AIProduct } from '@/config/aiProducts'

interface CheckResult {
  is_Violations: string
  old_score: number
  old_rating: string
  new_score: number
  new_rating: string
  words?: string
  reason?: string
  op?: string
  ideas?: string
}

interface HistoryRecord {
  id: number
  phone: string
  input: string
  is_violation: boolean
  words: string
  reasons: string
  op: string
  ideas: string
  old_score: number
  new_score: number
  old_rating: string
  new_rating: string
  created_at: string
}

const router = useRouter()
const inputText = ref('')
const loading = ref(false)
const checkResult = ref<CheckResult | null>(null)
const showHistory = ref(false)
const loadingHistory = ref(false)
const historyRecords = ref<HistoryRecord[]>([])

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

// 获取历史记录
const fetchHistory = async () => {
  const userInfo = localStorage.getItem('userInfo')
  if (!userInfo) {
    alert('请先登录后查看历史记录')
    router.push('/user')
    return
  }

  loadingHistory.value = true
  try {
    const userData = JSON.parse(userInfo)
    const response = await axios.get(`http://10.7.21.239:4455/vio_word/words/phone/${userData.phone}`)
    
    if (response.data.code === 200) {
      historyRecords.value = response.data.data.items
    } else {
      throw new Error(response.data.message || '获取历史记录失败')
    }
  } catch (error: any) {
    console.error('获取历史记录失败:', error)
    alert(error.response?.data?.message || '获取历史记录失败，请稍后重试')
  } finally {
    loadingHistory.value = false
  }
}

// 监听showHistory变化
watch(showHistory, (newVal: boolean) => {
  if (newVal) {
    fetchHistory()
  }
})

// 开始检测
const startCheck = async () => {
  // 检查是否登录
  const userInfo = localStorage.getItem('userInfo')
  if (!userInfo) {
    alert('请先登录后使用此功能')
    router.push('/user')
    return
  }

  if (!inputText.value) {
    alert('请输入要检测的内容')
    return
  }

  // 检查输入长度
  if (inputText.value.length > 120) {
    alert('输入字符长度不要超过120哦')
    return
  }

  loading.value = true
  try {
    const userData = JSON.parse(userInfo)
    // 验证用户信息格式
    if (!userData.phone || !userData.entitlements || userData.entitlements.length === 0) {
      throw new Error('用户信息不完整，请重新登录')
    }

    // 获取当前产品的ai_product_id
    const currentProduct = aiProducts.find((p: AIProduct) => p.id === 'live_check')
    if (!currentProduct) {
      throw new Error('产品配置错误')
    }

    // 查找用户是否有该产品的权限
    const activeEntitlement = userData.entitlements.find(
      (ent: any) => ent.is_active && ent.ai_product_id === currentProduct.ai_product_id
    )
    if (!activeEntitlement) {
      throw new Error('您暂无使用此功能的权限')
    }

    const response = await axios.post('http://10.7.21.239:4455/vio_word/check', {
      phone: userData.phone,
      ai_product_id: currentProduct.ai_product_id,
      input: inputText.value
    })
    
    if (response.data.code === 200) {
      checkResult.value = response.data.data.result
      
      // 更新用户信息中的daily_remaining
      const updatedUserInfo = JSON.parse(userInfo)
      const entitlementIndex = updatedUserInfo.entitlements.findIndex(
        (ent: any) => ent.entitlement_id === activeEntitlement.entitlement_id
      )
      if (entitlementIndex !== -1) {
        updatedUserInfo.entitlements[entitlementIndex].daily_remaining = 
          response.data.data.daily_remaining
        localStorage.setItem('userInfo', JSON.stringify(updatedUserInfo))
      }
    } else if (response.data.code === 403) {
      // 处理权限不足的情况
      if (response.data.message === '暂无权益') {
        alert('您暂无使用此功能的权限，请联系管理员')
      } else if (response.data.message === '使用额度不足') {
        alert('今日使用额度已用完，请明天再试')
      } else {
        alert(response.data.message || '权限不足')
      }
    } else {
      throw new Error(response.data.message || '检测失败')
    }
  } catch (error: any) {
    console.error('检测失败:', error)
    if (error.message === '用户信息不完整，请重新登录' || 
        error.message === '您暂无使用此功能的权限' ||
        error.message === '产品配置错误') {
      alert(error.message)
      router.push('/user')
    } else {
      alert(error.response?.data?.message || '检测失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.pb-16 {
  padding-bottom: 4rem;
}
</style>
