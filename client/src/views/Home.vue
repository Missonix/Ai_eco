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
              {{ checkResult.is_Violations }}
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
              checkResult.optimization1,
              checkResult.optimization2,
              checkResult.optimization3
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

    <!-- 免责声明 -->
    <footer class="mt-8 text-xs text-gray-400 text-center px-4">
      提示：当前检测依据为平台过往违规话术特征库，因政策动态调整可能存在偏差，最终违规判定请以官方审核结果为准，本工具结果仅作学习参考。
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const inputText = ref('')
const loading = ref(false)
const checkResult = ref(null)

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

  loading.value = true
  try {
    const { user_id } = JSON.parse(userInfo)
    const response = await axios.post('http://10.7.21.239:4455/vio_word/check', {
      input: inputText.value,
      user_id: user_id
    })
    
    if (response.data.code === 200) {
      checkResult.value = response.data.data.result
      
      // 更新本地存储的使用次数
      const storedUserInfo = JSON.parse(userInfo)
      storedUserInfo.usage_count = response.data.data.usage_count
      localStorage.setItem('userInfo', JSON.stringify(storedUserInfo))
    } else if (response.data.code === 403) {
      // 使用次数不足的处理
      alert(response.data.message)
      router.push('/user') // 跳转到用户页面查看剩余次数
    } else {
      throw new Error(response.data.message || '检测失败')
    }
  } catch (error) {
    console.error('检测失败:', error)
    if (error.response?.data?.code === 403) {
      alert('使用次数不足')
      router.push('/user')
    } else {
      alert('检测失败，请稍后重试')
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
