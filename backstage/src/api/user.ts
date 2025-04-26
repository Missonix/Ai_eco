import axios from 'axios'

const BASE_URL = 'http://10.7.21.239:4455'

export interface User {
  user_id: string
  phone: string
  password: string
  is_deleted: boolean
  last_login: string
  created_at: string
  updated_at: string
}

export interface SearchUserResponse {
  code: number
  message: string
  data: {
    items: User[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }
}

export interface CreateUserRequest {
  phone: string
  password: string
}

export interface UpdateUserRequest {
  password?: string
}

export const userApi = {
  // 创建用户
  createUser: (data: { phone: string; password: string }) => {
    return axios.post(`${BASE_URL}/api/users`, data)
  },

  // 更新用户
  updateUser: (userId: string, data: { phone?: string; password?: string }) => {
    return axios.put(`${BASE_URL}/api/users/${userId}`, data)
  },

  // 获取所有用户
  getAllUsers: () => {
    return axios.get(`${BASE_URL}/api/users`)
  },

  // 获取单个用户
  getUser: (userId: string) => {
    return axios.get(`${BASE_URL}/api/users/${userId}`)
  },

  // 通过手机号模糊搜索用户
  searchUserByPhone: (phone_prefix: string) => {
    return axios.post<SearchUserResponse>(`${BASE_URL}/api/users/search`, {
      phone_prefix,
    })
  },

  // 删除用户
  deleteUser: (userId: string) => {
    return axios.delete(`${BASE_URL}/api/users/${userId}`)
  },

  // 获取token
  getToken: (userId: string) => {
    return axios.get(`${BASE_URL}/api/users/token/${userId}`)
  },
}
