import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: () => import('@/views/Layout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
        },
        {
          path: 'customers',
          name: 'Customers',
          component: () => import('@/views/Customers.vue'),
        },
        {
          path: 'customers/:id',
          name: 'CustomerDetail',
          component: () => import('@/views/CustomerDetail.vue'),
        },
        {
          path: 'licenses',
          name: 'Licenses',
          component: () => import('@/views/Licenses.vue'),
        },
        {
          path: 'promos',
          name: 'Promos',
          component: () => import('@/views/Promos.vue'),
        },
        {
          path: 'orders',
          name: 'Orders',
          component: () => import('@/views/Orders.vue'),
        },
        // 内容管理
        {
          path: 'homepage-setting',
          name: 'HomepageSetting',
          component: () => import('@/views/HomepageSetting.vue'),
        },
        {
          path: 'pages',
          name: 'Pages',
          component: () => import('@/views/Pages.vue'),
        },
        {
          path: 'pages/:id',
          name: 'PageEdit',
          component: () => import('@/views/PageEdit.vue'),
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings.vue'),
        },
      ],
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth !== false) {
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

