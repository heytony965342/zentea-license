import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/pricing',
      name: 'Pricing',
      component: () => import('@/views/Pricing.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/licenses',
      name: 'MyLicenses',
      component: () => import('@/views/MyLicenses.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/orders',
      name: 'MyOrders',
      component: () => import('@/views/MyOrders.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/checkout',
      name: 'Checkout',
      component: () => import('@/views/Checkout.vue'),
      meta: { requiresAuth: true },
    },
    // 动态页面（功能介绍、使用文档、常见问题等）
    {
      path: '/features',
      name: 'Features',
      component: () => import('@/views/Page.vue'),
      meta: { requiresAuth: false },
      props: { slug: 'features' },
    },
    {
      path: '/docs',
      name: 'Docs',
      component: () => import('@/views/Page.vue'),
      meta: { requiresAuth: false },
      props: { slug: 'docs' },
    },
    {
      path: '/faq',
      name: 'FAQ',
      component: () => import('@/views/Page.vue'),
      meta: { requiresAuth: false },
      props: { slug: 'faq' },
    },
    {
      path: '/contact',
      name: 'Contact',
      component: () => import('@/views/Page.vue'),
      meta: { requiresAuth: false },
      props: { slug: 'contact' },
    },
    {
      path: '/business',
      name: 'Business',
      component: () => import('@/views/Page.vue'),
      meta: { requiresAuth: false },
      props: { slug: 'business' },
    },
    // 通用页面路由（放在最后）
    {
      path: '/:slug',
      name: 'DynamicPage',
      component: () => import('@/views/Page.vue'),
      meta: { requiresAuth: false },
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth) {
    if (!userStore.token) {
      return next('/login')
    }
    if (!userStore.user) {
      await userStore.fetchUser()
      if (!userStore.user) {
        return next('/login')
      }
    }
  }
  
  next()
})

export default router

