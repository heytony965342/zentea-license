<script setup lang="ts">
/**
 * 通用页面组件
 * 根据 slug 加载并显示后台配置的页面内容
 */
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import { pageApi } from '@/api'

// 接收 props（用于特定页面路由）
const props = defineProps<{
  slug?: string
}>()

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref('')
const page = ref<{
  slug: string
  title: string
  subtitle: string
  content: string
  meta_description: string
} | null>(null)

// 解析 Markdown 内容为 HTML
const contentHtml = computed(() => {
  if (!page.value?.content) return ''
  return marked(page.value.content)
})

// 获取当前页面 slug
const currentSlug = computed(() => {
  return props.slug || (route.params.slug as string)
})

// 加载页面内容
const loadPage = async () => {
  const slug = currentSlug.value
  if (!slug) {
    error.value = '页面不存在'
    loading.value = false
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const res = await pageApi.getPage(slug)
    if (res.code === 200 && res.data) {
      page.value = res.data
      // 更新页面标题
      document.title = `${res.data.title} - 茗管家`
    } else {
      error.value = res.message || '页面加载失败'
    }
  } catch (e: any) {
    if (e.response?.status === 404) {
      error.value = '页面不存在'
    } else {
      error.value = '页面加载失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 监听路由变化
watch(currentSlug, () => {
  loadPage()
})

onMounted(() => {
  loadPage()
})
</script>

<template>
  <div class="page-view">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-container">
        <a href="/" class="logo">🍃 茗管家</a>
        <div class="nav-links">
          <router-link to="/">首页</router-link>
          <router-link to="/features">功能介绍</router-link>
          <router-link to="/pricing">价格方案</router-link>
          <router-link to="/docs">使用文档</router-link>
          <router-link to="/contact">联系我们</router-link>
        </div>
        <div class="nav-actions">
          <router-link to="/login" class="btn-login">登录</router-link>
          <router-link to="/register" class="btn-register">免费试用</router-link>
        </div>
      </div>
    </nav>
    
    <!-- 页面主体 -->
    <main class="page-main">
      <!-- 加载中 -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">😔</div>
        <h2>{{ error }}</h2>
        <button @click="goHome" class="btn-home">返回首页</button>
      </div>
      
      <!-- 页面内容 -->
      <div v-else-if="page" class="page-content">
        <header class="page-header">
          <h1>{{ page.title }}</h1>
          <p v-if="page.subtitle" class="subtitle">{{ page.subtitle }}</p>
        </header>
        
        <article class="markdown-body" v-html="contentHtml"></article>
      </div>
    </main>
    
    <!-- 页脚 -->
    <footer class="page-footer">
      <div class="footer-container">
        <div class="footer-brand">
          <span class="brand-name">🍃 茗管家</span>
          <span class="brand-slogan">茶企专属 ERP 管理系统</span>
        </div>
        <div class="footer-links">
          <div class="link-group">
            <h4>产品</h4>
            <router-link to="/features">功能介绍</router-link>
            <router-link to="/pricing">价格方案</router-link>
          </div>
          <div class="link-group">
            <h4>支持</h4>
            <router-link to="/docs">使用文档</router-link>
            <router-link to="/faq">常见问题</router-link>
          </div>
          <div class="link-group">
            <h4>联系我们</h4>
            <router-link to="/contact">客服热线</router-link>
            <router-link to="/business">商务合作</router-link>
          </div>
        </div>
        <div class="footer-copyright">
          © 2025 茗管家 ZenTea ERP. All rights reserved.
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.page-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0a0f0d 0%, #1a2f23 100%);
}

/* 导航栏 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(10, 15, 13, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-links a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: #4ade80;
}

.nav-actions {
  display: flex;
  gap: 12px;
}

.btn-login {
  padding: 8px 16px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 14px;
}

.btn-register {
  padding: 8px 20px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  text-decoration: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

/* 页面主体 */
.page-main {
  flex: 1;
  padding-top: 80px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  padding: 100px 24px 60px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: rgba(255, 255, 255, 0.6);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #4ade80;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.error-state h2 {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 24px;
}

.btn-home {
  padding: 12px 32px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-home:hover {
  transform: scale(1.05);
}

/* 页面内容 */
.page-content {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 48px;
}

.page-header {
  text-align: center;
  margin-bottom: 48px;
  padding-bottom: 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.page-header h1 {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
}

.page-header .subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
}

/* Markdown 内容样式 */
.markdown-body {
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.8;
}

.markdown-body :deep(h2) {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  margin-top: 48px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.markdown-body :deep(h3) {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin-top: 32px;
  margin-bottom: 12px;
}

.markdown-body :deep(h4) {
  font-size: 16px;
  font-weight: 600;
  color: #4ade80;
  margin-top: 24px;
  margin-bottom: 8px;
}

.markdown-body :deep(p) {
  margin-bottom: 16px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin-bottom: 16px;
  padding-left: 24px;
}

.markdown-body :deep(li) {
  margin-bottom: 8px;
}

.markdown-body :deep(strong) {
  color: #fff;
  font-weight: 600;
}

.markdown-body :deep(a) {
  color: #4ade80;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin: 32px 0;
}

.markdown-body :deep(code) {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
}

.markdown-body :deep(pre) {
  background: rgba(0, 0, 0, 0.3);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 16px;
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #4ade80;
  padding-left: 16px;
  margin: 16px 0;
  color: rgba(255, 255, 255, 0.7);
}

/* 页脚 */
.page-footer {
  background: rgba(0, 0, 0, 0.3);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 48px 24px 24px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 32px;
}

.brand-name {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
}

.brand-slogan {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.footer-links {
  display: flex;
  gap: 64px;
  margin-bottom: 32px;
}

.link-group h4 {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  margin-bottom: 16px;
}

.link-group a {
  display: block;
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  font-size: 14px;
  margin-bottom: 8px;
  transition: color 0.2s;
}

.link-group a:hover {
  color: #4ade80;
}

.footer-copyright {
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* 响应式 */
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  
  .page-content {
    padding: 24px;
  }
  
  .page-header h1 {
    font-size: 28px;
  }
  
  .footer-links {
    flex-wrap: wrap;
    gap: 32px;
  }
}
</style>

