import Home from '@/views/Home.vue'
import type { Component } from 'vue'

export interface AIProduct {
  id: string
  name: string
  description: string
  rule_id: string
  component: Component
}

export const aiProducts: AIProduct[] = [
  {
    id: 'live_check',
    name: '直播话术违规词AI检测',
    description: '智能检测直播话术中的违规内容，提供优化建议',
    rule_id: 'RULE_53586b5d02bb43259493bd37ef1dc709',
    component: Home
  },
  {
    id: 'test_product1',
    name: '测试产品1',
    description: '测试产品1的功能描述',
    rule_id: 'RULE_c4a8c19a288a4abb8a19fcecabc6b5f6',
    component: Home
  }
] 