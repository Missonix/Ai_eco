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
    ai_product_id: 'AI_08b08f5b262840daac0b3c52f0d9f49a',
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