import { request } from './request'

// 认证
export const authApi = {
  // 登录
  login: (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return request.post('/auth/login', formData)
  },
  // 注册
  register: (data: {
    username: string
    email: string
    password: string
    company_name?: string
    contact_name?: string
    phone?: string
  }) => request.post('/portal/register', data),
  // 获取当前用户
  getMe: () => request.get('/auth/me'),
}

// 用户门户
export const portalApi = {
  // 获取我的授权列表
  getMyLicenses: () => request.get('/portal/licenses'),
  // 激活授权
  activateLicense: (licenseKey: string, machineInfo: object) => 
    request.post('/license/activate', { license_key: licenseKey, machine_info: machineInfo }),
  // 获取套餐列表
  getPlans: () => request.get('/portal/plans'),
  // 创建订单
  createOrder: (planType: string, promoCode?: string) => 
    request.post('/orders/create', { plan_type: planType, promo_code: promoCode }),
  // 获取我的订单
  getMyOrders: () => request.get('/orders/my'),
  // 上传支付凭证
  uploadPaymentProof: (orderId: number, proofUrl: string) =>
    request.post(`/orders/${orderId}/upload-proof?proof_url=${encodeURIComponent(proofUrl)}`),
}

// 促销
export const promoApi = {
  // 获取当前促销活动
  getCurrent: () => request.get('/promo/current'),
  // 检查促销码
  checkCode: (code: string) => request.post('/promo/check', { code }),
}

// 设置（公开接口）
export const settingApi = {
  // 获取首页配置
  getHomepage: () => request.get('/settings/public/homepage'),
  // 获取联系方式
  getContact: () => request.get('/settings/public/contact'),
}

// 页面内容
export const pageApi = {
  // 获取页面详情
  getPage: (slug: string) => request.get(`/pages/public/${slug}`),
  // 获取页面菜单
  getMenu: () => request.get('/pages/public/menu'),
}

