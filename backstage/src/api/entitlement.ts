import axios from 'axios'

const BASE_URL = 'http://10.7.21.239:4455'

export interface EntitlementRule {
  rule_id: string
  course_id: string
  course_name: string
  ai_product_id: string
  product_name: string
  daily_limit: number
  validity_days: number
  created_at: string
}

export interface CreateEntitlementRuleRequest {
  course_id: string
  ai_product_id: string
}

export interface UpdateEntitlementRuleRequest {
  ai_product_id?: string
  daily_limit?: number
  validity_days?: number
}

export interface SearchEntitlementRuleRequest {
  rule_id?: string
  course_id?: string
  ai_product_id?: string
  daily_limit?: number
  validity_days?: number
}

export const entitlementApi = {
  // 创建权益规则
  createRule(data: CreateEntitlementRuleRequest) {
    return axios.post(`${BASE_URL}/entitlement_rules`, data)
  },

  // 更新权益规则
  updateRule(ruleId: string, data: UpdateEntitlementRuleRequest) {
    return axios.patch(`${BASE_URL}/entitlement_rules/${ruleId}`, data)
  },

  // 获取所有权益规则
  getAllRules() {
    return axios.get<{ code: number; message: string; data: EntitlementRule[] }>(
      `${BASE_URL}/entitlement_rules`,
    )
  },

  // 获取单个权益规则
  getRule(ruleId: string) {
    return axios.get(`${BASE_URL}/entitlement_rules/${ruleId}`)
  },

  // 搜索权益规则
  searchRule(data: SearchEntitlementRuleRequest) {
    return axios.post(`${BASE_URL}/entitlement_rules/search`, data)
  },

  // 删除权益规则
  deleteRule(ruleId: string) {
    return axios.delete(`${BASE_URL}/entitlement_rules/${ruleId}`)
  },
}
