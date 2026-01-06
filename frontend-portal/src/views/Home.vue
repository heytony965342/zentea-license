<script setup lang="ts">
/**
 * 茗管家首页 - 品牌展示
 */
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NSpace } from 'naive-ui'
import { useUserStore } from '@/stores/user'
import { promoApi, settingApi } from '@/api'

// 组件
import TeaParticles from '@/components/TeaParticles.vue'
import DeviceMockup from '@/components/DeviceMockup.vue'
import AiDemo from '@/components/AiDemo.vue'
import FeatureCard from '@/components/FeatureCard.vue'
import { useScrollReveal } from '@/composables/useScrollReveal'

const router = useRouter()
const userStore = useUserStore()
const { observe } = useScrollReveal()

// Mockup 配置
const mockupConfig = reactive({
  laptopImage: '',
  phoneImage: '',
})

// 所有首页配置
const pageConfig = reactive({
  // Showcase 区
  showcaseTag: '多端协同',
  showcaseTitle: '跨平台无缝办公体验',
  showcaseSubtitle: '无论是在办公室使用电脑，还是在茶园使用手机，数据实时同步，触手可及',
  
  // Features 区
  featuresTag: '核心能力',
  featuresTitle: '为茶企量身打造的全流程解决方案',
  featuresSubtitle: '从采购到销售，从库存到财务，一站式管理您的茶叶生意',
  
  // AI Demo 区
  aiSectionTag: 'AI 赋能',
  aiSectionTitle: '认识「小茗」—— 您的智能经营管家',
  aiSectionSubtitle: '用自然语言提问，即刻获得专业的数据分析与决策建议',
  
  // Testimonials 区
  testimonialsTag: '客户心声',
  testimonialsTitle: '深受全国茶企信赖',
  
  // CTA 区
  ctaTitle: '开启智能茶企管理之旅',
  ctaSubtitle: '免费试用 7 天，体验 AI 驱动的进销存管理',
  ctaButtonText: '立即免费试用',
  ctaSecondaryText: '查看价格方案',
  
  // Footer
  footerBrandName: '茗管家',
  footerBrandSlogan: '茶企专属 ERP 管理系统',
  footerCopyright: '© 2025 茗管家 ZenTea ERP. All rights reserved.',
})

// 导航栏滚动效果
const scrollY = ref(0)
const navClass = computed(() => ({
  'nav': true,
  'nav-scrolled': scrollY.value > 50
}))

// 各区块的滚动进度（用于过渡效果）
const sectionProgress = reactive({
  hero: 0,
  showcase: 0,
  features: 0,
  aiDemo: 0,
  testimonials: 0,
  cta: 0,
})

// 区块引用
const showcaseRef = ref<HTMLElement | null>(null)
const featuresRef = ref<HTMLElement | null>(null)
const aiDemoRef = ref<HTMLElement | null>(null)
const testimonialsRef = ref<HTMLElement | null>(null)
const ctaRef = ref<HTMLElement | null>(null)

function onScroll() {
  scrollY.value = window.scrollY
  const windowHeight = window.innerHeight
  
  // 计算每个区块的滚动进度
  const refs = {
    showcase: showcaseRef.value,
    features: featuresRef.value,
    aiDemo: aiDemoRef.value,
    testimonials: testimonialsRef.value,
    cta: ctaRef.value,
  }
  
  Object.entries(refs).forEach(([key, el]) => {
    if (el) {
      const rect = el.getBoundingClientRect()
      // 当元素进入视口时 progress 从 0 变到 1
      // 当元素离开视口时 progress 从 1 变到 2
      if (rect.top >= windowHeight) {
        // 还没进入视口
        sectionProgress[key as keyof typeof sectionProgress] = 0
      } else if (rect.bottom <= 0) {
        // 已经完全离开视口
        sectionProgress[key as keyof typeof sectionProgress] = 2
      } else if (rect.top <= 0 && rect.bottom >= windowHeight) {
        // 完全在视口中
        sectionProgress[key as keyof typeof sectionProgress] = 1
      } else if (rect.top > 0) {
        // 正在进入视口
        sectionProgress[key as keyof typeof sectionProgress] = 1 - (rect.top / windowHeight)
      } else {
        // 正在离开视口
        sectionProgress[key as keyof typeof sectionProgress] = 1 + (1 - rect.bottom / windowHeight)
      }
    }
  })
}

// 计算区块样式
const getSectionStyle = (key: string) => {
  const progress = sectionProgress[key as keyof typeof sectionProgress]
  
  // 进入时（0->1）：从下方淡入
  // 停留时（1）：完全显示
  // 离开时（1->2）：向上淡出并缩小
  
  if (progress <= 1) {
    // 进入阶段
    const enterProgress = Math.min(progress * 1.5, 1) // 加速进入
    return {
      opacity: enterProgress,
      transform: `translateY(${(1 - enterProgress) * 60}px)`,
    }
  } else {
    // 离开阶段
    const leaveProgress = progress - 1
    return {
      opacity: 1 - leaveProgress * 0.8,
      transform: `translateY(${-leaveProgress * 80}px) scale(${1 - leaveProgress * 0.05})`,
      filter: `blur(${leaveProgress * 3}px)`,
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll() // 初始化
})

// 响应式检测
const isMobile = ref(window.innerWidth < 768)
onMounted(() => {
  const checkMobile = () => { isMobile.value = window.innerWidth < 768 }
  window.addEventListener('resize', checkMobile)
})

// 促销活动
interface Promo {
  id: number
  name: string
  description: string
  end_date: string
}
const currentPromos = ref<Promo[]>([])
const loadPromos = async () => {
  try {
    const res = await promoApi.getCurrent()
    if (res.code === 200) currentPromos.value = res.data || []
  } catch { /* ignore */ }
}
onMounted(loadPromos)

// 后台可配置内容
const heroContent = reactive({
  title: '茶企专属 ERP 管理系统',
  subtitle: '专为茶叶行业打造，覆盖进销存、财务、客户、报表全流程管理',
  ctaText: '免费试用 7 天',
  secondaryText: '预约演示'
})

// 加载首页配置
const loadHomepageConfig = async () => {
  try {
    const res = await settingApi.getHomepage()
    if (res.code === 200 && res.data) {
      const d = res.data
      
      // Hero 区文案配置
      if (d.home_hero_title) heroContent.title = d.home_hero_title
      if (d.home_hero_subtitle) heroContent.subtitle = d.home_hero_subtitle
      if (d.home_cta_text) heroContent.ctaText = d.home_cta_text
      if (d.home_secondary_text) heroContent.secondaryText = d.home_secondary_text
      
      // Showcase 区配置
      if (d.showcase_tag) pageConfig.showcaseTag = d.showcase_tag
      if (d.showcase_title) pageConfig.showcaseTitle = d.showcase_title
      if (d.showcase_subtitle) pageConfig.showcaseSubtitle = d.showcase_subtitle
      if (d.mockup_laptop_image) mockupConfig.laptopImage = d.mockup_laptop_image
      if (d.mockup_phone_image) mockupConfig.phoneImage = d.mockup_phone_image
      
      // Features 区配置
      if (d.features_tag) pageConfig.featuresTag = d.features_tag
      if (d.features_title) pageConfig.featuresTitle = d.features_title
      if (d.features_subtitle) pageConfig.featuresSubtitle = d.features_subtitle
      if (d.features_list && Array.isArray(d.features_list) && d.features_list.length > 0) {
        features.value = d.features_list
      }
      
      // AI Demo 区配置
      if (d.ai_section_tag) pageConfig.aiSectionTag = d.ai_section_tag
      if (d.ai_section_title) pageConfig.aiSectionTitle = d.ai_section_title
      if (d.ai_section_subtitle) pageConfig.aiSectionSubtitle = d.ai_section_subtitle
      
      // Testimonials 区配置
      if (d.testimonials_tag) pageConfig.testimonialsTag = d.testimonials_tag
      if (d.testimonials_title) pageConfig.testimonialsTitle = d.testimonials_title
      if (d.testimonials_list && Array.isArray(d.testimonials_list) && d.testimonials_list.length > 0) {
        testimonials.value = d.testimonials_list
      }
      
      // CTA 区配置
      if (d.cta_title) pageConfig.ctaTitle = d.cta_title
      if (d.cta_subtitle) pageConfig.ctaSubtitle = d.cta_subtitle
      if (d.cta_button_text) pageConfig.ctaButtonText = d.cta_button_text
      if (d.cta_secondary_text) pageConfig.ctaSecondaryText = d.cta_secondary_text
      
      // Footer 配置
      if (d.footer_brand_name) pageConfig.footerBrandName = d.footer_brand_name
      if (d.footer_brand_slogan) pageConfig.footerBrandSlogan = d.footer_brand_slogan
      if (d.footer_copyright) pageConfig.footerCopyright = d.footer_copyright
      if (d.footer_links && Array.isArray(d.footer_links) && d.footer_links.length > 0) {
        footerLinks.value = d.footer_links
      }
    }
  } catch { /* 使用默认值 */ }
}

onMounted(() => {
  loadHomepageConfig()
})

// 核心功能模块（从后台加载）
const features = ref([
  {
    icon: '📦',
    title: '智能采购',
    description: '供应商比价、自动补货建议、采购成本分析',
    features: ['多供应商比价', '智能补货预测', 'AI 成本优化']
  },
  {
    icon: '✅',
    title: '多级审批',
    description: '移动端审批、流程合规、实时通知提醒',
    features: ['手机一键审批', '自定义流程', '操作留痕']
  },
  {
    icon: '💰',
    title: '合规财务',
    description: '标准财务报表、成本核算、税务管理',
    features: ['一键生成报表', '多维成本分析', '应收应付管理']
  },
  {
    icon: '🤖',
    title: 'AI 经营大脑',
    description: '自然语言查询、销量预测、智能决策建议',
    features: ['对话式查数据', 'AI 销量预测', '经营诊断报告']
  }
])

// 客户评价（从后台加载）
const testimonials = ref([
  {
    content: '系统非常好用，AI 助手帮我们节省了大量统计时间，强烈推荐！',
    author: '张总',
    company: '福建某茶业公司'
  },
  {
    content: '移动端审批太方便了，出差在外也能及时处理订单。',
    author: '李经理',
    company: '杭州某茶叶批发商'
  },
  {
    content: '财务报表一键生成，再也不用加班做账了。',
    author: '王会计',
    company: '云南某普洱茶厂'
  }
])

// 页脚链接（从后台加载）
const footerLinks = ref([
  {
    title: '产品',
    links: [
      { text: '功能介绍', href: '/features' },
      { text: '价格方案', href: '/pricing' }
    ]
  },
  {
    title: '支持',
    links: [
      { text: '使用文档', href: '/docs' },
      { text: '常见问题', href: '/faq' }
    ]
  },
  {
    title: '联系我们',
    links: [
      { text: '客服热线', href: '/contact' },
      { text: '商务合作', href: '/business' }
    ]
  }
])
</script>

<template>
  <div class="home">
    <!-- 沉浸式导航栏 -->
    <header :class="navClass">
      <div class="nav-content">
        <div class="logo">
          <span class="logo-icon">🍃</span>
          <span class="logo-text">茗管家</span>
        </div>
        <nav class="nav-links">
          <a href="#features">功能特点</a>
          <a href="#ai-demo">AI 演示</a>
          <a @click="router.push('/pricing')">价格方案</a>
        </nav>
        <NSpace class="nav-actions">
          <template v-if="userStore.token">
            <NButton text @click="router.push('/dashboard')">控制台</NButton>
            <NButton @click="userStore.logout()">退出</NButton>
          </template>
          <template v-else>
            <NButton text @click="router.push('/login')">登录</NButton>
            <NButton type="primary" @click="router.push('/register')">免费注册</NButton>
          </template>
        </NSpace>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
      <!-- 粒子树背景 -->
      <TeaParticles />
      
      <!-- 文字内容（叠加在背景上） -->
      <div class="hero-content">
        <div class="hero-text" :ref="el => observe(el as HTMLElement)">
          <h1>{{ heroContent.title }}</h1>
          <p>{{ heroContent.subtitle }}</p>
          
          <NSpace size="large" class="hero-actions">
            <NButton 
              type="primary" 
              size="large" 
              class="btn-glow"
              @click="router.push('/register')"
            >
              {{ heroContent.ctaText }}
            </NButton>
            <NButton 
              size="large" 
              ghost
              @click="router.push('/pricing')"
            >
              {{ heroContent.secondaryText }}
            </NButton>
          </NSpace>
          
          <!-- 促销横幅 -->
          <div v-if="currentPromos.length" class="promo-banner">
            <div v-for="promo in currentPromos" :key="promo.id" class="promo-item">
              🎉 {{ promo.name }}：{{ promo.description }}
              <span class="promo-end">
                截止 {{ new Date(promo.end_date).toLocaleDateString('zh-CN') }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 向下滚动提示 -->
      <div class="scroll-hint">
        <span>向下探索</span>
        <div class="scroll-arrow"></div>
      </div>
    </section>

    <!-- 产品多端展示区 -->
    <section 
      id="showcase" 
      ref="showcaseRef" 
      class="showcase-section section-transition"
      :style="getSectionStyle('showcase')"
    >
      <div class="section-container">
        <div class="section-header" :ref="el => observe(el as HTMLElement)">
          <span class="section-tag">{{ pageConfig.showcaseTag }}</span>
          <h2>{{ pageConfig.showcaseTitle }}</h2>
          <p>{{ pageConfig.showcaseSubtitle }}</p>
        </div>
        
        <div class="mockup-display" :ref="el => observe(el as HTMLElement)" data-delay="200">
          <DeviceMockup :config="mockupConfig" />
        </div>
      </div>
    </section>

    <!-- 核心功能板块 -->
    <section 
      id="features" 
      ref="featuresRef"
      class="features-section section-transition"
      :style="getSectionStyle('features')"
    >
      <div class="section-container">
        <div class="section-header" :ref="el => observe(el as HTMLElement)">
          <span class="section-tag">{{ pageConfig.featuresTag }}</span>
          <h2>{{ pageConfig.featuresTitle }}</h2>
          <p>{{ pageConfig.featuresSubtitle }}</p>
        </div>
        
        <div class="features-grid">
          <FeatureCard
            v-for="(f, i) in features"
            :key="i"
            :icon="f.icon"
            :title="f.title"
            :description="f.description"
            :features="f.features"
            :delay="i * 100"
            :ref="el => observe((((el as any)?.$el) ?? el) as HTMLElement)"
          />
        </div>
      </div>
    </section>

    <!-- AI 交互演示区 -->
    <section 
      id="ai-demo" 
      ref="aiDemoRef"
      class="ai-section section-transition"
      :style="getSectionStyle('aiDemo')"
    >
      <div class="section-container">
        <div class="section-header light" :ref="el => observe(el as HTMLElement)">
          <span class="section-tag">{{ pageConfig.aiSectionTag }}</span>
          <h2>{{ pageConfig.aiSectionTitle }}</h2>
          <p>{{ pageConfig.aiSectionSubtitle }}</p>
        </div>
        
        <div :ref="el => observe(el as HTMLElement)" data-delay="200">
          <AiDemo />
        </div>
      </div>
    </section>

    <!-- 客户评价 -->
    <section 
      ref="testimonialsRef"
      class="testimonials-section section-transition"
      :style="getSectionStyle('testimonials')"
    >
      <div class="section-container">
        <div class="section-header" :ref="el => observe(el as HTMLElement)">
          <span class="section-tag">{{ pageConfig.testimonialsTag }}</span>
          <h2>{{ pageConfig.testimonialsTitle }}</h2>
        </div>
        
        <div class="testimonials-grid">
          <div 
            v-for="(t, i) in testimonials" 
            :key="i" 
            class="testimonial-card"
            :ref="el => observe(el as HTMLElement)"
            :data-delay="i * 100"
          >
            <div class="quote">"</div>
            <p class="content">{{ t.content }}</p>
            <div class="author">
              <div class="avatar">{{ t.author[0] }}</div>
              <div class="info">
                <div class="name">{{ t.author }}</div>
                <div class="company">{{ t.company }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA 板块 -->
    <section 
      ref="ctaRef"
      class="cta-section"
    >
      <div class="cta-bg"></div>
      <div class="section-container" :ref="el => observe(el as HTMLElement)">
        <h2>{{ pageConfig.ctaTitle }}</h2>
        <p>{{ pageConfig.ctaSubtitle }}</p>
        <NSpace size="large" justify="center">
          <NButton 
            type="primary" 
            size="large" 
            class="btn-glow"
            @click="router.push('/register')"
          >
            {{ pageConfig.ctaButtonText }}
          </NButton>
          <NButton 
            size="large"
            @click="router.push('/pricing')"
          >
            {{ pageConfig.ctaSecondaryText }}
          </NButton>
        </NSpace>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-brand">
          <div class="logo">🍃 {{ pageConfig.footerBrandName }}</div>
          <p>{{ pageConfig.footerBrandSlogan }}</p>
        </div>
        <div class="footer-links">
          <div 
            v-for="(group, gi) in footerLinks" 
            :key="gi" 
            class="link-group"
          >
            <h4>{{ group.title }}</h4>
            <template v-for="(link, li) in group.links" :key="li">
              <router-link 
                v-if="link.href.startsWith('/')" 
                :to="link.href"
              >{{ link.text }}</router-link>
              <a 
                v-else 
                :href="link.href"
                target="_blank"
              >{{ link.text }}</a>
            </template>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>{{ pageConfig.footerCopyright }}</p>
      </div>
    </footer>
  </div>
</template>

<style>
/* 全局滚动动效 */
.scroll-reveal {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.scroll-reveal.revealed {
  opacity: 1;
  transform: translateY(0);
}
.scroll-reveal[data-delay="100"] { transition-delay: 100ms; }
.scroll-reveal[data-delay="200"] { transition-delay: 200ms; }
.scroll-reveal[data-delay="300"] { transition-delay: 300ms; }

/* 区块过渡效果 */
.section-transition {
  will-change: opacity, transform, filter;
  transition: opacity 0.15s ease-out, transform 0.15s ease-out, filter 0.15s ease-out;
}
</style>

<style scoped>
/* ========== 基础变量 ========== */
.home {
  --forest-green: #1a472a;
  --deep-green: #050a12;  /* 深邃夜空背景，更适合辉光效果 */
  --cyber-blue: #00F2FF;
  --cyber-green: #00FF88;
  --gold: #d4af37;
  --light-gold: #f0c850;
  min-height: 100vh;
  background: var(--deep-green);
  color: #fff;
  overflow-x: hidden;
}

/* ========== 导航栏 ========== */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 70px;
  z-index: 1000;
  transition: all 0.3s;
}

.nav-scrolled {
  background: rgba(15, 42, 26, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 22px;
  font-weight: 700;
}

.logo-icon {
  font-size: 28px;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-links a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
}

.nav-links a:hover {
  color: var(--gold);
}

.nav-actions {
  display: flex;
}

/* ========== Hero Section ========== */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 100px 40px 60px;
  background: #050a12;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  justify-content: flex-start;
  padding-left: 5%;
  pointer-events: none;  /* 让鼠标事件穿透到粒子树 */
}

.hero-text {
  max-width: 600px;
  text-align: left;
  pointer-events: auto;  /* 文字区域可交互 */
}

.hero-text h1 {
  font-size: 64px;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #fff 0%, #00eeff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ========== Showcase Section ========== */
.showcase-section {
  background: linear-gradient(180deg, #050a12 0%, #0a1a10 100%);
  padding: 120px 0 80px;
}

.mockup-display {
  display: flex;
  justify-content: center;
  align-items: center;
  perspective: 2000px;
  margin-top: 60px;
  transform: scale(1.1); /* 稍微放大设备展示 */
}

.hero-text p {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 40px;
  line-height: 1.6;
}

.hero-actions {
  margin-bottom: 40px;
}

.btn-glow {
  background: linear-gradient(135deg, var(--gold), var(--light-gold)) !important;
  border: none !important;
  color: var(--deep-green) !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 20px rgba(212, 175, 55, 0.4);
  transition: all 0.3s !important;
}

.btn-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(212, 175, 55, 0.6);
}

.promo-banner {
  display: inline-block;
  padding: 16px 24px;
  background: rgba(212, 175, 55, 0.15);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 12px;
}

.promo-item {
  color: var(--gold);
  font-size: 14px;
}

.promo-end {
  margin-left: 16px;
  opacity: 0.7;
  font-size: 12px;
}

.scroll-hint {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.scroll-arrow {
  width: 20px;
  height: 20px;
  border-right: 2px solid rgba(255, 255, 255, 0.5);
  border-bottom: 2px solid rgba(255, 255, 255, 0.5);
  transform: rotate(45deg);
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: rotate(45deg) translateY(0); }
  50% { transform: rotate(45deg) translateY(8px); }
}

/* ========== 通用 Section ========== */
.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 100px 40px;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-tag {
  display: inline-block;
  padding: 6px 16px;
  background: rgba(212, 175, 55, 0.15);
  color: var(--gold);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 40px;
  font-weight: 700;
  margin-bottom: 16px;
}

.section-header p {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
}

.section-header.light h2 {
  color: #fff;
}

/* ========== Features Section ========== */
.features-section {
  background: linear-gradient(180deg, var(--forest-green) 0%, var(--deep-green) 100%);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

/* ========== AI Section ========== */
.ai-section {
  background: linear-gradient(180deg, var(--deep-green) 0%, var(--forest-green) 100%);
  position: relative;
  overflow: hidden;
}

/* ========== Testimonials ========== */
.testimonials-section {
  background: var(--deep-green);
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.testimonial-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 32px;
  position: relative;
}

.quote {
  font-size: 60px;
  color: var(--gold);
  opacity: 0.3;
  position: absolute;
  top: 10px;
  left: 20px;
  line-height: 1;
}

.testimonial-card .content {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.7;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--gold), var(--light-gold));
  color: var(--deep-green);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.name {
  font-weight: 600;
  margin-bottom: 2px;
}

.company {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* ========== CTA Section ========== */
.cta-section {
  position: relative;
  text-align: center;
  padding: 120px 40px;
  background: var(--forest-green);
  overflow: hidden;
}

.cta-bg {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(212, 175, 55, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 50%, rgba(74, 222, 128, 0.1) 0%, transparent 50%);
}

.cta-section h2 {
  font-size: 44px;
  font-weight: 700;
  margin-bottom: 16px;
  position: relative;
}

.cta-section p {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 40px;
  position: relative;
}

/* ========== Footer ========== */
.footer {
  background: #0a1a10;
  padding: 60px 40px 24px;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  padding-bottom: 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-brand .logo {
  margin-bottom: 12px;
}

.footer-brand p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.footer-links {
  display: flex;
  gap: 80px;
}

.link-group h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.link-group a,
.link-group :deep(a) {
  display: block;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  text-decoration: none;
  margin-bottom: 10px;
  cursor: pointer;
  transition: color 0.2s;
}

.link-group a:hover,
.link-group :deep(a):hover {
  color: var(--gold);
}

.footer-bottom {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 24px;
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
}

/* ========== Responsive ========== */
@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .hero-text h1 {
    font-size: 40px;
  }
  
  .hero-mockup {
    display: none;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .testimonials-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .nav-content {
    padding: 0 20px;
  }
  
  .nav-links {
    display: none;
  }
  
  .hero {
    padding: 100px 20px 60px;
  }
  
  .hero-text h1 {
    font-size: 32px;
  }
  
  .hero-text p {
    font-size: 16px;
  }
  
  .section-container {
    padding: 60px 20px;
  }
  
  .section-header h2 {
    font-size: 28px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 40px;
  }
  
  .footer-links {
    flex-wrap: wrap;
    gap: 40px;
  }
}
</style>
