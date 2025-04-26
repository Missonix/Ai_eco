import axios from 'axios'

const BASE_URL = 'http://10.7.21.239:4455'

export interface AIProduct {
  ai_product_id: string
  ai_product_name: string
  created_at: string
}

export interface CreateAIProductRequest {
  ai_product_name: string
}

export interface UpdateAIProductRequest {
  ai_product_name: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface SearchProductResponse {
  code: number
  message: string
  data: {
    items: AIProduct[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }
}

export const productApi = {
  // 创建产品
  createProduct: (data: CreateAIProductRequest) => {
    return axios.post(`${BASE_URL}/ai_products`, data)
  },

  // 更新产品
  updateProduct: (productId: string, data: UpdateAIProductRequest) => {
    return axios.put(`${BASE_URL}/ai_products/${productId}`, data)
  },

  // 获取所有产品
  getAllProducts: (page: number, pageSize: number) => {
    return axios.get(`${BASE_URL}/ai_products`, {
      params: {
        page,
        page_size: pageSize,
      },
    })
  },

  // 获取单个产品
  getProduct: (productId: string) => {
    return axios.get(`${BASE_URL}/ai_products/${productId}`)
  },

  // 删除产品
  deleteProduct: (productId: string) => {
    return axios.delete(`${BASE_URL}/ai_products/${productId}`)
  },

  // 通过产品名称模糊搜索产品
  searchProduct: (product_name_prefix: string) => {
    return axios.post<SearchProductResponse>(`${BASE_URL}/ai_products/search`, {
      product_name_prefix,
    })
  },
}
