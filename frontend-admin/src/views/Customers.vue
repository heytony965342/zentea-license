<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NDataTable, NButton, NPagination, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { adminApi } from '@/api'

const router = useRouter()
const message = useMessage()

interface Customer {
  id: number
  username: string
  email: string
  company_name: string
  contact_name: string
  phone: string
  created_at: string
}

const loading = ref(false)
const customers = ref<Customer[]>([])
const page = ref(1)
const pageSize = ref(20)

const columns: DataTableColumns<Customer> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '用户名', key: 'username', width: 120 },
  { title: '企业名称', key: 'company_name', ellipsis: { tooltip: true } },
  { title: '联系人', key: 'contact_name', width: 100 },
  { title: '邮箱', key: 'email', width: 180 },
  { title: '电话', key: 'phone', width: 130 },
  { 
    title: '注册时间', 
    key: 'created_at', 
    width: 160,
    render: (row) => row.created_at ? new Date(row.created_at).toLocaleString('zh-CN') : '-'
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row) => h(
      NButton,
      { size: 'small', onClick: () => router.push(`/customers/${row.id}`) },
      () => '详情'
    )
  },
]

const loadData = async () => {
  loading.value = true
  try {
    const res = await adminApi.getCustomers({ page: page.value, page_size: pageSize.value })
    if (res.code === 200) {
      customers.value = res.data.items
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
    <h2 style="margin-bottom: 24px">客户管理</h2>
    
    <NCard>
      <NDataTable
        :columns="columns"
        :data="customers"
        :loading="loading"
        :bordered="false"
      />
      
      <div style="margin-top: 16px; display: flex; justify-content: flex-end">
        <NPagination
          v-model:page="page"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          show-size-picker
          @update:page="loadData"
          @update:page-size="loadData"
        />
      </div>
    </NCard>
  </div>
</template>

