<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authApi } from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const currentStep = ref(1)

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  company_name: '',
  contact_name: '',
  phone: '',
})

// 粒子背景
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
  
  const particles: { x: number; y: number; size: number; speedX: number; speedY: number; opacity: number }[] = []
  
  for (let i = 0; i < 40; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 2 + 1,
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

const nextStep = () => {
  if (!form.value.username || !form.value.email || !form.value.password) {
    errorMsg.value = '请填写所有必填项'
    return
  }
  
  if (form.value.password !== form.value.confirmPassword) {
    errorMsg.value = '两次密码不一致'
    return
  }
  
  if (form.value.password.length < 6) {
    errorMsg.value = '密码长度至少6位'
    return
  }
  
  errorMsg.value = ''
  currentStep.value = 2
}

const prevStep = () => {
  currentStep.value = 1
  errorMsg.value = ''
}

const handleRegister = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await authApi.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      company_name: form.value.company_name || undefined,
      contact_name: form.value.contact_name || undefined,
      phone: form.value.phone || undefined,
    })
    
    if (res.code === 200) {
      successMsg.value = '注册成功！'
      setTimeout(() => {
        // 如果有套餐参数，跳转到登录后继续购买流程
        const plan = route.query.plan
        if (plan) {
          router.push(`/login?redirect=/checkout?plan=${plan}`)
        } else {
          router.push('/login')
        }
      }, 1500)
    } else {
      errorMsg.value = res.message || '注册失败'
    }
  } catch (e: any) {
    errorMsg.value = e.response?.data?.message || '注册失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  initParticles()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<template>
  <div class="register-page">
    <canvas ref="canvasRef" class="particles-bg"></canvas>
    
    <div class="register-container">
      <!-- 左侧品牌区 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="brand-logo" @click="router.push('/')">🍃</div>
          <h1>加入茗管家</h1>
          <p>开启智能茶企管理之旅</p>
          
          <div class="benefits">
            <div class="benefit-item">
              <div class="benefit-icon">🎁</div>
              <div class="benefit-text">
                <h4>7天免费试用</h4>
                <p>全功能体验，无需付费</p>
              </div>
            </div>
            <div class="benefit-item">
              <div class="benefit-icon">🔒</div>
              <div class="benefit-text">
                <h4>数据安全保障</h4>
                <p>银行级加密，每日备份</p>
              </div>
            </div>
            <div class="benefit-item">
              <div class="benefit-icon">💬</div>
              <div class="benefit-text">
                <h4>专属客服支持</h4>
                <p>7×12小时在线服务</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧注册区 -->
      <div class="form-section">
        <div class="form-box">
          <!-- 步骤指示器 -->
          <div class="steps">
            <div :class="['step', { active: currentStep >= 1 }]">
              <span class="step-num">1</span>
              <span class="step-label">账户信息</span>
            </div>
            <div class="step-line" :class="{ active: currentStep >= 2 }"></div>
            <div :class="['step', { active: currentStep >= 2 }]">
              <span class="step-num">2</span>
              <span class="step-label">企业信息</span>
            </div>
          </div>
          
          <!-- 成功提示 -->
          <div v-if="successMsg" class="success-msg">
            <span class="success-icon">✓</span>
            {{ successMsg }}
          </div>
          
          <form v-else @submit.prevent="currentStep === 1 ? nextStep() : handleRegister()">
            <!-- 步骤1：账户信息 -->
            <template v-if="currentStep === 1">
              <div class="form-group">
                <label>用户名 <span class="required">*</span></label>
                <input 
                  v-model="form.username" 
                  type="text" 
                  placeholder="用于登录的用户名"
                />
              </div>
              
              <div class="form-group">
                <label>邮箱 <span class="required">*</span></label>
                <input 
                  v-model="form.email" 
                  type="email" 
                  placeholder="用于接收通知的邮箱"
                />
              </div>
              
              <div class="form-group">
                <label>密码 <span class="required">*</span></label>
                <input 
                  v-model="form.password" 
                  type="password" 
                  placeholder="至少6位字符"
                />
              </div>
              
              <div class="form-group">
                <label>确认密码 <span class="required">*</span></label>
                <input 
                  v-model="form.confirmPassword" 
                  type="password" 
                  placeholder="再次输入密码"
                />
              </div>
            </template>
            
            <!-- 步骤2：企业信息 -->
            <template v-if="currentStep === 2">
              <div class="form-group">
                <label>企业名称</label>
                <input 
                  v-model="form.company_name" 
                  type="text" 
                  placeholder="您的企业或门店名称（选填）"
                />
              </div>
              
              <div class="form-group">
                <label>联系人</label>
                <input 
                  v-model="form.contact_name" 
                  type="text" 
                  placeholder="联系人姓名（选填）"
                />
              </div>
              
              <div class="form-group">
                <label>联系电话</label>
                <input 
                  v-model="form.phone" 
                  type="tel" 
                  placeholder="方便我们联系您（选填）"
                />
              </div>
            </template>
            
            <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
            
            <div class="btn-group">
              <button 
                v-if="currentStep === 2" 
                type="button" 
                class="btn-back"
                @click="prevStep"
              >
                返回
              </button>
              <button type="submit" class="btn-submit" :disabled="loading">
                <span v-if="loading" class="loading-spinner"></span>
                <span v-else>{{ currentStep === 1 ? '下一步' : '完成注册' }}</span>
              </button>
            </div>
          </form>
          
          <div class="form-footer">
            <span>已有账户？</span>
            <router-link to="/login">立即登录</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0f0d 0%, #0d1512 50%, #0a1a14 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.particles-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.register-container {
  position: relative;
  z-index: 1;
  display: flex;
  width: 100%;
  max-width: 1000px;
  min-height: 650px;
  margin: 24px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

/* 左侧品牌区 */
.brand-section {
  flex: 1;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(34, 211, 238, 0.05));
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.brand-content {
  color: white;
}

.brand-logo {
  font-size: 56px;
  cursor: pointer;
  margin-bottom: 16px;
  transition: transform 0.3s;
}

.brand-logo:hover {
  transform: scale(1.1);
}

.brand-content h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #fff, rgba(255,255,255,0.8));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-content > p {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 40px;
}

.benefits {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.benefit-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.benefit-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.benefit-text h4 {
  font-size: 15px;
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
}

.benefit-text p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* 右侧注册区 */
.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.form-box {
  width: 100%;
  max-width: 380px;
}

/* 步骤指示器 */
.steps {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
}

.step.active .step-num {
  background: linear-gradient(135deg, #059669, #10b981);
  border-color: #10b981;
  color: white;
}

.step-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.step.active .step-label {
  color: rgba(255, 255, 255, 0.8);
}

.step-line {
  width: 60px;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0 16px;
  margin-bottom: 24px;
  transition: background 0.3s;
}

.step-line.active {
  background: linear-gradient(90deg, #10b981, #10b981);
}

/* 表单样式 */
.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  margin-bottom: 8px;
}

.required {
  color: #f87171;
}

.form-group input {
  width: 100%;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  font-size: 15px;
  transition: all 0.3s;
  outline: none;
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.form-group input:focus {
  border-color: #4ade80;
  background: rgba(74, 222, 128, 0.05);
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.1);
}

.error-msg {
  color: #f87171;
  font-size: 13px;
  margin-bottom: 16px;
  padding: 10px 14px;
  background: rgba(248, 113, 113, 0.1);
  border-radius: 8px;
}

.success-msg {
  text-align: center;
  padding: 48px 24px;
  color: #4ade80;
  font-size: 18px;
}

.success-icon {
  display: inline-flex;
  width: 48px;
  height: 48px;
  background: rgba(74, 222, 128, 0.2);
  border-radius: 50%;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 16px;
}

.btn-group {
  display: flex;
  gap: 12px;
}

.btn-back {
  flex: 0 0 auto;
  padding: 14px 24px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-back:hover {
  border-color: rgba(255, 255, 255, 0.4);
  color: white;
}

.btn-submit {
  flex: 1;
  padding: 14px;
  background: linear-gradient(135deg, #059669, #10b981);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-footer {
  margin-top: 24px;
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.form-footer a {
  color: #4ade80;
  text-decoration: none;
  margin-left: 4px;
  font-weight: 500;
}

.form-footer a:hover {
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 768px) {
  .register-container {
    flex-direction: column;
    min-height: auto;
  }
  
  .brand-section {
    display: none;
  }
  
  .form-section {
    padding: 32px 24px;
  }
}
</style>
