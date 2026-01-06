<script setup lang="ts">
/**
 * AI 交互演示区 - 小茗管家对话模拟
 * 自动循环播放预设对话，展示自然语言处理能力
 * 优化：动态光标 + Stagger 入场动画
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { NCard } from 'naive-ui'

interface DemoQuery {
  question: string
  answer: {
    type: 'chart' | 'table' | 'text' | 'stats'
    data: any
  }
}

const props = withDefaults(defineProps<{
  queries?: DemoQuery[]
}>(), {
  queries: () => [
    {
      question: '查一下上个月利润最高的茶叶种类',
      answer: {
        type: 'stats',
        data: {
          title: '利润排行 TOP 3',
          items: [
            { label: '大红袍', value: '¥28,500', trend: '+15%' },
            { label: '西湖龙井', value: '¥22,300', trend: '+8%' },
            { label: '安溪铁观音', value: '¥18,600', trend: '+12%' }
          ]
        }
      }
    },
    {
      question: '本周销售额和上周相比怎么样？',
      answer: {
        type: 'stats',
        data: {
          title: '周销售对比',
          items: [
            { label: '本周销售额', value: '¥156,800', trend: '+23%' },
            { label: '订单数量', value: '89 单', trend: '+18%' },
            { label: '新增客户', value: '12 位', trend: '+50%' }
          ]
        }
      }
    },
    {
      question: '哪些商品库存快不足了？',
      answer: {
        type: 'stats',
        data: {
          title: '库存预警',
          items: [
            { label: '特级龙井（2024）', value: '仅剩 5 斤', trend: '紧急' },
            { label: '正山小种', value: '仅剩 8 斤', trend: '预警' },
            { label: '白毫银针', value: '仅剩 10 斤', trend: '预警' }
          ]
        }
      }
    },
    {
      question: '帮我预测下个月普洱茶的销量',
      answer: {
        type: 'stats',
        data: {
          title: 'AI 销量预测',
          items: [
            { label: '预测销量', value: '约 280 斤', trend: '置信度 92%' },
            { label: '建议备货', value: '320 斤', trend: '含安全库存' },
            { label: '预估营收', value: '¥84,000', trend: '+15%' }
          ]
        }
      }
    }
  ]
})

const currentIndex = ref(0)
const typingText = ref('')
const showAnswer = ref(false)
const isTyping = ref(false)
const isThinking = ref(false)  // AI 思考状态
const visibleItems = ref<number[]>([])  // 控制 stagger 显示的项
let timer: number | null = null
let typeTimer: number | null = null

const currentQuery = computed(() => props.queries[currentIndex.value])

// 打字机效果
async function typeQuestion(text: string) {
  isTyping.value = true
  typingText.value = ''
  showAnswer.value = false
  isThinking.value = false
  visibleItems.value = []
  
  for (let i = 0; i <= text.length; i++) {
    await new Promise(resolve => {
      typeTimer = window.setTimeout(resolve, 40 + Math.random() * 40)
    })
    typingText.value = text.slice(0, i)
  }
  
  isTyping.value = false
  
  // AI 思考中...
  isThinking.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  isThinking.value = false
  
  // 显示答案
  showAnswer.value = true
  
  // Stagger 显示每个数据项
  const items = currentQuery.value.answer.data.items
  for (let i = 0; i < items.length; i++) {
    await new Promise(resolve => setTimeout(resolve, 200))
    visibleItems.value.push(i)
  }
  
  // 停留后切换下一个
  await new Promise(resolve => setTimeout(resolve, 4000))
  nextQuery()
}

function nextQuery() {
  currentIndex.value = (currentIndex.value + 1) % props.queries.length
  typeQuestion(props.queries[currentIndex.value].question)
}

onMounted(() => {
  typeQuestion(props.queries[0].question)
})

onUnmounted(() => {
  if (timer) clearTimeout(timer)
  if (typeTimer) clearTimeout(typeTimer)
})

// 趋势颜色
function getTrendColor(trend: string): string {
  if (trend.includes('+')) return '#52c41a'
  if (trend.includes('-')) return '#f5222d'
  if (trend === '紧急') return '#f5222d'
  if (trend === '预警') return '#faad14'
  return '#1a472a'
}
</script>

<template>
  <div class="ai-demo">
    <div class="demo-container">
      <!-- 搜索框 -->
      <div class="search-box">
        <div class="search-icon">🤖</div>
        <div class="search-input">
          <span class="typing-text">{{ typingText }}</span>
          <span class="cursor" :class="{ typing: isTyping, thinking: isThinking }">|</span>
        </div>
        <div class="ai-badge">
          <span v-if="isThinking" class="thinking-dots">
            <span></span><span></span><span></span>
          </span>
          <span v-else>小茗</span>
        </div>
      </div>
      
      <!-- 答案卡片 -->
      <Transition name="slide-up">
        <div v-if="showAnswer && currentQuery" class="answer-card">
          <NCard :bordered="false" class="glass-card">
            <template #header>
              <div class="answer-header">
                <span class="answer-icon">✨</span>
                {{ currentQuery.answer.data.title }}
              </div>
            </template>
            
            <div class="stats-grid">
              <Transition
                v-for="(item, i) in currentQuery.answer.data.items" 
                :key="i"
                name="stagger-item"
              >
                <div 
                  v-if="visibleItems.includes(i)"
                  class="stat-item"
                  :style="{ '--delay': `${i * 100}ms` }"
                >
                  <div class="stat-label">{{ item.label }}</div>
                  <div class="stat-value">{{ item.value }}</div>
                  <div 
                    class="stat-trend" 
                    :style="{ color: getTrendColor(item.trend) }"
                  >
                    {{ item.trend }}
                  </div>
                </div>
              </Transition>
            </div>
          </NCard>
        </div>
      </Transition>
      
      <!-- 进度指示器 -->
      <div class="progress-dots">
        <span 
          v-for="(_, i) in queries" 
          :key="i" 
          class="dot"
          :class="{ active: i === currentIndex }"
          @click="currentIndex = i; typeQuestion(queries[i].question)"
        ></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-demo {
  padding: 40px 20px;
}

.demo-container {
  max-width: 600px;
  margin: 0 auto;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 50px;
  margin-bottom: 20px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
}

.search-icon {
  font-size: 24px;
}

.search-input {
  flex: 1;
  font-size: 16px;
  color: #fff;
  min-height: 24px;
  display: flex;
  align-items: center;
}

.typing-text {
  color: rgba(255, 255, 255, 0.95);
}

/* 动态光标 */
.cursor {
  color: #d4af37;
  font-weight: bold;
  margin-left: 2px;
  animation: blink 1s infinite;
}

.cursor.typing {
  animation: blink 0.4s infinite;
}

.cursor.thinking {
  animation: pulse 0.6s infinite;
  color: #4ade80;
}

@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scaleY(0.8); }
  50% { opacity: 1; transform: scaleY(1.2); }
}

.ai-badge {
  padding: 6px 14px;
  background: linear-gradient(135deg, #d4af37, #f0c850);
  color: #1a472a;
  border-radius: 14px;
  font-size: 12px;
  font-weight: 600;
  min-width: 45px;
  text-align: center;
}

/* 思考中动画 */
.thinking-dots {
  display: inline-flex;
  gap: 3px;
  align-items: center;
  justify-content: center;
}

.thinking-dots span {
  width: 4px;
  height: 4px;
  background: #1a472a;
  border-radius: 50%;
  animation: thinking-bounce 1.4s infinite both;
}

.thinking-dots span:nth-child(1) { animation-delay: 0s; }
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes thinking-bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.answer-card {
  margin-bottom: 20px;
}

.glass-card {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.glass-card :deep(.n-card-header) {
  padding: 16px 20px 8px;
}

.glass-card :deep(.n-card__content) {
  padding: 8px 20px 20px;
}

.answer-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}

.answer-icon {
  font-size: 18px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 14px 12px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.65);
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 6px;
}

.stat-trend {
  font-size: 12px;
  font-weight: 600;
}

.progress-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s;
}

.dot.active {
  background: #d4af37;
  transform: scale(1.3);
  box-shadow: 0 0 8px rgba(212, 175, 55, 0.5);
}

.dot:hover {
  background: rgba(255, 255, 255, 0.6);
}

/* 滑入动画 */
.slide-up-enter-active {
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.slide-up-leave-active {
  transition: all 0.3s ease-out;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Stagger 动画 - 数据项依次跳出 */
.stagger-item-enter-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  transition-delay: var(--delay, 0ms);
}

.stagger-item-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.9);
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    text-align: left;
  }
  
  .stat-label {
    margin-bottom: 0;
    flex: 1;
  }
  
  .stat-value {
    margin-bottom: 0;
    margin-right: 12px;
  }
}
</style>
