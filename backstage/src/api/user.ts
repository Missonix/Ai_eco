import axios from 'axios'

const BASE_URL = 'http://10.7.21.239:4455/api'

export interface User {
  user_id: string
  phone: string
  password: string
  is_deleted: boolean
  last_login: string | null
  created_at: string
  updated_at: string
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
  createUser(data: CreateUserRequest) {
    return axios.post(`${BASE_URL}/users`, data)
  },

  // 更新用户
  updateUser(userId: string, data: UpdateUserRequest) {
    return axios.patch(`${BASE_URL}/users/${userId}`, data)
  },

  // 获取所有用户
  getAllUsers() {
    return axios.get(`${BASE_URL}/users`)
  },

  // 获取单个用户
  getUser(userId: string) {
    return axios.get(`${BASE_URL}/users/${userId}`)
  },

  // 通过手机号搜索用户
  searchUserByPhone(phone: string) {
    return axios.get(`${BASE_URL}/users/phone/${phone}`)
  },

  // 删除用户
  deleteUser(userId: string) {
    return axios.delete(`${BASE_URL}/users/${userId}`)
  },

  // 获取token
  getToken(userId: string) {
    return axios.get(`${BASE_URL}/users/token/${userId}`)
  },
}
