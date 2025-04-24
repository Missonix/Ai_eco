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
    ai_product_id: 'AI_fd1b6a1c6718494d8422e1584dee85d0',
    component: Home
  },
  {
    id: 'test_product1',
    name: '测试产品1',
    description: '测试产品1的功能描述',
    ai_product_id: 'AI_test_product1',
    component: Home
  },
  {
    id: 'test_product2',
    name: '测试产品2',
    description: '测试产品2的功能描述',
    ai_product_id: 'AI_test_product2',
    component: Home
  }
] 