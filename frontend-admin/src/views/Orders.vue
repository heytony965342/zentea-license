<script setup lang="ts">
/**
 * 订单审核管理页面
 */
import { ref, onMounted, h } from 'vue'
import { 
  NCard, NDataTable, NButton, NSpace, NTag, NPagination, NSelect,
  NModal, NDescriptions, NDescriptionsItem, NInput, NImage,
  useMessage, useDialog
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { request } from '@/api/request'

const message = useMessage()
const dialog = useDialog()

interface Order {
  id: number
  order_no: string
  user_id: number
  user?: {
    username: string
    company_name: string
  }
  plan_type: string
  amount: number
  status: string
  payment_proof?: string
  promo_code?: string
  notes?: string
  created_at: string
  paid_at?: string
}

const loading = ref(false)
const orders = ref<Order[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const statusFilter = ref<string | null>(null)

// 详情弹窗
const showDetail = ref(false)
const currentOrder = ref<Order | null>(null)
const rejectReason = ref('')

const planTypeMap: Record<string, string> = {
  monthly: '月度版',
  yearly: '年度版',
  lifetime: '终身版',
  trial: '试用版',
}

const statusMap: Record<string, { label: string; type: 'success' | 'warning' | 'error' | 'info' }> = {
  pending: { label: '待审核', type: 'warning' },
  paid: { label: '已完成', type: 'success' },
  cancelled: { label: '已取消', type: 'error' },
  refunded: { label: '已退款', type: 'info' },
}

const statusOptions = [
  { label: '全部', value: null },
  { label: '待审核', value: 'pending' },
  { label: '已完成', value: 'paid' },
  { label: '已取消', value: 'cancelled' },
]

const columns: DataTableColumns<Order> = [
  { title: '订单号', key: 'order_no', width: 180 },
  { 
    title: '客户', 
    key: 'user',
    width: 150,
    render: (row) => row.user?.company_name || row.user?.username || `用户#${row.user_id}`
  },
  { 
    title: '套餐', 
    key: 'plan_type', 
    width: 90,
    render: (row) => planTypeMap[row.plan_type] || row.plan_type
  },
  { 
    title: '金额', 
    key: 'amount', 
    width: 90,
    render: (row) => row.amount > 0 ? `¥${row.amount}` : '免费'
  },
  { 
    title: '状态', 
    key: 'status', 
    width: 90,
    render: (row) => {
      const s = statusMap[row.status] || { label: row.status, type: 'info' }
      return h(NTag, { type: s.type, size: 'small' }, () => s.label)
    }
  },
  { 
    title: '支付凭证', 
    key: 'payment_proof',
    width: 90,
    render: (row) => row.payment_proof ? '已上传' : '-'
  },
  { 
    title: '创建时间', 
    key: 'created_at',
    width: 160,
    render: (row) => new Date(row.created_at).toLocaleString('zh-CN')
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row) => h(NSpace, { size: 'small' }, () => [
      h(NButton, { size: 'small', onClick: () => viewDetail(row) }, () => '详情'),
      row.status === 'pending' && h(NButton, { size: 'small', type: 'primary', onClick: () => handleApprove(row) }, () => '通过'),
      row.status === 'pending' && h(NButton, { size: 'small', type: 'error', onClick: () => handleReject(row) }, () => '拒绝'),
    ])
  },
]

const loadData = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const res = await request.get('/orders/admin/list', params)
    if (res.code === 200) {
      orders.value = res.data.items
      total.value = res.data.total
    }
  } catch (e) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (order: Order) => {
  currentOrder.value = order
  showDetail.value = true
}

const handleApprove = (order: Order) => {
  dialog.warning({
    title: '确认审核通过',
    content: `确定通过订单 ${order.order_no} 吗？通过后将自动生成授权码。`,
    positiveText: '确认通过',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const res = await request.post(`/orders/admin/${order.id}/approve`)
        if (res.code === 200) {
          message.success('审核通过，授权码已生成')
          loadData()
        } else {
          message.error(res.message || '操作失败')
        }
      } catch (e) {
        message.error('操作失败')
      }
    },
  })
}

const handleReject = (order: Order) => {
  currentOrder.value = order
  rejectReason.value = ''
  
  dialog.warning({
    title: '拒绝订单',
    content: () => h('div', [
      h('p', '请输入拒绝原因：'),
      h(NInput, {
        value: rejectReason.value,
        'onUpdate:value': (v: string) => { rejectReason.value = v },
        type: 'textarea',
        rows: 3,
      }),
    ]),
    positiveText: '确认拒绝',
    negativeText: '取消',
    onPositiveClick: async () => {
      if (!rejectReason.value.trim()) {
        message.warning('请输入拒绝原因')
        return false
      }
      try {
        const res = await request.post(`/orders/admin/${order.id}/reject?reason=${encodeURIComponent(rejectReason.value)}`)
        if (res.code === 200) {
          message.success('已拒绝')
          loadData()
        } else {
          message.error(res.message || '操作失败')
        }
      } catch (e) {
        message.error('操作失败')
      }
    },
  })
}

onMounted(loadData)
</script>

<template>
  <div>
    <NSpace justify="space-between" align="center" style="margin-bottom: 24px">
      <h2 style="margin: 0">订单审核</h2>
      <NSelect
        v-model:value="statusFilter"
        :options="statusOptions"
        style="width: 150px"
        placeholder="筛选状态"
        @update:value="loadData"
      />
    </NSpace>
    
    <NCard>
      <NDataTable
        :columns="columns"
        :data="orders"
        :loading="loading"
        :bordered="false"
      />
      
      <div style="margin-top: 16px; display: flex; justify-content: flex-end">
        <NPagination
          v-model:page="page"
          v-model:page-size="pageSize"
          :item-count="total"
          :page-sizes="[20, 50, 100]"
          show-size-picker
          @update:page="loadData"
          @update:page-size="loadData"
        />
      </div>
    </NCard>
    
    <!-- 订单详情弹窗 -->
    <NModal v-model:show="showDetail" title="订单详情" preset="card" style="width: 600px">
      <NDescriptions v-if="currentOrder" :column="2" label-placement="left">
        <NDescriptionsItem label="订单号">{{ currentOrder.order_no }}</NDescriptionsItem>
        <NDescriptionsItem label="状态">
          <NTag :type="statusMap[currentOrder.status]?.type || 'default'">
            {{ statusMap[currentOrder.status]?.label || currentOrder.status }}
          </NTag>
        </NDescriptionsItem>
        <NDescriptionsItem label="客户">
          {{ currentOrder.user?.company_name || currentOrder.user?.username }}
        </NDescriptionsItem>
        <NDescriptionsItem label="套餐">
          {{ planTypeMap[currentOrder.plan_type] || currentOrder.plan_type }}
        </NDescriptionsItem>
        <NDescriptionsItem label="金额">
          {{ currentOrder.amount > 0 ? `¥${currentOrder.amount}` : '免费' }}
        </NDescriptionsItem>
        <NDescriptionsItem label="促销码">
          {{ currentOrder.promo_code || '-' }}
        </NDescriptionsItem>
        <NDescriptionsItem label="创建时间">
          {{ new Date(currentOrder.created_at).toLocaleString('zh-CN') }}
        </NDescriptionsItem>
        <NDescriptionsItem label="完成时间">
          {{ currentOrder.paid_at ? new Date(currentOrder.paid_at).toLocaleString('zh-CN') : '-' }}
        </NDescriptionsItem>
        <NDescriptionsItem label="支付凭证" :span="2">
          <NImage 
            v-if="currentOrder.payment_proof" 
            :src="currentOrder.payment_proof" 
            width="200"
            style="max-height: 300px"
          />
          <span v-else>未上传</span>
        </NDescriptionsItem>
        <NDescriptionsItem label="备注" :span="2">
          <pre style="white-space: pre-wrap; margin: 0">{{ currentOrder.notes || '-' }}</pre>
        </NDescriptionsItem>
      </NDescriptions>
      
      <template #footer v-if="currentOrder?.status === 'pending'">
        <NSpace justify="end">
          <NButton type="error" @click="handleReject(currentOrder!)">拒绝</NButton>
          <NButton type="primary" @click="handleApprove(currentOrder!)">通过</NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

