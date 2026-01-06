<script setup lang="ts">
import { h, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NLayout, NLayoutSider, NLayoutContent, NMenu, NButton, NSpace, NAvatar, NDropdown } from 'naive-ui'
import { 
  HomeOutline, 
  PeopleOutline, 
  KeyOutline, 
  GiftOutline,
  ReceiptOutline,
  LogOutOutline,
  PersonOutline,
  SettingsOutline,
  DocumentTextOutline,
  NewspaperOutline
} from '@vicons/ionicons5'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const menuOptions = [
  {
    label: '仪表盘',
    key: 'Dashboard',
    icon: () => h(HomeOutline),
  },
  {
    label: '客户管理',
    key: 'Customers',
    icon: () => h(PeopleOutline),
  },
  {
    label: '授权管理',
    key: 'Licenses',
    icon: () => h(KeyOutline),
  },
  {
    label: '订单审核',
    key: 'Orders',
    icon: () => h(ReceiptOutline),
  },
  {
    label: '促销活动',
    key: 'Promos',
    icon: () => h(GiftOutline),
  },
  {
    label: '内容管理',
    key: 'content',
    icon: () => h(NewspaperOutline),
    children: [
      {
        label: '首页设置',
        key: 'HomepageSetting',
        icon: () => h(HomeOutline),
      },
      {
        label: '页面管理',
        key: 'Pages',
        icon: () => h(DocumentTextOutline),
      },
    ],
  },
  {
    label: '系统设置',
    key: 'Settings',
    icon: () => h(SettingsOutline),
  },
]

const activeKey = computed(() => route.name as string)

const handleMenuSelect = (key: string) => {
  router.push({ name: key })
}

const userDropdownOptions = [
  { label: '退出登录', key: 'logout', icon: () => h(LogOutOutline) },
]

const handleUserAction = (key: string) => {
  if (key === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<template>
  <NLayout has-sider style="height: 100vh">
    <NLayoutSider
      bordered
      :width="200"
      :native-scrollbar="false"
      style="background: #1a472a"
    >
      <div class="logo">
        <span>🍃 ZenTea License</span>
      </div>
      <NMenu
        :options="menuOptions"
        :value="activeKey"
        :collapsed-width="64"
        :inverted="true"
        @update:value="handleMenuSelect"
      />
    </NLayoutSider>
    
    <NLayout>
      <div class="header">
        <div></div>
        <NDropdown :options="userDropdownOptions" @select="handleUserAction">
          <NSpace align="center" style="cursor: pointer">
            <NAvatar round size="small">
              <PersonOutline />
            </NAvatar>
            <span>{{ userStore.user?.username }}</span>
          </NSpace>
        </NDropdown>
      </div>
      
      <NLayoutContent style="padding: 24px; background: #f5f7fa">
        <router-view />
      </NLayoutContent>
    </NLayout>
  </NLayout>
</template>

<style scoped>
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.header {
  height: 60px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
}
</style>

