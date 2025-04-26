import axios from 'axios'

const BASE_URL = 'http://10.7.21.239:4455'

export interface Course {
  course_id: string
  course_name: string
  created_at: string
  updated_at: string
}

export interface CreateCourseRequest {
  course_name: string
}

export interface UpdateCourseRequest {
  course_name: string
}

export interface SearchCourseRequest {
  course_name?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface SearchCourseResponse {
  code: number
  message: string
  data: {
    items: Course[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }
}

export const courseApi = {
  // 创建课程
  createCourse: (data: { course_name: string }) => {
    return axios.post(`${BASE_URL}/courses`, data)
  },

  // 更新课程
  updateCourse: (courseId: string, data: { course_name: string }) => {
    return axios.put(`${BASE_URL}/courses/${courseId}`, data)
  },

  // 获取所有课程
  getAllCourses: (page: number, pageSize: number) => {
    return axios.get(`${BASE_URL}/courses`, {
      params: {
        page,
        page_size: pageSize,
      },
    })
  },

  // 获取单个课程
  getCourse: (courseId: string) => {
    return axios.get(`${BASE_URL}/courses/${courseId}`)
  },

  // 通过课程名称模糊搜索课程
  searchCourse: (course_name_prefix: string) => {
    return axios.post<SearchCourseResponse>(`${BASE_URL}/courses/search`, {
      course_name_prefix,
    })
  },

  // 删除课程
  deleteCourse: (courseId: string) => {
    return axios.delete(`${BASE_URL}/courses/${courseId}`)
  },
}
