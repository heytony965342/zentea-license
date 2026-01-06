<script setup lang="ts">
/**
 * 我的订单页面 - 深色主题版
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { portalApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

interface Order {
  id: number
  order_no: string
  plan_type: string
  amount: number
  status: string
  created_at: string
  paid_at: string | null
}

const orders = ref<Order[]>([])
const loading = ref(false)

const planTypeMap: Record<string, { name: string; icon: string }> = {
  monthly: { name: '月度版', icon: '📅' },
  yearly: { name: '年度版', icon: '⭐' },
  lifetime: { name: '终身版', icon: '👑' },
  trial: { name: '试用版', icon: '🌱' },
}

const statusMap: Record<string, { label: string; class: string; icon: string }> = {
  pending: { label: '待支付', class: 'status-pending', icon: '⏳' },
  paid: { label: '已支付', class: 'status-paid', icon: '✅' },
  cancelled: { label: '已取消', class: 'status-cancelled', icon: '❌' },
  refunded: { label: '已退款', class: 'status-refunded', icon: '↩️' },
}

// 粒子动画
const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationId: number | null = null

const initParticles = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  resize()
  window.addEventListener('resize', resize)
  
  interface Particle {
    x: number; y: number; size: number
    speedX: number; speedY: number; opacity: number
  }
  
  const particles: Particle[] = []
  for (let i = 0; i < 30; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 2 + 1,
      speedX: (Math.random() - 0.5) * 0.2,
      speedY: (Math.random() - 0.5) * 0.2,
      opacity: Math.random() * 0.2 + 0.05,
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    particles.forEach(p => {
      p.x += p.speedX
      p.y += p.speedY
      if (p.x < 0) p.x = canvas.width
      if (p.x > canvas.width) p.x = 0
      if (p.y < 0) p.y = canvas.height
      if (p.y > canvas.height) p.y = 0
      
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(74, 222, 128, ${p.opacity})`
      ctx.fill()
    })
    animationId = requestAnimationFrame(animate)
  }
  animate()
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await portalApi.getMyOrders()
    if (res.code === 200) {
      orders.value = res.data || []
    }
  } catch (e) {
    orders.value = []
  } finally {
    loading.value = false
  }
}

const continuePay = (order: Order) => {
  router.push(`/checkout?order_id=${order.id}`)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPrice = (amount: number) => {
  return amount > 0 ? `¥${amount.toFixed(2)}` : '免费'
}

const handleLogout = () => {
  userStore.logout()
  router.push('/')
}

onMounted(() => {
  initParticles()
  loadData()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<template>
  <div class="orders-page">
    <!-- 背景粒子 -->
    <canvas ref="canvasRef" class="particles-bg"></canvas>
    
    <!-- 顶部导航 -->
    <header class="nav">
      <div class="nav-content">
        <div class="logo" @click="router.push('/')">🍃 茗管家</div>
        <nav class="nav-links">
          <router-link to="/dashboard">控制台</router-link>
          <router-link to="/licenses">我的授权</router-link>
          <router-link to="/orders" class="active">我的订单</router-link>
          <router-link to="/pricing">购买</router-link>
        </nav>
        <div class="nav-user">
          <span class="user-name">{{ userStore.user?.company_name || userStore.user?.username }}</span>
          <button class="btn-logout" @click="handleLogout">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            退出
          </button>
        </div>
      </div>
    </header>

    <main class="content">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="header-text">
          <h1>
            <span class="page-icon">📋</span>
            我的订单
          </h1>
          <p>查看和管理您的所有订单记录</p>
        </div>
        <button class="btn-buy" @click="router.push('/pricing')">
          <span class="btn-icon">✨</span>
          购买授权
        </button>
      </div>

      <!-- 订单列表 -->
      <div class="orders-container">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>
        
        <div v-else-if="orders.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <h3>暂无订单</h3>
          <p>购买授权后，您的订单将显示在这里</p>
          <button class="btn-primary" @click="router.push('/pricing')">
            立即购买
          </button>
        </div>
        
        <div v-else class="orders-list">
          <div 
            v-for="order in orders" 
            :key="order.id" 
            class="order-card"
          >
            <!-- 订单头部 -->
            <div class="order-header">
              <div class="order-info">
                <span class="order-no">{{ order.order_no }}</span>
                <span :class="['order-status', statusMap[order.status]?.class]">
                  <span class="status-icon">{{ statusMap[order.status]?.icon }}</span>
                  {{ statusMap[order.status]?.label || order.status }}
                </span>
              </div>
              <div class="order-price" :class="{ free: order.amount === 0 }">
                {{ formatPrice(order.amount) }}
              </div>
            </div>
            
            <!-- 订单内容 -->
            <div class="order-body">
              <div class="plan-info">
                <span class="plan-icon">{{ planTypeMap[order.plan_type]?.icon || '📦' }}</span>
                <span class="plan-name">{{ planTypeMap[order.plan_type]?.name || order.plan_type }}</span>
              </div>
              
              <div class="order-dates">
                <div class="date-item">
                  <span class="date-label">创建时间</span>
                  <span class="date-value">{{ formatDate(order.created_at) }}</span>
                </div>
                <div v-if="order.paid_at" class="date-item">
                  <span class="date-label">支付时间</span>
                  <span class="date-value">{{ formatDate(order.paid_at) }}</span>
                </div>
              </div>
            </div>
            
            <!-- 订单操作 -->
            <div v-if="order.status === 'pending' && order.amount > 0" class="order-footer">
              <button class="btn-pay" @click="continuePay(order)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
                  <line x1="1" y1="10" x2="23" y2="10"/>
                </svg>
                去支付
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 订单说明 -->
      <div class="order-tips">
        <h3>
          <span class="tips-icon">💡</span>
          订单说明
        </h3>
        <ul>
          <li>订单创建后请在 <strong>24小时</strong> 内完成支付，超时订单将自动取消</li>
          <li>支付成功后，系统将自动生成授权码并发送至您的邮箱</li>
          <li>如需退款，请联系客服处理（已激活的授权不支持退款）</li>
          <li>发票开具请联系客服，提供订单号和开票信息</li>
        </ul>
      </div>
    </main>
    
    <!-- 页脚 -->
    <footer class="footer">
      <p>© 2025 茗管家 ZenTea ERP. All rights reserved.</p>
    </footer>
  </div>
</template>

<style scoped>
/* ========== 基础变量 ========== */
.orders-page {
  --bg-primary: #0a0f0d;
  --bg-secondary: #0d1512;
  --bg-card: rgba(255, 255, 255, 0.03);
  --border-color: rgba(255, 255, 255, 0.08);
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-muted: rgba(255, 255, 255, 0.5);
  --accent-green: #4ade80;
  --accent-cyan: #22d3ee;
  --accent-gold: #fbbf24;
  
  min-height: 100vh;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, #0a1a14 100%);
  color: var(--text-primary);
  position: relative;
}

/* ========== 背景粒子 ========== */
.particles-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

/* ========== 导航栏 ========== */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 70px;
  background: rgba(10, 15, 13, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  z-index: 100;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo:hover {
  opacity: 0.8;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-links a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-links a:hover,
.nav-links a.active {
  color: var(--accent-green);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  font-size: 14px;
  color: var(--text-secondary);
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout svg {
  width: 16px;
  height: 16px;
}

.btn-logout:hover {
  border-color: #f87171;
  color: #f87171;
}

/* ========== 主内容区 ========== */
.content {
  max-width: 900px;
  margin: 0 auto;
  padding: 110px 24px 60px;
  position: relative;
  z-index: 1;
}

/* ========== 页面标题 ========== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-text h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-icon {
  font-size: 32px;
}

.header-text p {
  color: var(--text-muted);
  font-size: 14px;
  margin: 0;
}

.btn-buy {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #059669, #10b981);
  border: none;
  color: white;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.btn-buy:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5);
}

.btn-icon {
  font-size: 16px;
}

/* ========== 订单容器 ========== */
.orders-container {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 32px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px 0;
  color: var(--text-muted);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(74, 222, 128, 0.2);
  border-top-color: var(--accent-green);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  margin: 0 0 8px;
  color: var(--text-primary);
}

.empty-state p {
  color: var(--text-muted);
  font-size: 14px;
  margin: 0 0 24px;
}

.btn-primary {
  padding: 12px 32px;
  background: linear-gradient(135deg, #059669, #10b981);
  border: none;
  color: white;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

/* ========== 订单列表 ========== */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
}

.order-card:hover {
  border-color: rgba(74, 222, 128, 0.3);
}

/* 订单头部 */
.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid var(--border-color);
}

.order-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.order-no {
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  color: var(--text-secondary);
}

.order-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-icon {
  font-size: 14px;
}

.status-pending {
  background: rgba(251, 191, 36, 0.2);
  color: var(--accent-gold);
}

.status-paid {
  background: rgba(74, 222, 128, 0.2);
  color: var(--accent-green);
}

.status-cancelled {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-muted);
}

.status-refunded {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.order-price {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent-green);
}

.order-price.free {
  color: var(--accent-cyan);
}

/* 订单内容 */
.order-body {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.plan-icon {
  font-size: 32px;
}

.plan-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.order-dates {
  display: flex;
  gap: 32px;
}

.date-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: right;
}

.date-label {
  font-size: 12px;
  color: var(--text-muted);
}

.date-value {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 订单操作 */
.order-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
}

.btn-pay {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  background: linear-gradient(135deg, #059669, #10b981);
  border: none;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-pay svg {
  width: 18px;
  height: 18px;
}

.btn-pay:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

/* ========== 订单说明 ========== */
.order-tips {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
}

.order-tips h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tips-icon {
  font-size: 20px;
}

.order-tips ul {
  margin: 0;
  padding-left: 20px;
}

.order-tips li {
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.order-tips li strong {
  color: var(--accent-gold);
}

/* ========== 页脚 ========== */
.footer {
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
  font-size: 12px;
  position: relative;
  z-index: 1;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .btn-buy {
    width: 100%;
    justify-content: center;
  }
  
  .order-header {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .order-body {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .order-dates {
    width: 100%;
    justify-content: space-around;
  }
  
  .date-item {
    text-align: center;
  }
}
</style>
