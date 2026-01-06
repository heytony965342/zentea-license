import axios from 'axios'

const instance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export const request = {
  async get<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
    return instance.get(url, { params })
  },
  async post<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    return instance.post(url, data)
  },
  async put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    return instance.put(url, data)
  },
  async delete<T = any>(url: string): Promise<ApiResponse<T>> {
    return instance.delete(url)
  },
}

