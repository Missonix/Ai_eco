import axios from 'axios'

const BASE_URL = 'http://10.7.21.239:4455'

export interface Order {
  order_id: string
  phone: string
  course_id: string
  purchase_time: string
  is_refund: boolean
  is_generate: boolean
  created_at: string
}

export interface CreateOrderRequest {
  order_id: string
  phone: string
  course_name: string
  purchase_time: string
  is_refund: string
}

export interface UpdateOrderRequest {
  is_refund: string
}

export interface SearchOrderRequest {
  order_id?: string
  phone?: string
  course_id?: string
  purchase_time?: string
  is_refund?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const orderApi = {
  // 创建订单
  createOrder(data: CreateOrderRequest) {
    return axios.post(`${BASE_URL}/orders`, data)
  },

  // 更新订单
  updateOrder(orderId: string, data: UpdateOrderRequest) {
    return axios.patch(`${BASE_URL}/orders/${orderId}`, data)
  },

  // 获取所有订单
  getAllOrders(page: number = 1, pageSize: number = 10) {
    return axios.get<{ code: number; message: string; data: PaginatedResponse<Order> }>(
      `${BASE_URL}/orders?page=${page}&page_size=${pageSize}`,
    )
  },

  // 获取单个订单
  getOrder(orderId: string) {
    return axios.get(`${BASE_URL}/orders/${orderId}`)
  },

  // 搜索订单
  searchOrder(data: SearchOrderRequest) {
    return axios.post(`${BASE_URL}/orders/search`, data)
  },

  // 删除订单
  deleteOrder(orderId: string) {
    return axios.delete(`${BASE_URL}/orders/${orderId}`)
  },

  // 生成用户权益
  generateEntitlement(orderId: string) {
    return axios.get(`${BASE_URL}/user_entitlements/generate/${orderId}`)
  },

  // 批量上传订单
  uploadOrders(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return axios.post(`${BASE_URL}/orders/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}
