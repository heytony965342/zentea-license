<script setup lang="ts">
/**
 * 毛玻璃功能卡片组件
 * 优化：图标背景化 + border-beam 动画
 */
import { ref } from 'vue'

defineProps<{
  icon: string
  title: string
  description: string
  features?: string[]
  delay?: number
}>()

const isHovered = ref(false)
</script>

<template>
  <div 
    class="feature-card"
    :style="{ animationDelay: `${delay || 0}ms` }"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <!-- 超大背景水印图标 -->
    <div class="icon-watermark">{{ icon }}</div>
    
    <!-- border-beam 动画 -->
    <div class="border-beam" :class="{ active: isHovered }">
      <div class="beam"></div>
    </div>
    
    <!-- 内容 -->
    <div class="card-content">
      <h3 class="card-title">{{ title }}</h3>
      <p class="card-desc">{{ description }}</p>
      <ul v-if="features?.length" class="card-features">
        <li v-for="(f, i) in features" :key="i">
          <span class="check">✓</span>
          {{ f }}
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.feature-card {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 32px 28px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

/* 超大背景水印图标 */
.icon-watermark {
  position: absolute;
  right: -10px;
  bottom: -20px;
  font-size: 120px;
  opacity: 0.06;
  pointer-events: none;
  transition: all 0.5s ease;
  filter: grayscale(0.5);
}

.feature-card:hover .icon-watermark {
  opacity: 0.12;
  transform: scale(1.1) rotate(-5deg);
}

/* Border Beam 动画容器 */
.border-beam {
  position: absolute;
  inset: 0;
  border-radius: 20px;
  overflow: hidden;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s;
}

.border-beam.active {
  opacity: 1;
}

.beam {
  position: absolute;
  width: 50px;
  height: 50px;
  background: linear-gradient(90deg, transparent, #4ade80, transparent);
  filter: blur(8px);
  animation: none;
}

.border-beam.active .beam {
  animation: border-travel 2s linear infinite;
}

@keyframes border-travel {
  0% {
    top: 0;
    left: 0;
    width: 0;
    height: 2px;
  }
  25% {
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
  }
  25.1% {
    top: 0;
    left: auto;
    right: 0;
    width: 2px;
    height: 0;
  }
  50% {
    top: 0;
    right: 0;
    width: 2px;
    height: 100%;
  }
  50.1% {
    top: auto;
    bottom: 0;
    right: 0;
    width: 0;
    height: 2px;
  }
  75% {
    bottom: 0;
    right: 0;
    left: 0;
    width: 100%;
    height: 2px;
  }
  75.1% {
    bottom: 0;
    left: 0;
    width: 2px;
    height: 0;
  }
  100% {
    bottom: 0;
    left: 0;
    width: 2px;
    height: 100%;
  }
}

/* 渐变边框效果 */
.feature-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  padding: 1px;
  background: linear-gradient(135deg, transparent 40%, rgba(74, 222, 128, 0) 50%, transparent 60%);
  -webkit-mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: all 0.4s;
}

.feature-card:hover::before {
  background: linear-gradient(135deg, transparent 20%, rgba(74, 222, 128, 0.5) 50%, transparent 80%);
  opacity: 1;
  animation: gradient-spin 3s linear infinite;
}

@keyframes gradient-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.feature-card:hover {
  transform: translateY(-8px);
  border-color: rgba(74, 222, 128, 0.3);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(74, 222, 128, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* 内容区 */
.card-content {
  position: relative;
  z-index: 1;
}

.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
}

.card-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.7;
  margin-bottom: 20px;
}

.card-features {
  list-style: none;
  padding: 0;
  margin: 0;
}

.card-features li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  padding: 6px 0;
}

.check {
  color: #4ade80;
  font-weight: bold;
}

/* 入场动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feature-card {
  animation: fadeInUp 0.6s ease-out backwards;
}
</style>
