<script setup lang="ts">
/**
 * 我的授权页面 - 深色主题版
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { portalApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

interface License {
  id: number
  license_key: string
  plan_type: string
  status: string
  created_at: string
  activated_at: string | null
  expire_date: string | null
  machine_id: string | null
  max_users: number
}

const licenses = ref<License[]>([])
const loading = ref(false)
const filterStatus = ref<string>('all')

const planTypeMap: Record<string, { name: string; icon: string; color: string }> = {
  monthly: { name: '月度版', icon: '📅', color: '#4ade80' },
  yearly: { name: '年度版', icon: '⭐', color: '#22d3ee' },
  lifetime: { name: '终身版', icon: '👑', color: '#fbbf24' },
  trial: { name: '试用版', icon: '🌱', color: '#a78bfa' },
  promo_free: { name: '限免版', icon: '🎁', color: '#f472b6' },
  free_forever: { name: '永久免费', icon: '♾️', color: '#4ade80' },
}

const statusMap: Record<string, { label: string; class: string; icon: string }> = {
  pending: { label: '待激活', class: 'status-pending', icon: '⏳' },
  active: { label: '已激活', class: 'status-active', icon: '✅' },
  expired: { label: '已过期', class: 'status-expired', icon: '⏰' },
  revoked: { label: '已吊销', class: 'status-revoked', icon: '🚫' },
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
    const res = await portalApi.getMyLicenses()
    if (res.code === 200) {
      licenses.value = res.data || []
    }
  } catch (e) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

const filteredLicenses = computed(() => {
  if (filterStatus.value === 'all') return licenses.value
  return licenses.value.filter(l => l.status === filterStatus.value)
})

const stats = computed(() => ({
  total: licenses.value.length,
  active: licenses.value.filter(l => l.status === 'active').length,
  pending: licenses.value.filter(l => l.status === 'pending').length,
  expired: licenses.value.filter(l => l.status === 'expired').length,
}))

const formatDate = (date: string | null) => {
  if (!date) return '永久'
  return new Date(date).toLocaleDateString('zh-CN')
}

const copyLicenseKey = (key: string) => {
  navigator.clipboard.writeText(key)
  message.success('授权码已复制')
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
  <div class="licenses-page">
    <!-- 背景粒子 -->
    <canvas ref="canvasRef" class="particles-bg"></canvas>
    
    <!-- 顶部导航 -->
    <header class="nav">
      <div class="nav-content">
        <div class="logo" @click="router.push('/')">🍃 茗管家</div>
        <nav class="nav-links">
          <router-link to="/dashboard">控制台</router-link>
          <router-link to="/licenses" class="active">我的授权</router-link>
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
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="header-text">
          <h1>
            <span class="page-icon">🔑</span>
            我的授权
          </h1>
          <p>查看和管理您的所有软件授权</p>
        </div>
        <button class="btn-buy" @click="router.push('/pricing')">
          <span class="btn-icon">✨</span>
          购买新授权
        </button>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div 
          class="stat-card" 
          :class="{ active: filterStatus === 'all' }"
          @click="filterStatus = 'all'"
        >
          <span class="stat-icon">📊</span>
          <span class="stat-value">{{ stats.total }}</span>
          <span class="stat-label">全部授权</span>
        </div>
        <div 
          class="stat-card success" 
          :class="{ active: filterStatus === 'active' }"
          @click="filterStatus = 'active'"
        >
          <span class="stat-icon">✅</span>
          <span class="stat-value">{{ stats.active }}</span>
          <span class="stat-label">已激活</span>
        </div>
        <div 
          class="stat-card warning" 
          :class="{ active: filterStatus === 'pending' }"
          @click="filterStatus = 'pending'"
        >
          <span class="stat-icon">⏳</span>
          <span class="stat-value">{{ stats.pending }}</span>
          <span class="stat-label">待激活</span>
        </div>
        <div 
          class="stat-card danger" 
          :class="{ active: filterStatus === 'expired' }"
          @click="filterStatus = 'expired'"
        >
          <span class="stat-icon">⏰</span>
          <span class="stat-value">{{ stats.expired }}</span>
          <span class="stat-label">已过期</span>
        </div>
      </div>

      <!-- 授权列表 -->
      <div class="licenses-container">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>
        
        <div v-else-if="filteredLicenses.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <h3>{{ filterStatus === 'all' ? '暂无授权' : '暂无符合条件的授权' }}</h3>
          <p v-if="filterStatus === 'all'">购买授权后，您的授权信息将显示在这里</p>
          <p v-else>切换筛选条件查看其他授权</p>
          <button v-if="filterStatus === 'all'" class="btn-primary" @click="router.push('/pricing')">
            立即购买
          </button>
          <button v-else class="btn-secondary" @click="filterStatus = 'all'">
            查看全部
          </button>
        </div>
        
        <div v-else class="licenses-grid">
          <div 
            v-for="lic in filteredLicenses" 
            :key="lic.id" 
            class="license-card"
            :class="[statusMap[lic.status]?.class]"
          >
            <!-- 授权头部 -->
            <div class="license-header">
              <div class="plan-badge">
                <span class="plan-icon">{{ planTypeMap[lic.plan_type]?.icon || '📄' }}</span>
                <span class="plan-name">{{ planTypeMap[lic.plan_type]?.name || lic.plan_type }}</span>
              </div>
              <span :class="['license-status', statusMap[lic.status]?.class]">
                <span class="status-icon">{{ statusMap[lic.status]?.icon }}</span>
                {{ statusMap[lic.status]?.label || lic.status }}
              </span>
            </div>
            
            <!-- 授权码 -->
            <div class="license-key-section">
              <label>授权码</label>
              <div class="license-key">
                <code>{{ lic.license_key }}</code>
                <button 
                  class="btn-copy" 
                  @click="copyLicenseKey(lic.license_key)"
                  title="复制授权码"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                  </svg>
                </button>
              </div>
            </div>
            
            <!-- 授权详情 -->
            <div class="license-details">
              <div class="detail-item">
                <span class="detail-label">到期时间</span>
                <span class="detail-value">{{ formatDate(lic.expire_date) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">最大用户数</span>
                <span class="detail-value">{{ lic.max_users }} 人</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">设备绑定</span>
                <span class="detail-value" :class="{ bound: lic.machine_id }">
                  {{ lic.machine_id ? '已绑定' : '未绑定' }}
                </span>
              </div>
              <div v-if="lic.activated_at" class="detail-item">
                <span class="detail-label">激活时间</span>
                <span class="detail-value">{{ formatDate(lic.activated_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 使用说明 -->
      <div class="usage-guide">
        <h3>
          <span class="guide-icon">📚</span>
          使用说明
        </h3>
        <div class="guide-steps">
          <div class="step">
            <div class="step-num">1</div>
            <div class="step-content">
              <h4>复制授权码</h4>
              <p>点击授权码旁边的复制按钮</p>
            </div>
          </div>
          <div class="step">
            <div class="step-num">2</div>
            <div class="step-content">
              <h4>打开软件</h4>
              <p>启动茗管家 ERP 软件</p>
            </div>
          </div>
          <div class="step">
            <div class="step-num">3</div>
            <div class="step-content">
              <h4>激活授权</h4>
              <p>进入「系统设置」→「授权管理」，粘贴授权码并激活</p>
            </div>
          </div>
        </div>
        
        <div class="guide-notes">
          <p>⚠️ 每个授权码只能绑定一台设备，如需更换设备请联系客服</p>
          <p>📧 授权到期前系统会通过邮件提醒您续费</p>
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
.licenses-page {
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
  max-width: 1100px;
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

/* ========== 统计卡片 ========== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  border-color: rgba(74, 222, 128, 0.3);
  transform: translateY(-2px);
}

.stat-card.active {
  border-color: var(--accent-green);
  background: rgba(74, 222, 128, 0.1);
}

.stat-card.success.active {
  border-color: var(--accent-green);
  background: rgba(74, 222, 128, 0.1);
}

.stat-card.warning.active {
  border-color: var(--accent-gold);
  background: rgba(251, 191, 36, 0.1);
}

.stat-card.danger.active {
  border-color: #f87171;
  background: rgba(248, 113, 113, 0.1);
}

.stat-icon {
  font-size: 28px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
}

/* ========== 授权容器 ========== */
.licenses-container {
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

.btn-secondary {
  padding: 12px 32px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  border-color: var(--accent-green);
  color: var(--accent-green);
}

/* ========== 授权网格 ========== */
.licenses-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.license-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
}

.license-card:hover {
  border-color: rgba(74, 222, 128, 0.3);
  transform: translateY(-4px);
}

.license-card.status-active {
  border-left: 3px solid var(--accent-green);
}

.license-card.status-pending {
  border-left: 3px solid var(--accent-gold);
}

.license-card.status-expired,
.license-card.status-revoked {
  border-left: 3px solid #f87171;
}

/* 授权头部 */
.license-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.plan-badge {
  display: flex;
  align-items: center;
  gap: 10px;
}

.plan-icon {
  font-size: 28px;
}

.plan-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.license-status {
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

/* 授权码区域 */
.license-key-section {
  margin-bottom: 20px;
}

.license-key-section label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.license-key {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.license-key code {
  flex: 1;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  color: var(--accent-cyan);
  word-break: break-all;
}

.btn-copy {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.3);
  border-radius: 6px;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-copy svg {
  width: 16px;
  height: 16px;
  color: var(--accent-green);
}

.btn-copy:hover {
  background: rgba(74, 222, 128, 0.2);
}

/* 授权详情 */
.license-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: var(--text-muted);
}

.detail-value {
  font-size: 14px;
  color: var(--text-secondary);
}

.detail-value.bound {
  color: var(--accent-green);
}

/* ========== 使用说明 ========== */
.usage-guide {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
}

.usage-guide h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 24px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.guide-icon {
  font-size: 24px;
}

.guide-steps {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.step {
  flex: 1;
  display: flex;
  gap: 16px;
}

.step-num {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #059669, #10b981);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--text-primary);
}

.step-content p {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.guide-notes {
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.guide-notes p {
  font-size: 13px;
  color: var(--text-muted);
  margin: 8px 0;
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
  .licenses-grid {
    grid-template-columns: 1fr;
  }
}

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
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .license-details {
    grid-template-columns: 1fr;
  }
  
  .guide-steps {
    flex-direction: column;
  }
}
</style>
