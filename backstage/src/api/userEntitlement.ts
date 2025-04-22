import axios from 'axios'

const BASE_URL = 'http://10.7.21.239:4455'

export interface UserEntitlement {
  entitlement_id: string
  phone: string
  rule_id: string
  course_name: string
  product_name: string
  ai_product_id: string
  start_date: string
  end_date: string
  created_at: string
  daily_remaining: number
  is_active: boolean
}

export interface CreateUserEntitlementRequest {
  phone: string
  rule_id: string
}

export interface UpdateUserEntitlementRequest {
  phone?: string
  rule_id?: string
  end_date?: string
  daily_remaining?: number
}

export interface SearchUserEntitlementRequest {
  entitlement_id?: string
  phone?: string
  rule_id?: string
  course_name?: string
  product_name?: string
  start_date?: string
  end_date?: string
  daily_remaining?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const userEntitlementApi = {
  // 创建用户权益
  createEntitlement(data: CreateUserEntitlementRequest) {
    return axios.post(`${BASE_URL}/user_entitlements`, data)
  },

  // 更新用户权益
  updateEntitlement(entitlementId: string, data: UpdateUserEntitlementRequest) {
    return axios.patch(`${BASE_URL}/user_entitlements/${entitlementId}`, data)
  },

  // 获取所有用户权益
  getAllEntitlements(page: number = 1, pageSize: number = 10) {
    return axios.get<{ code: number; message: string; data: PaginatedResponse<UserEntitlement> }>(
      `${BASE_URL}/user_entitlements?page=${page}&page_size=${pageSize}`,
    )
  },

  // 获取单个用户权益
  getEntitlement(entitlementId: string) {
    return axios.get(`${BASE_URL}/user_entitlements/${entitlementId}`)
  },

  // 搜索用户权益
  searchEntitlement(data: SearchUserEntitlementRequest) {
    return axios.post(`${BASE_URL}/user_entitlements/search`, data)
  },

  // 删除用户权益
  deleteEntitlement(entitlementId: string) {
    return axios.delete(`${BASE_URL}/user_entitlements/${entitlementId}`)
  },
}
