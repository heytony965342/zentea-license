<script setup lang="ts">
/**
 * 用户控制台 - 深色主题版
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { portalApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

interface License {
  id: number
  license_key: string
  plan_type: string
  status: string
  expire_date: string | null
}

const licenses = ref<License[]>([])
const loading = ref(false)

const planTypeMap: Record<string, { name: string; icon: string; color: string }> = {
  monthly: { name: '月度版', icon: '📅', color: '#4ade80' },
  yearly: { name: '年度版', icon: '⭐', color: '#22d3ee' },
  lifetime: { name: '终身版', icon: '👑', color: '#fbbf24' },
  trial: { name: '试用版', icon: '🌱', color: '#a78bfa' },
  promo_free: { name: '限免版', icon: '🎁', color: '#f472b6' },
  free_forever: { name: '永久免费', icon: '♾️', color: '#4ade80' },
}

const statusMap: Record<string, { label: string; class: string }> = {
  pending: { label: '待激活', class: 'status-pending' },
  active: { label: '有效', class: 'status-active' },
  expired: { label: '已过期', class: 'status-expired' },
  revoked: { label: '已吊销', class: 'status-revoked' },
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
  for (let i = 0; i < 35; i++) {
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

const loadLicenses = async () => {
  loading.value = true
  try {
    const res = await portalApi.getMyLicenses()
    if (res.code === 200) {
      licenses.value = res.data || []
    }
  } catch (e) {
    // ignore
  } finally {
    loading.value = false
  }
}

const activeLicenses = computed(() => licenses.value.filter(l => l.status === 'active'))
const pendingLicenses = computed(() => licenses.value.filter(l => l.status === 'pending'))

const formatDate = (date: string | null) => {
  if (!date) return '永久'
  return new Date(date).toLocaleDateString('zh-CN')
}

const handleLogout = () => {
  userStore.logout()
  router.push('/')
}

onMounted(() => {
  initParticles()
  loadLicenses()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<template>
  <div class="dashboard-page">
    <!-- 背景粒子 -->
    <canvas ref="canvasRef" class="particles-bg"></canvas>
    
    <!-- 顶部导航 -->
    <header class="nav">
      <div class="nav-content">
        <div class="logo" @click="router.push('/')">🍃 茗管家</div>
        <nav class="nav-links">
          <router-link to="/dashboard" class="active">控制台</router-link>
          <router-link to="/licenses">我的授权</router-link>
          <router-link to="/orders">我的订单</router-link>
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
      <!-- 欢迎区 -->
      <div class="welcome-section">
        <div class="welcome-text">
          <span class="welcome-tag">👋 欢迎回来</span>
          <h1>{{ userStore.user?.company_name || userStore.user?.username }}</h1>
          <p>在这里管理您的茗管家 ERP 授权</p>
        </div>
        <button class="btn-buy" @click="router.push('/pricing')">
          <span class="btn-icon">✨</span>
          购买新授权
        </button>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card active-card">
          <div class="stat-icon">🔑</div>
          <div class="stat-info">
            <span class="stat-value">{{ activeLicenses.length }}</span>
            <span class="stat-label">有效授权</span>
          </div>
          <div class="stat-glow"></div>
        </div>
        
        <div class="stat-card pending-card">
          <div class="stat-icon">⏳</div>
          <div class="stat-info">
            <span class="stat-value">{{ pendingLicenses.length }}</span>
            <span class="stat-label">待激活</span>
          </div>
        </div>
        
        <div class="stat-card total-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <span class="stat-value">{{ licenses.length }}</span>
            <span class="stat-label">全部授权</span>
          </div>
        </div>
      </div>

      <!-- 最近授权 -->
      <div class="recent-section">
        <div class="section-header">
          <h2>
            <span class="section-icon">📜</span>
            最近授权
          </h2>
          <button class="btn-view-all" @click="router.push('/licenses')">
            查看全部
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>
        
        <div v-else-if="licenses.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <h3>暂无授权</h3>
          <p>购买授权后，您可以在这里管理所有授权</p>
          <button class="btn-primary" @click="router.push('/pricing')">
            立即购买
          </button>
        </div>
        
        <div v-else class="license-list">
          <div 
            v-for="lic in licenses.slice(0, 4)" 
            :key="lic.id" 
            class="license-card"
          >
            <div class="license-header">
              <span class="plan-icon">{{ planTypeMap[lic.plan_type]?.icon || '📄' }}</span>
              <span class="plan-name">{{ planTypeMap[lic.plan_type]?.name || lic.plan_type }}</span>
              <span :class="['license-status', statusMap[lic.status]?.class]">
                {{ statusMap[lic.status]?.label || lic.status }}
              </span>
            </div>
            <div class="license-key">
              <code>{{ lic.license_key }}</code>
              <button 
                class="btn-copy" 
                @click="navigator.clipboard.writeText(lic.license_key)"
                title="复制授权码"
              >
                📋
              </button>
            </div>
            <div class="license-footer">
              <span class="expire-label">到期时间</span>
              <span class="expire-date">{{ formatDate(lic.expire_date) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="quick-actions">
        <h2>
          <span class="section-icon">⚡</span>
          快捷操作
        </h2>
        <div class="actions-grid">
          <div class="action-card" @click="router.push('/licenses')">
            <span class="action-icon">🔑</span>
            <span class="action-title">授权管理</span>
            <span class="action-desc">查看和管理您的所有授权</span>
          </div>
          <div class="action-card" @click="router.push('/orders')">
            <span class="action-icon">📋</span>
            <span class="action-title">订单记录</span>
            <span class="action-desc">查看历史订单和支付状态</span>
          </div>
          <div class="action-card" @click="router.push('/pricing')">
            <span class="action-icon">💎</span>
            <span class="action-title">升级方案</span>
            <span class="action-desc">探索更多授权方案</span>
          </div>
          <div class="action-card" @click="router.push('/docs')">
            <span class="action-icon">📚</span>
            <span class="action-title">使用文档</span>
            <span class="action-desc">了解如何使用茗管家</span>
          </div>
        </div>
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
.dashboard-page {
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 110px 24px 60px;
  position: relative;
  z-index: 1;
}

/* ========== 欢迎区 ========== */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.welcome-tag {
  display: inline-block;
  padding: 6px 14px;
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.3);
  border-radius: 20px;
  font-size: 13px;
  color: var(--accent-green);
  margin-bottom: 12px;
}

.welcome-text h1 {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 8px;
  background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-text p {
  color: var(--text-muted);
  font-size: 15px;
  margin: 0;
}

.btn-buy {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #059669, #10b981);
  border: none;
  color: white;
  border-radius: 12px;
  font-size: 15px;
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
  font-size: 18px;
}

/* ========== 统计卡片 ========== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 40px;
}

.stat-card {
  position: relative;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  overflow: hidden;
  transition: all 0.3s;
}

.stat-card:hover {
  border-color: rgba(74, 222, 128, 0.3);
  transform: translateY(-4px);
}

.stat-card.active-card {
  background: linear-gradient(135deg, rgba(74, 222, 128, 0.1), rgba(34, 211, 238, 0.05));
  border-color: rgba(74, 222, 128, 0.3);
}

.stat-glow {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(74, 222, 128, 0.15) 0%, transparent 70%);
  pointer-events: none;
}

.stat-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
}

.active-card .stat-value {
  background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 14px;
  color: var(--text-muted);
}

/* ========== 最近授权区 ========== */
.recent-section {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.section-icon {
  font-size: 24px;
}

.btn-view-all {
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

.btn-view-all svg {
  width: 16px;
  height: 16px;
}

.btn-view-all:hover {
  border-color: var(--accent-green);
  color: var(--accent-green);
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 60px 0;
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
  padding: 60px 20px;
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

/* 授权列表 */
.license-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.license-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s;
}

.license-card:hover {
  border-color: rgba(74, 222, 128, 0.3);
  background: rgba(74, 222, 128, 0.03);
}

.license-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.plan-icon {
  font-size: 24px;
}

.plan-name {
  flex: 1;
  font-weight: 600;
  color: var(--text-primary);
}

.license-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-active {
  background: rgba(74, 222, 128, 0.2);
  color: var(--accent-green);
}

.status-pending {
  background: rgba(251, 191, 36, 0.2);
  color: var(--accent-gold);
}

.status-expired,
.status-revoked {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.license-key {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin-bottom: 16px;
}

.license-key code {
  flex: 1;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  color: var(--accent-cyan);
  word-break: break-all;
}

.btn-copy {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.btn-copy:hover {
  opacity: 1;
}

.license-footer {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.expire-label {
  color: var(--text-muted);
}

.expire-date {
  color: var(--text-secondary);
}

/* ========== 快捷操作 ========== */
.quick-actions {
  margin-bottom: 40px;
}

.quick-actions h2 {
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 20px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-card:hover {
  border-color: rgba(74, 222, 128, 0.3);
  background: rgba(74, 222, 128, 0.05);
  transform: translateY(-4px);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.action-desc {
  font-size: 13px;
  color: var(--text-muted);
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
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .license-list {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  
  .welcome-section {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .welcome-text h1 {
    font-size: 28px;
  }
  
  .btn-buy {
    width: 100%;
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
}
</style>
