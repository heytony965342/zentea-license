import { request } from './request'

// 认证
export const authApi = {
  login: (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return request.post('/auth/login', formData)
  },
  getMe: () => request.get('/auth/me'),
}

// 管理后台
export const adminApi = {
  // 仪表盘
  getDashboard: () => request.get('/admin/dashboard'),
  
  // 客户
  getCustomers: (params?: { page?: number; page_size?: number }) => 
    request.get('/admin/customers', params),
  getCustomer: (id: number) => request.get(`/admin/customers/${id}`),
  
  // 授权
  getLicenses: (params?: { 
    page?: number
    page_size?: number
    status?: string
    user_id?: number 
  }) => request.get('/admin/licenses', params),
  createLicense: (data: {
    user_id: number
    plan_type: string
    expire_date?: string
    max_users?: number
    notes?: string
  }) => request.post('/admin/licenses', data),
  extendLicense: (id: number, days: number) => 
    request.post(`/admin/licenses/${id}/extend?days=${days}`),
  revokeLicense: (id: number, reason?: string) => 
    request.post(`/admin/licenses/${id}/revoke`, null, { params: { reason } }),
  unbindLicense: (id: number) => request.post(`/admin/licenses/${id}/unbind`),
}

// 促销
export const promoApi = {
  getCurrent: () => request.get('/promo/current'),
}

// 系统设置
export const settingApi = {
  // 获取所有设置
  getAll: (category?: string) => request.get('/settings', category ? { category } : {}),
  // 更新设置
  update: (settings: Record<string, string>) => request.put('/settings', { settings }),
  // 获取支付设置
  getPayment: () => request.get('/settings/payment'),
  // 获取客服联系方式
  getContact: () => request.get('/settings/contact'),
  // 获取首页配置
  getHomepage: () => request.get('/settings/homepage'),
}

// 页面管理
export const pageApi = {
  // 获取页面列表
  getList: (status?: string) => request.get('/pages', status ? { status } : {}),
  // 获取页面详情
  getDetail: (id: number) => request.get(`/pages/${id}`),
  // 创建页面
  create: (data: {
    slug: string
    title: string
    subtitle?: string
    content?: string
    meta_description?: string
    status?: string
    sort_order?: number
  }) => request.post('/pages', data),
  // 更新页面
  update: (id: number, data: {
    title?: string
    subtitle?: string
    content?: string
    meta_description?: string
    status?: string
    sort_order?: number
  }) => request.put(`/pages/${id}`, data),
  // 删除页面
  delete: (id: number) => request.delete(`/pages/${id}`),
}

