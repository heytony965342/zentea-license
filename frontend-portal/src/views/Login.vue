<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const errorMsg = ref('')
const form = ref({
  username: '',
  password: '',
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

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  
  loading.value = true
  errorMsg.value = ''
  
  try {
    const success = await userStore.login(form.value.username, form.value.password)
    if (success) {
      router.push('/dashboard')
    } else {
      errorMsg.value = '用户名或密码错误'
    }
  } catch (e: any) {
    errorMsg.value = e.message || '登录失败'
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
  <div class="login-page">
    <canvas ref="canvasRef" class="particles-bg"></canvas>
    
    <div class="login-container">
      <!-- 左侧品牌区 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="brand-logo" @click="router.push('/')">🍃</div>
          <h1>茗管家</h1>
          <p>茶企专属 ERP 管理系统</p>
          <div class="features">
            <div class="feature-item">
              <span class="icon">📦</span>
              <span>智能进销存管理</span>
            </div>
            <div class="feature-item">
              <span class="icon">🤖</span>
              <span>AI 智能助手</span>
            </div>
            <div class="feature-item">
              <span class="icon">📊</span>
              <span>实时数据分析</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧登录区 -->
      <div class="form-section">
        <div class="form-box">
          <h2>欢迎回来</h2>
          <p class="subtitle">登录您的账户继续</p>
          
          <form @submit.prevent="handleLogin">
            <div class="form-group">
              <label>用户名</label>
              <input 
                v-model="form.username" 
                type="text" 
                placeholder="请输入用户名"
                autocomplete="username"
              />
            </div>
            
            <div class="form-group">
              <label>密码</label>
              <input 
                v-model="form.password" 
                type="password" 
                placeholder="请输入密码"
                autocomplete="current-password"
              />
            </div>
            
            <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
            
            <button type="submit" class="btn-submit" :disabled="loading">
              <span v-if="loading" class="loading-spinner"></span>
              <span v-else>登 录</span>
            </button>
          </form>
          
          <div class="form-footer">
            <span>还没有账户？</span>
            <router-link to="/register">立即注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
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

.login-container {
  position: relative;
  z-index: 1;
  display: flex;
  width: 100%;
  max-width: 1000px;
  min-height: 600px;
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
  text-align: center;
  color: white;
}

.brand-logo {
  font-size: 64px;
  cursor: pointer;
  margin-bottom: 16px;
  transition: transform 0.3s;
}

.brand-logo:hover {
  transform: scale(1.1);
}

.brand-content h1 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #fff, rgba(255,255,255,0.8));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-content > p {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 48px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.feature-item .icon {
  font-size: 20px;
}

/* 右侧登录区 */
.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.form-box {
  width: 100%;
  max-width: 360px;
}

.form-box h2 {
  font-size: 28px;
  font-weight: 600;
  color: white;
  margin-bottom: 8px;
}

.form-box .subtitle {
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 32px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  margin-bottom: 8px;
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

.btn-submit {
  width: 100%;
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
  .login-container {
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
