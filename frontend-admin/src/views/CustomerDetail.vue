<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NDescriptions, NDescriptionsItem, NButton, NSpace, NDataTable, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { adminApi } from '@/api'

const route = useRoute()
const router = useRouter()
const message = useMessage()

interface License {
  id: number
  license_key: string
  plan_type: string
  status: string
  created_at: string
  expire_date: string
}

interface CustomerDetail {
  id: number
  username: string
  email: string
  company_name: string
  contact_name: string
  phone: string
  address: string
  created_at: string
  licenses: License[]
}

const loading = ref(false)
const customer = ref<CustomerDetail | null>(null)

const planTypeMap: Record<string, string> = {
  monthly: '月度版',
  yearly: '年度版',
  lifetime: '终身版',
  trial: '试用版',
  promo_free: '限免版',
  free_forever: '永久免费',
}

const statusMap: Record<string, { label: string; type: 'success' | 'warning' | 'error' | 'info' }> = {
  pending: { label: '待激活', type: 'warning' },
  active: { label: '已激活', type: 'success' },
  expired: { label: '已过期', type: 'error' },
  revoked: { label: '已吊销', type: 'error' },
}

const licenseColumns: DataTableColumns<License> = [
  { title: '授权码', key: 'license_key', width: 280, ellipsis: { tooltip: true } },
  { 
    title: '版本', 
    key: 'plan_type', 
    width: 100,
    render: (row) => planTypeMap[row.plan_type] || row.plan_type
  },
  { 
    title: '状态', 
    key: 'status', 
    width: 100,
    render: (row) => {
      const s = statusMap[row.status] || { label: row.status, type: 'info' }
      return h(NTag, { type: s.type, size: 'small' }, () => s.label)
    }
  },
  { 
    title: '到期时间', 
    key: 'expire_date',
    width: 120,
    render: (row) => row.expire_date ? new Date(row.expire_date).toLocaleDateString('zh-CN') : '永久'
  },
  { 
    title: '创建时间', 
    key: 'created_at',
    width: 160,
    render: (row) => new Date(row.created_at).toLocaleString('zh-CN')
  },
]

import { h } from 'vue'

const loadData = async () => {
  const id = Number(route.params.id)
  if (!id) return
  
  loading.value = true
  try {
    const res = await adminApi.getCustomer(id)
    if (res.code === 200) {
      customer.value = res.data
    }
  } catch (e) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div>
    <NSpace align="center" style="margin-bottom: 24px">
      <NButton @click="router.back()">← 返回</NButton>
      <h2 style="margin: 0">客户详情</h2>
    </NSpace>
    
    <NCard title="基本信息" style="margin-bottom: 16px">
      <NDescriptions :column="3" v-if="customer">
        <NDescriptionsItem label="用户名">{{ customer.username }}</NDescriptionsItem>
        <NDescriptionsItem label="企业名称">{{ customer.company_name || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="联系人">{{ customer.contact_name || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="邮箱">{{ customer.email }}</NDescriptionsItem>
        <NDescriptionsItem label="电话">{{ customer.phone || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="注册时间">
          {{ customer.created_at ? new Date(customer.created_at).toLocaleString('zh-CN') : '-' }}
        </NDescriptionsItem>
        <NDescriptionsItem label="地址" :span="3">{{ customer.address || '-' }}</NDescriptionsItem>
      </NDescriptions>
    </NCard>
    
    <NCard title="授权记录">
      <NDataTable
        :columns="licenseColumns"
        :data="customer?.licenses || []"
        :loading="loading"
        :bordered="false"
      />
    </NCard>
  </div>
</template>

