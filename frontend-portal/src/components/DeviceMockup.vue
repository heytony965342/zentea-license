<script setup lang="ts">
/**
 * 3D 多端协同展示组件
 * 展示 PC 端与 App 端协同能力
 * 优化：轻量视差效果 + 收敛发光
 */
import { ref, computed } from 'vue'

interface MockupConfig {
  laptopImage: string   // PC端截图
  phoneImage: string    // App端截图
  rotateAngle: number   // 3D 倾斜角度
}

const props = withDefaults(defineProps<{
  config?: Partial<MockupConfig>
}>(), {})

const defaultConfig: MockupConfig = {
  laptopImage: '',
  phoneImage: '',
  rotateAngle: 12  // 略微减小初始角度
}

const config = computed(() => ({ ...defaultConfig, ...props.config }))

// 鼠标视差效果 - 限制最大 2 度
const containerRef = ref<HTMLDivElement>()
const rotateX = ref(0)
const rotateY = ref(0)
const maxTilt = 2  // 最大倾斜角度

function onMouseMove(e: MouseEvent) {
  if (!containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const x = (e.clientX - rect.left) / rect.width - 0.5
  const y = (e.clientY - rect.top) / rect.height - 0.5
  // 反向倾斜，限制在 2 度以内
  rotateY.value = -x * maxTilt
  rotateX.value = y * maxTilt
}

function onMouseLeave() {
  // 平滑回正
  rotateX.value = 0
  rotateY.value = 0
}
</script>

<template>
  <div 
    ref="containerRef"
    class="device-mockup"
    @mousemove="onMouseMove"
    @mouseleave="onMouseLeave"
  >
    <!-- 3D 变换容器 -->
    <div 
      class="mockup-3d"
      :style="{
        transform: `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY + config.rotateAngle}deg)`
      }"
    >
      <!-- MacBook -->
      <div class="laptop">
        <div class="laptop-screen">
          <div class="screen-content">
            <img 
              v-if="config.laptopImage" 
              :src="config.laptopImage" 
              alt="PC端界面"
            />
            <!-- 默认演示界面 -->
            <div v-else class="demo-screen laptop-demo">
              <div class="demo-header">
                <span class="dot red"></span>
                <span class="dot yellow"></span>
                <span class="dot green"></span>
                <span class="title">茗管家 - 销售管理</span>
              </div>
              <div class="demo-body">
                <div class="sidebar">
                  <div class="menu-item active">📊 工作台</div>
                  <div class="menu-item">📦 商品管理</div>
                  <div class="menu-item">📝 销售订单</div>
                  <div class="menu-item">💰 财务管理</div>
                  <div class="menu-item">📈 数据报表</div>
                </div>
                <div class="main-content">
                  <div class="stats-row">
                    <div class="stat-card">
                      <div class="stat-num">¥158,600</div>
                      <div class="stat-label">今日销售额</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-num">89</div>
                      <div class="stat-label">今日订单</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-num">12</div>
                      <div class="stat-label">新增客户</div>
                    </div>
                  </div>
                  <div class="chart-placeholder">
                    <div class="bar" style="height: 60%"></div>
                    <div class="bar" style="height: 80%"></div>
                    <div class="bar" style="height: 45%"></div>
                    <div class="bar" style="height: 90%"></div>
                    <div class="bar" style="height: 70%"></div>
                    <div class="bar" style="height: 55%"></div>
                    <div class="bar" style="height: 85%"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="laptop-base">
          <div class="laptop-notch"></div>
        </div>
      </div>
      
      <!-- Phone -->
      <div class="phone">
        <div class="phone-screen">
          <img 
            v-if="config.phoneImage" 
            :src="config.phoneImage" 
            alt="App端界面"
          />
          <!-- 默认演示界面 -->
          <div v-else class="demo-screen phone-demo">
            <div class="phone-header">
              <span>9:41</span>
              <span class="notch"></span>
              <span>📶 🔋</span>
            </div>
            <div class="phone-content">
              <div class="phone-nav">
                <span>🍃</span>
                <span class="phone-title">茗管家</span>
                <span>🔔</span>
              </div>
              <div class="order-card">
                <div class="order-header">
                  <span>📝 新订单</span>
                  <span class="order-time">刚刚</span>
                </div>
                <div class="order-info">
                  <div>客户：王先生</div>
                  <div>商品：大红袍 2斤</div>
                  <div class="order-amount">¥1,200</div>
                </div>
                <div class="order-actions">
                  <button class="btn-confirm">确认订单</button>
                </div>
              </div>
              <div class="quick-actions">
                <div class="action-btn">📦 开单</div>
                <div class="action-btn">📊 库存</div>
                <div class="action-btn">👥 客户</div>
                <div class="action-btn">🤖 AI</div>
              </div>
            </div>
            <div class="phone-tabbar">
              <div class="tab active">🏠</div>
              <div class="tab">📋</div>
              <div class="tab">➕</div>
              <div class="tab">📊</div>
              <div class="tab">👤</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 装饰光晕 - 收敛版本 -->
    <div class="glow glow-primary"></div>
    <div class="glow glow-accent"></div>
  </div>
</template>

<style scoped>
.device-mockup {
  position: relative;
  width: 100%;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible;
}

.mockup-3d {
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}

/* MacBook */
.laptop {
  position: relative;
  width: 480px;
  transform: translateZ(0);
}

.laptop-screen {
  background: linear-gradient(135deg, #2a2a2a, #1a1a1a);
  border-radius: 12px 12px 0 0;
  padding: 10px 10px 0;
  box-shadow: 0 -2px 20px rgba(0,0,0,0.3);
}

.screen-content {
  background: #1e1e1e;
  border-radius: 6px 6px 0 0;
  overflow: hidden;
  aspect-ratio: 16/10;
}

.screen-content img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.laptop-base {
  height: 14px;
  background: linear-gradient(to bottom, #3a3a3a, #2a2a2a);
  border-radius: 0 0 12px 12px;
  position: relative;
}

.laptop-notch {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: #1a1a1a;
  border-radius: 0 0 4px 4px;
  top: 0;
}

/* Phone */
.phone {
  position: absolute;
  right: -40px;
  top: 50%;
  transform: translateY(-50%) translateZ(60px);
  width: 140px;
}

.phone-screen {
  background: #1a1a1a;
  border-radius: 20px;
  padding: 4px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.1);
  overflow: hidden;
}

.phone-screen img {
  width: 100%;
  border-radius: 16px;
}

/* Demo Screens */
.demo-screen {
  font-size: 10px;
  color: #fff;
}

.laptop-demo {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.demo-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #2d2d2d;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.dot.red { background: #ff5f57; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #28ca41; }

.title {
  margin-left: auto;
  color: #888;
  font-size: 9px;
}

.demo-body {
  flex: 1;
  display: flex;
  background: #1a1a1a;
}

.sidebar {
  width: 100px;
  background: #252525;
  padding: 10px 0;
}

.menu-item {
  padding: 6px 12px;
  font-size: 8px;
  color: #888;
  cursor: pointer;
}

.menu-item.active {
  background: rgba(26, 71, 42, 0.3);
  color: #4ade80;
  border-left: 2px solid #4ade80;
}

.main-content {
  flex: 1;
  padding: 12px;
}

.stats-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.stat-card {
  flex: 1;
  background: rgba(255,255,255,0.05);
  padding: 8px;
  border-radius: 6px;
  text-align: center;
}

.stat-num {
  font-size: 12px;
  font-weight: 700;
  color: #4ade80;
}

.stat-label {
  font-size: 7px;
  color: #666;
  margin-top: 2px;
}

.chart-placeholder {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 60px;
  padding: 10px;
  background: rgba(255,255,255,0.03);
  border-radius: 6px;
}

.bar {
  flex: 1;
  background: linear-gradient(to top, #1a472a, #4ade80);
  border-radius: 2px;
  animation: grow 2s ease-out infinite alternate;
}

@keyframes grow {
  from { opacity: 0.6; }
  to { opacity: 1; }
}

/* Phone Demo */
.phone-demo {
  background: linear-gradient(135deg, #1a472a, #0f2a1a);
  border-radius: 16px;
  height: 280px;
  display: flex;
  flex-direction: column;
}

.phone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  font-size: 8px;
  color: #fff;
}

.phone-header .notch {
  width: 50px;
  height: 12px;
  background: #000;
  border-radius: 10px;
}

.phone-content {
  flex: 1;
  padding: 8px;
}

.phone-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.phone-title {
  font-weight: 600;
  font-size: 11px;
}

.order-card {
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 8px;
  margin-bottom: 10px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  margin-bottom: 6px;
}

.order-time {
  color: #4ade80;
}

.order-info {
  font-size: 8px;
  color: rgba(255,255,255,0.7);
  line-height: 1.6;
}

.order-amount {
  color: #d4af37;
  font-weight: 700;
  font-size: 12px;
  margin-top: 4px;
}

.order-actions {
  margin-top: 8px;
}

.btn-confirm {
  width: 100%;
  padding: 6px;
  background: #4ade80;
  color: #0f2a1a;
  border: none;
  border-radius: 6px;
  font-size: 9px;
  font-weight: 600;
  cursor: pointer;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}

.action-btn {
  background: rgba(255,255,255,0.1);
  padding: 8px 4px;
  border-radius: 8px;
  text-align: center;
  font-size: 8px;
}

.phone-tabbar {
  display: flex;
  justify-content: space-around;
  padding: 8px;
  background: rgba(0,0,0,0.3);
}

.tab {
  font-size: 14px;
  opacity: 0.5;
}

.tab.active {
  opacity: 1;
}

/* 收敛版发光效果 - 更淡更柔和 */
.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  z-index: -1;
}

.glow-primary {
  width: 350px;
  height: 350px;
  background: rgba(26, 71, 42, 0.25);  /* 更淡 */
  left: 5%;
  top: 15%;
}

.glow-accent {
  width: 180px;
  height: 180px;
  /* 科技金 #B08D57 的半透明渐变 */
  background: radial-gradient(circle, rgba(176, 141, 87, 0.2), transparent 70%);
  right: 15%;
  bottom: 20%;
}

/* Responsive */
@media (max-width: 768px) {
  .device-mockup {
    height: 350px;
  }
  
  .laptop {
    width: 320px;
  }
  
  .phone {
    width: 100px;
    right: -20px;
  }
  
  .phone-demo {
    height: 200px;
  }
}
</style>
