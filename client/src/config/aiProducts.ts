import Home from '@/views/Home.vue'
import type { Component } from 'vue'

export interface AIProduct {
  id: string
  name: string
  description: string
  ai_product_id: string
  component: Component
}

export const aiProducts: AIProduct[] = [
  {
    id: 'live_check',
    name: '直播话术违规词AI检测',
    description: '智能检测直播话术中的违规内容，提供优化建议',
    ai_product_id: 'AI_84d296e757de45a3bcc576260fd06c19',
    component: Home
  },
  {
    id: 'test_product1',
    name: '测试产品1',
    description: '测试产品1的功能描述',
    ai_product_id: 'AI_test_product1',
    component: Home
  }
] 