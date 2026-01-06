<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const plans = [
  {
    name: '试用版',
    price: '免费',
    priceNum: '',
    period: '7天体验',
    description: '快速了解系统功能',
    features: ['全功能体验', '最多 2 个用户', '基础技术支持', '云端数据存储'],
    action: '免费试用',
    type: 'trial',
    tier: 'basic',
  },
  {
    name: '年度版',
    price: '¥',
    priceNum: '899',
    period: '/年',
    description: '最受欢迎的选择',
    features: ['全部功能', '最多 10 个用户', '优先技术支持', '数据自动备份', '免费版本升级', '专属客服通道'],
    action: '立即购买',
    type: 'yearly',
    recommended: true,
    tier: 'pro',
  },
  {
    name: '终身版',
    price: '¥',
    priceNum: '2999',
    period: '一次性付款',
    description: '长期投资首选',
    features: ['全部功能', '无限用户数量', '专属 VIP 支持', '永久免费更新', '优先体验新功能', '定制化服务'],
    action: '立即购买',
    type: 'lifetime',
    tier: 'premium',
  },
]

// 粒子动画
const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationId: number | null = null

interface Particle {
  x: number
  y: number
  size: number
  speedX: number
  speedY: number
  opacity: number
}

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
  
  const particles: Particle[] = []
  const particleCount = 50
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 3 + 1,
      speedX: (Math.random() - 0.5) * 0.3,
      speedY: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.3 + 0.1,
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

const handleBuy = (type: string) => {
  const token = localStorage.getItem('portal_token')
  if (token) {
    router.push(`/checkout?plan=${type}`)
  } else {
    router.push(`/register?plan=${type}`)
  }
}

onMounted(() => {
  initParticles()
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<template>
  <div class="pricing-page">
    <!-- 背景粒子 -->
    <canvas ref="canvasRef" class="particles-bg"></canvas>
    
    <!-- 顶部导航 -->
    <header class="nav">
      <div class="nav-content">
        <div class="logo" @click="router.push('/')">🍃 茗管家</div>
        <nav class="nav-links">
          <router-link to="/">首页</router-link>
          <router-link to="/features">功能介绍</router-link>
          <router-link to="/pricing" class="active">价格方案</router-link>
          <router-link to="/docs">使用文档</router-link>
        </nav>
        <div class="nav-actions">
          <button class="btn-login" @click="router.push('/login')">登录</button>
          <button class="btn-register" @click="router.push('/register')">免费试用</button>
        </div>
      </div>
    </header>

    <!-- Hero 区域 -->
    <section class="pricing-hero">
      <span class="hero-tag">💎 灵活定价</span>
      <h1>选择适合您的方案</h1>
      <p>从初创茶铺到连锁品牌，我们为每个阶段的茶企提供最优解决方案</p>
    </section>

    <!-- 价格卡片 -->
    <section class="pricing-cards">
      <div class="cards-container">
        <div 
          v-for="plan in plans" 
          :key="plan.type"
          :class="['plan-card', plan.tier, { recommended: plan.recommended }]"
        >
          <!-- 推荐标签 -->
          <div v-if="plan.recommended" class="recommend-badge">
            <span class="badge-glow"></span>
            <span class="badge-text">🔥 最受欢迎</span>
          </div>
          
          <!-- 卡片内容 -->
          <div class="card-content">
            <h3 class="plan-name">{{ plan.name }}</h3>
            <p class="plan-desc">{{ plan.description }}</p>
            
            <div class="price-block">
              <span class="currency">{{ plan.price }}</span>
              <span class="amount">{{ plan.priceNum }}</span>
              <span class="period">{{ plan.period }}</span>
            </div>
            
            <ul class="features-list">
              <li v-for="(f, i) in plan.features" :key="i">
                <span :class="['check-icon', plan.tier]">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
                <span class="feature-text">{{ f }}</span>
              </li>
            </ul>
            
            <button 
              :class="['buy-btn', plan.tier, { primary: plan.recommended }]"
              @click="handleBuy(plan.type)"
            >
              {{ plan.action }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ 简要 -->
    <section class="faq-section">
      <h2>常见问题</h2>
      <div class="faq-grid">
        <div class="faq-item">
          <h4>可以随时升级方案吗？</h4>
          <p>是的，您可以随时升级到更高级的方案，费用按比例计算。</p>
        </div>
        <div class="faq-item">
          <h4>支持哪些支付方式？</h4>
          <p>支持支付宝、微信支付、银行转账等多种支付方式。</p>
        </div>
        <div class="faq-item">
          <h4>数据安全如何保障？</h4>
          <p>采用银行级加密技术，数据每日自动备份，确保您的业务数据安全。</p>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-brand">
          <span class="brand-logo">🍃</span>
          <span class="brand-name">茗管家</span>
        </div>
        <p class="copyright">© 2025 茗管家 ZenTea ERP. All rights reserved.</p>
        <div class="footer-links">
          <router-link to="/contact">联系我们</router-link>
          <router-link to="/docs">帮助中心</router-link>
          <router-link to="/business">商务合作</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* ========== 基础变量 ========== */
.pricing-page {
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
  overflow-x: hidden;
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
  background: rgba(10, 15, 13, 0.85);
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

.nav-actions {
  display: flex;
  gap: 12px;
}

.btn-login {
  padding: 8px 20px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-login:hover {
  border-color: var(--accent-green);
  color: var(--accent-green);
}

.btn-register {
  padding: 8px 20px;
  background: linear-gradient(135deg, #059669, #10b981);
  border: none;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-register:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
}

/* ========== Hero 区域 ========== */
.pricing-hero {
  padding: 140px 24px 80px;
  text-align: center;
  position: relative;
  z-index: 1;
}

.hero-tag {
  display: inline-block;
  padding: 8px 20px;
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.3);
  border-radius: 50px;
  font-size: 14px;
  color: var(--accent-green);
  margin-bottom: 24px;
}

.pricing-hero h1 {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.pricing-hero p {
  font-size: 18px;
  color: var(--text-secondary);
  max-width: 500px;
  margin: 0 auto;
}

/* ========== 价格卡片区域 ========== */
.pricing-cards {
  padding: 0 24px 100px;
  position: relative;
  z-index: 1;
}

.cards-container {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  align-items: stretch;
}

/* 基础卡片样式 */
.plan-card {
  position: relative;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 32px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: visible;
}

.plan-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

/* 悬停效果 */
.plan-card:hover {
  transform: translateY(-8px);
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.4),
    0 0 60px rgba(74, 222, 128, 0.1);
}

/* ========== 推荐卡片特殊样式 ========== */
.plan-card.recommended {
  transform: scale(1.05);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(34, 211, 238, 0.05));
  border: 2px solid transparent;
  background-clip: padding-box;
  z-index: 2;
}

.plan-card.recommended::after {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 22px;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green), var(--accent-cyan));
  background-size: 200% 200%;
  animation: borderGlow 3s ease infinite;
  z-index: -1;
}

@keyframes borderGlow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.plan-card.recommended:hover {
  transform: scale(1.05) translateY(-8px);
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.5),
    0 0 80px rgba(74, 222, 128, 0.2);
}

/* 推荐标签 */
.recommend-badge {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.badge-glow {
  position: absolute;
  inset: -4px;
  background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan));
  border-radius: 20px;
  filter: blur(8px);
  opacity: 0.6;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.badge-text {
  position: relative;
  display: block;
  padding: 8px 20px;
  background: linear-gradient(135deg, #059669, #10b981);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: white;
  white-space: nowrap;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
}

/* ========== 卡片内容 ========== */
.card-content {
  position: relative;
  z-index: 1;
}

.plan-name {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.plan-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 24px;
}

/* 价格样式 */
.price-block {
  margin-bottom: 28px;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2px;
}

.currency {
  font-size: 20px;
  font-weight: 500;
  color: var(--text-secondary);
}

.amount {
  font-size: 52px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: -2px;
}

.plan-card.recommended .amount {
  background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.plan-card.premium .amount {
  background: linear-gradient(135deg, var(--accent-gold), #f59e0b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.period {
  font-size: 14px;
  color: var(--text-muted);
  margin-left: 4px;
}

/* ========== 功能列表 ========== */
.features-list {
  list-style: none;
  padding: 0;
  margin: 0 0 28px;
}

.features-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.features-list li:last-child {
  border-bottom: none;
}

.check-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.check-icon svg {
  width: 12px;
  height: 12px;
}

.check-icon.basic {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-muted);
}

.check-icon.pro {
  background: rgba(74, 222, 128, 0.2);
  color: var(--accent-green);
}

.check-icon.premium {
  background: rgba(251, 191, 36, 0.2);
  color: var(--accent-gold);
}

.feature-text {
  font-size: 14px;
  color: var(--text-secondary);
}

/* ========== 购买按钮 ========== */
.buy-btn {
  width: 100%;
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.buy-btn.basic {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.buy-btn.basic:hover {
  border-color: var(--accent-green);
  color: var(--accent-green);
  box-shadow: 0 0 20px rgba(74, 222, 128, 0.2);
}

.buy-btn.pro,
.buy-btn.primary {
  background: linear-gradient(135deg, #059669, #10b981);
  border: none;
  color: white;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.buy-btn.pro:hover,
.buy-btn.primary:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 25px rgba(16, 185, 129, 0.5);
}

.buy-btn.premium {
  background: linear-gradient(135deg, #d97706, #f59e0b);
  border: none;
  color: white;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.buy-btn.premium:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 25px rgba(245, 158, 11, 0.5);
}

/* ========== FAQ 区域 ========== */
.faq-section {
  max-width: 900px;
  margin: 0 auto;
  padding: 60px 24px 80px;
  position: relative;
  z-index: 1;
}

.faq-section h2 {
  text-align: center;
  font-size: 28px;
  margin-bottom: 40px;
  color: var(--text-primary);
}

.faq-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.faq-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
}

.faq-item:hover {
  border-color: rgba(74, 222, 128, 0.3);
  background: rgba(74, 222, 128, 0.05);
}

.faq-item h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.faq-item p {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
}

/* ========== 页脚 ========== */
.footer {
  background: linear-gradient(180deg, transparent, rgba(16, 185, 129, 0.05));
  border-top: 1px solid var(--border-color);
  padding: 40px 24px;
  position: relative;
  z-index: 1;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-logo {
  font-size: 24px;
}

.brand-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.copyright {
  font-size: 12px;
  color: var(--text-muted);
}

.footer-links {
  display: flex;
  gap: 24px;
}

.footer-links a {
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: var(--accent-green);
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .cards-container {
    grid-template-columns: 1fr;
    max-width: 400px;
  }
  
  .plan-card.recommended {
    transform: none;
    order: -1;
  }
  
  .plan-card.recommended:hover {
    transform: translateY(-8px);
  }
  
  .faq-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  
  .pricing-hero h1 {
    font-size: 32px;
  }
  
  .pricing-hero p {
    font-size: 16px;
  }
  
  .amount {
    font-size: 42px;
  }
}
</style>
