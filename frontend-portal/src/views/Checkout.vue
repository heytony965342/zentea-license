<script setup lang="ts">
/**
 * 结算/支付页面 - 深色主题版
 */
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import { portalApi, promoApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const message = useMessage()
const userStore = useUserStore()

// 套餐信息
const planType = ref(route.query.plan as string || 'yearly')
const planInfo = computed(() => {
  const plans: Record<string, { name: string; price: number; period: string; icon: string }> = {
    trial: { name: '试用版', price: 0, period: '7天体验', icon: '🌱' },
    monthly: { name: '月度版', price: 99, period: '每月', icon: '📅' },
    yearly: { name: '年度版', price: 899, period: '每年', icon: '⭐' },
    lifetime: { name: '终身版', price: 2999, period: '永久', icon: '👑' },
  }
  return plans[planType.value] || plans.yearly
})

// 步骤
const currentStep = ref(1)
const steps = [
  { num: 1, title: '确认订单', icon: '📋' },
  { num: 2, title: '支付', icon: '💳' },
  { num: 3, title: '完成', icon: '✅' },
]

// 促销码
const promoCode = ref('')
const promoChecking = ref(false)
const promoValid = ref(false)
const promoDiscount = ref(0)
const promoMessage = ref('')
const finalPrice = computed(() => {
  if (promoValid.value) {
    return Math.max(0, planInfo.value.price - promoDiscount.value)
  }
  return planInfo.value.price
})

// 订单
const orderCreating = ref(false)
const orderInfo = ref<{
  order_id: number
  order_no: string
  amount: number
  license_key?: string
} | null>(null)

// 支付凭证
const paymentProofUrl = ref('')
const uploading = ref(false)

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

// 检查促销码
const checkPromoCode = async () => {
  if (!promoCode.value.trim()) {
    promoValid.value = false
    promoMessage.value = ''
    promoDiscount.value = 0
    return
  }
  
  promoChecking.value = true
  try {
    const res = await promoApi.checkCode(promoCode.value.trim())
    if (res.code === 200) {
      promoValid.value = true
      promoMessage.value = res.data.name
      promoDiscount.value = planInfo.value.price // 限免活动全额减免
    } else {
      promoValid.value = false
      promoMessage.value = res.message || '促销码无效'
      promoDiscount.value = 0
    }
  } catch (e) {
    promoValid.value = false
    promoMessage.value = '检查失败'
    promoDiscount.value = 0
  } finally {
    promoChecking.value = false
  }
}

// 创建订单
const createOrder = async () => {
  orderCreating.value = true
  try {
    const res = await portalApi.createOrder(
      planType.value,
      promoValid.value ? promoCode.value : undefined
    )
    
    if (res.code === 200) {
      orderInfo.value = res.data
      if (res.data.license_key) {
        currentStep.value = 3
        message.success('授权已生成！')
      } else {
        currentStep.value = 2
      }
    } else {
      message.error(res.message || '创建订单失败')
    }
  } catch (e: any) {
    message.error(e.message || '创建订单失败')
  } finally {
    orderCreating.value = false
  }
}

// 上传支付凭证
const submitPaymentProof = async () => {
  if (!paymentProofUrl.value.trim()) {
    message.warning('请输入支付凭证图片地址')
    return
  }
  
  if (!orderInfo.value) return
  
  uploading.value = true
  try {
    const res = await portalApi.uploadPaymentProof(orderInfo.value.order_id, paymentProofUrl.value)
    if (res.code === 200) {
      message.success('凭证已提交，请等待审核')
      currentStep.value = 3
    } else {
      message.error(res.message || '提交失败')
    }
  } catch (e) {
    message.error('提交失败')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  if (!userStore.token) {
    router.push('/login')
  }
  initParticles()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<template>
  <div class="checkout-page">
    <!-- 背景粒子 -->
    <canvas ref="canvasRef" class="particles-bg"></canvas>
    
    <!-- 顶部导航 -->
    <header class="nav">
      <div class="nav-content">
        <div class="logo" @click="router.push('/')">🍃 茗管家</div>
        <button class="btn-back" @click="router.push('/dashboard')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回控制台
        </button>
      </div>
    </header>

    <main class="content">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>购买授权</h1>
        <p>安全便捷的支付流程</p>
      </div>
      
      <!-- 步骤指示器 -->
      <div class="steps-container">
        <div 
          v-for="(step, index) in steps" 
          :key="step.num"
          :class="['step-item', { 
            active: currentStep === step.num, 
            completed: currentStep > step.num 
          }]"
        >
          <div class="step-icon">
            <span v-if="currentStep > step.num">✓</span>
            <span v-else>{{ step.icon }}</span>
          </div>
          <span class="step-title">{{ step.title }}</span>
          <div v-if="index < steps.length - 1" class="step-line"></div>
        </div>
      </div>
      
      <!-- 步骤1: 确认订单 -->
      <div v-if="currentStep === 1" class="card order-card">
        <div class="card-header">
          <h2>确认订单信息</h2>
        </div>
        
        <div class="order-summary">
          <div class="plan-preview">
            <span class="plan-icon">{{ planInfo.icon }}</span>
            <div class="plan-details">
              <h3>{{ planInfo.name }}</h3>
              <p>有效期：{{ planInfo.period }}</p>
            </div>
            <div class="plan-price">
              <span class="currency">¥</span>
              <span class="amount">{{ planInfo.price }}</span>
            </div>
          </div>
          
          <!-- 促销码 -->
          <div class="promo-section">
            <label>促销码（可选）</label>
            <div class="promo-input-group">
              <input 
                v-model="promoCode"
                type="text"
                placeholder="输入促销码"
                @blur="checkPromoCode"
              />
              <button 
                class="btn-verify"
                :disabled="promoChecking"
                @click="checkPromoCode"
              >
                {{ promoChecking ? '验证中...' : '验证' }}
              </button>
            </div>
            <div 
              v-if="promoMessage" 
              :class="['promo-message', { valid: promoValid, invalid: !promoValid }]"
            >
              <span v-if="promoValid">✓</span>
              <span v-else>✕</span>
              {{ promoMessage }}
            </div>
          </div>
          
          <!-- 价格汇总 -->
          <div class="price-summary">
            <div class="price-row">
              <span>套餐原价</span>
              <span>¥{{ planInfo.price }}</span>
            </div>
            <div v-if="promoValid" class="price-row discount">
              <span>促销优惠</span>
              <span>-¥{{ promoDiscount }}</span>
            </div>
            <div class="price-row total">
              <span>应付金额</span>
              <span class="final-price">¥{{ finalPrice }}</span>
            </div>
          </div>
        </div>
        
        <div class="card-footer">
          <button 
            class="btn-primary"
            :disabled="orderCreating"
            @click="createOrder"
          >
            <span v-if="orderCreating" class="loading-spinner"></span>
            {{ finalPrice > 0 ? '提交订单' : '免费领取' }}
          </button>
        </div>
      </div>
      
      <!-- 步骤2: 支付 -->
      <div v-if="currentStep === 2" class="card payment-card">
        <div class="card-header">
          <h2>支付订单</h2>
        </div>
        
        <div class="payment-info">
          <div class="alert-box info">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 16v-4M12 8h.01" stroke-linecap="round"/>
            </svg>
            <span>请转账至以下账户，转账完成后上传支付凭证</span>
          </div>
          
          <div class="order-details">
            <div class="detail-item">
              <label>订单号</label>
              <span class="order-no">{{ orderInfo?.order_no }}</span>
            </div>
            <div class="detail-item">
              <label>支付金额</label>
              <span class="payment-amount">¥{{ orderInfo?.amount }}</span>
            </div>
          </div>
          
          <div class="payment-methods">
            <h4>支持的支付方式</h4>
            <div class="methods-grid">
              <div class="method-item">
                <span class="method-icon">💳</span>
                <span>银行转账</span>
              </div>
              <div class="method-item">
                <span class="method-icon">📱</span>
                <span>支付宝</span>
              </div>
              <div class="method-item">
                <span class="method-icon">💬</span>
                <span>微信支付</span>
              </div>
            </div>
            <p class="methods-note">请联系客服获取收款账户信息</p>
          </div>
          
          <div class="proof-upload">
            <label>上传支付凭证</label>
            <input 
              v-model="paymentProofUrl"
              type="text"
              placeholder="粘贴支付截图的图片URL"
            />
            <p class="upload-hint">提示：可将截图上传至图床后粘贴链接</p>
          </div>
        </div>
        
        <div class="card-footer">
          <button 
            class="btn-primary"
            :disabled="uploading || !paymentProofUrl.trim()"
            @click="submitPaymentProof"
          >
            <span v-if="uploading" class="loading-spinner"></span>
            提交凭证
          </button>
        </div>
      </div>
      
      <!-- 步骤3: 完成 -->
      <div v-if="currentStep === 3" class="card complete-card">
        <!-- 授权码已生成 -->
        <template v-if="orderInfo?.license_key">
          <div class="success-header">
            <div class="success-icon">🎉</div>
            <h2>授权已生成！</h2>
            <p>请在茗管家 ERP 软件中输入以下授权码进行激活</p>
          </div>
          
          <div class="license-display">
            <label>您的授权码</label>
            <div class="license-code">
              <code>{{ orderInfo.license_key }}</code>
              <button class="btn-copy" @click="navigator.clipboard.writeText(orderInfo.license_key || '')">
                📋 复制
              </button>
            </div>
          </div>
          
          <div class="next-steps">
            <h4>下一步操作</h4>
            <ol>
              <li>打开茗管家 ERP 软件</li>
              <li>进入「系统设置」→「授权管理」</li>
              <li>输入上方授权码并点击激活</li>
            </ol>
          </div>
        </template>
        
        <!-- 等待审核 -->
        <template v-else>
          <div class="pending-header">
            <div class="pending-icon">⏳</div>
            <h2>凭证已提交</h2>
            <p>我们将在 1-2 个工作日内审核您的支付凭证</p>
          </div>
          
          <div class="order-status">
            <div class="status-item">
              <label>订单号</label>
              <span>{{ orderInfo?.order_no }}</span>
            </div>
            <div class="status-item">
              <label>订单状态</label>
              <span class="status-badge pending">等待审核</span>
            </div>
          </div>
          
          <div class="alert-box success">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>审核通过后，授权码将自动发送至您的邮箱</span>
          </div>
        </template>
        
        <div class="card-footer">
          <button class="btn-secondary" @click="router.push('/orders')">
            查看我的订单
          </button>
          <button class="btn-primary" @click="router.push('/licenses')">
            查看我的授权
          </button>
        </div>
      </div>
    </main>
    
    <!-- 页脚 -->
    <footer class="footer">
      <p>© 2025 茗管家 ZenTea ERP. 安全支付由 SSL 加密保护</p>
    </footer>
  </div>
</template>

<style scoped>
/* ========== 基础变量 ========== */
.checkout-page {
  --bg-primary: #0a0f0d;
  --bg-secondary: #0d1512;
  --bg-card: rgba(255, 255, 255, 0.03);
  --border-color: rgba(255, 255, 255, 0.08);
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-muted: rgba(255, 255, 255, 0.5);
  --accent-green: #4ade80;
  --accent-cyan: #22d3ee;
  --accent-red: #f87171;
  
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
  max-width: 900px;
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
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back svg {
  width: 18px;
  height: 18px;
}

.btn-back:hover {
  border-color: var(--accent-green);
  color: var(--accent-green);
}

/* ========== 主内容区 ========== */
.content {
  max-width: 700px;
  margin: 0 auto;
  padding: 110px 24px 60px;
  position: relative;
  z-index: 1;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.page-header p {
  color: var(--text-muted);
  font-size: 15px;
}

/* ========== 步骤指示器 ========== */
.steps-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40px;
  gap: 0;
}

.step-item {
  display: flex;
  align-items: center;
  position: relative;
}

.step-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: all 0.3s;
}

.step-item.active .step-icon {
  border-color: var(--accent-green);
  background: rgba(74, 222, 128, 0.1);
  box-shadow: 0 0 20px rgba(74, 222, 128, 0.3);
}

.step-item.completed .step-icon {
  border-color: var(--accent-green);
  background: var(--accent-green);
  color: #000;
}

.step-title {
  position: absolute;
  top: 56px;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: 12px;
  color: var(--text-muted);
}

.step-item.active .step-title,
.step-item.completed .step-title {
  color: var(--accent-green);
}

.step-line {
  width: 80px;
  height: 2px;
  background: var(--border-color);
  margin: 0 8px;
}

.step-item.completed + .step-item .step-line,
.step-item.completed .step-line {
  background: var(--accent-green);
}

/* ========== 卡片通用样式 ========== */
.card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  overflow: hidden;
}

.card-header {
  padding: 24px 28px;
  border-bottom: 1px solid var(--border-color);
}

.card-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.card-footer {
  padding: 24px 28px;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* ========== 订单确认卡片 ========== */
.order-summary {
  padding: 28px;
}

.plan-preview {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(74, 222, 128, 0.05);
  border: 1px solid rgba(74, 222, 128, 0.2);
  border-radius: 12px;
  margin-bottom: 24px;
}

.plan-icon {
  font-size: 32px;
}

.plan-details {
  flex: 1;
}

.plan-details h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.plan-details p {
  font-size: 13px;
  color: var(--text-muted);
}

.plan-price {
  text-align: right;
}

.plan-price .currency {
  font-size: 16px;
  color: var(--text-secondary);
}

.plan-price .amount {
  font-size: 32px;
  font-weight: 700;
  color: var(--accent-green);
}

/* 促销码 */
.promo-section {
  margin-bottom: 24px;
}

.promo-section label {
  display: block;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.promo-input-group {
  display: flex;
  gap: 12px;
}

.promo-input-group input {
  flex: 1;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.promo-input-group input:focus {
  border-color: var(--accent-green);
}

.promo-input-group input::placeholder {
  color: var(--text-muted);
}

.btn-verify {
  padding: 12px 20px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-verify:hover:not(:disabled) {
  border-color: var(--accent-green);
  color: var(--accent-green);
}

.btn-verify:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.promo-message {
  margin-top: 10px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.promo-message.valid {
  color: var(--accent-green);
}

.promo-message.invalid {
  color: var(--accent-red);
}

/* 价格汇总 */
.price-summary {
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.price-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.price-row.discount {
  color: var(--accent-green);
}

.price-row.total {
  padding-top: 16px;
  margin-top: 8px;
  border-top: 1px dashed var(--border-color);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.final-price {
  font-size: 24px;
  color: var(--accent-green);
}

/* ========== 按钮样式 ========== */
.btn-primary {
  padding: 14px 32px;
  background: linear-gradient(135deg, #059669, #10b981);
  border: none;
  color: white;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  padding: 14px 32px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  border-color: var(--accent-green);
  color: var(--accent-green);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ========== 支付卡片 ========== */
.payment-info {
  padding: 28px;
}

.alert-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  font-size: 14px;
  margin-bottom: 24px;
}

.alert-box svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.alert-box.info {
  background: rgba(34, 211, 238, 0.1);
  border: 1px solid rgba(34, 211, 238, 0.3);
  color: var(--accent-cyan);
}

.alert-box.success {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.3);
  color: var(--accent-green);
}

.order-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-item {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
}

.detail-item label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.order-no {
  font-family: monospace;
  font-size: 14px;
  color: var(--text-primary);
}

.payment-amount {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent-green);
}

.payment-methods {
  margin-bottom: 24px;
}

.payment-methods h4 {
  font-size: 14px;
  margin-bottom: 12px;
  color: var(--text-secondary);
}

.methods-grid {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.method-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-size: 13px;
  color: var(--text-secondary);
}

.method-icon {
  font-size: 24px;
}

.methods-note {
  font-size: 12px;
  color: var(--text-muted);
}

.proof-upload {
  margin-top: 24px;
}

.proof-upload label {
  display: block;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.proof-upload input {
  width: 100%;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.proof-upload input:focus {
  border-color: var(--accent-green);
}

.upload-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

/* ========== 完成卡片 ========== */
.success-header,
.pending-header {
  text-align: center;
  padding: 40px 28px 24px;
}

.success-icon,
.pending-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.success-header h2,
.pending-header h2 {
  font-size: 24px;
  margin-bottom: 8px;
}

.success-header p,
.pending-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

.license-display {
  padding: 0 28px 24px;
}

.license-display label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
  text-align: center;
}

.license-code {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.3);
  border-radius: 12px;
}

.license-code code {
  font-size: 18px;
  font-family: 'Fira Code', monospace;
  color: var(--accent-green);
  letter-spacing: 1px;
}

.btn-copy {
  padding: 8px 12px;
  background: rgba(74, 222, 128, 0.2);
  border: none;
  color: var(--accent-green);
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-copy:hover {
  background: rgba(74, 222, 128, 0.3);
}

.next-steps {
  padding: 0 28px 28px;
}

.next-steps h4 {
  font-size: 14px;
  margin-bottom: 12px;
  color: var(--text-secondary);
}

.next-steps ol {
  margin: 0;
  padding-left: 20px;
}

.next-steps li {
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-muted);
}

.order-status {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 0 28px 24px;
}

.status-item {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  text-align: center;
}

.status-item label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

.complete-card .alert-box {
  margin: 0 28px 24px;
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
@media (max-width: 640px) {
  .steps-container {
    transform: scale(0.85);
  }
  
  .order-details,
  .order-status {
    grid-template-columns: 1fr;
  }
  
  .methods-grid {
    flex-wrap: wrap;
  }
  
  .method-item {
    flex: 1 1 calc(50% - 6px);
  }
  
  .card-footer {
    flex-direction: column;
  }
  
  .card-footer button {
    width: 100%;
    justify-content: center;
  }
}
</style>
