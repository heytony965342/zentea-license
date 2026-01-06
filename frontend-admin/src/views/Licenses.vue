<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { 
  NCard, NDataTable, NButton, NSpace, NTag, NModal, NForm, NFormItem, 
  NInput, NSelect, NDatePicker, NPagination, NPopconfirm, useMessage 
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { adminApi } from '@/api'

const message = useMessage()

interface License {
  id: number
  user_id: number
  license_key: string
  plan_type: string
  status: string
  created_at: string
  activated_at: string | null
  expire_date: string | null
  machine_id: string | null
  max_users: number
  notes: string | null
  user?: {
    username: string
    company_name: string
  }
}

const loading = ref(false)
const licenses = ref<License[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 新建授权
const showCreate = ref(false)
const creating = ref(false)
const createForm = ref({
  user_id: null as number | null,
  plan_type: 'yearly',
  expire_date: null as number | null,
  max_users: 5,
  notes: '',
})

const planOptions = [
  { label: '月度版', value: 'monthly' },
  { label: '年度版', value: 'yearly' },
  { label: '终身版', value: 'lifetime' },
  { label: '试用版（7天）', value: 'trial' },
  { label: '限免版', value: 'promo_free' },
  { label: '永久免费', value: 'free_forever' },
]

const statusMap: Record<string, { label: string; type: 'success' | 'warning' | 'error' | 'info' }> = {
  pending: { label: '待激活', type: 'warning' },
  active: { label: '已激活', type: 'success' },
  expired: { label: '已过期', type: 'error' },
  revoked: { label: '已吊销', type: 'error' },
}

const columns: DataTableColumns<License> = [
  { title: 'ID', key: 'id', width: 60 },
  { 
    title: '授权码', 
    key: 'license_key', 
    width: 200, 
    ellipsis: { tooltip: true },
    render: (row) => h('code', { style: 'font-size: 12px' }, row.license_key)
  },
  { 
    title: '客户', 
    key: 'user',
    width: 150,
    render: (row) => row.user?.company_name || row.user?.username || `用户#${row.user_id}`
  },
  { 
    title: '版本', 
    key: 'plan_type', 
    width: 90,
    render: (row) => {
      const opt = planOptions.find(o => o.value === row.plan_type)
      return opt?.label || row.plan_type
    }
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
    title: '到期时间', 
    key: 'expire_date',
    width: 110,
    render: (row) => row.expire_date ? new Date(row.expire_date).toLocaleDateString('zh-CN') : '永久'
  },
  { 
    title: '机器码', 
    key: 'machine_id',
    width: 100,
    ellipsis: { tooltip: true },
    render: (row) => row.machine_id || '-'
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render: (row) => h(NSpace, { size: 'small' }, () => [
      row.status === 'active' && h(
        NPopconfirm,
        { onPositiveClick: () => handleRevoke(row.id) },
        {
          trigger: () => h(NButton, { size: 'small', type: 'error' }, () => '吊销'),
          default: () => '确定吊销此授权？'
        }
      ),
      row.machine_id && h(
        NPopconfirm,
        { onPositiveClick: () => handleUnbind(row.id) },
        {
          trigger: () => h(NButton, { size: 'small' }, () => '解绑'),
          default: () => '确定解除机器绑定？'
        }
      ),
      h(NButton, { size: 'small', onClick: () => handleExtend(row.id) }, () => '续期'),
    ])
  },
]

const loadData = async () => {
  loading.value = true
  try {
    const res = await adminApi.getLicenses({ page: page.value, page_size: pageSize.value })
    if (res.code === 200) {
      licenses.value = res.data.items
      total.value = res.data.total
    }
  } catch (e) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!createForm.value.user_id) {
    message.warning('请输入客户ID')
    return
  }
  
  creating.value = true
  try {
    const data: any = {
      user_id: createForm.value.user_id,
      plan_type: createForm.value.plan_type,
      max_users: createForm.value.max_users,
      notes: createForm.value.notes || undefined,
    }
    if (createForm.value.expire_date) {
      data.expire_date = new Date(createForm.value.expire_date).toISOString().split('T')[0]
    }
    
    const res = await adminApi.createLicense(data)
    if (res.code === 200) {
      message.success('创建成功')
      showCreate.value = false
      createForm.value = { user_id: null, plan_type: 'yearly', expire_date: null, max_users: 5, notes: '' }
      loadData()
    } else {
      message.error(res.message || '创建失败')
    }
  } catch (e: any) {
    message.error(e.message || '创建失败')
  } finally {
    creating.value = false
  }
}

const handleRevoke = async (id: number) => {
  try {
    const res = await adminApi.revokeLicense(id, '管理员手动吊销')
    if (res.code === 200) {
      message.success('已吊销')
      loadData()
    }
  } catch (e) {
    message.error('操作失败')
  }
}

const handleUnbind = async (id: number) => {
  try {
    const res = await adminApi.unbindLicense(id)
    if (res.code === 200) {
      message.success('已解绑')
      loadData()
    }
  } catch (e) {
    message.error('操作失败')
  }
}

const handleExtend = async (id: number) => {
  const days = window.prompt('请输入续期天数', '365')
  if (!days) return
  
  try {
    const res = await adminApi.extendLicense(id, parseInt(days))
    if (res.code === 200) {
      message.success('续期成功')
      loadData()
    }
  } catch (e) {
    message.error('操作失败')
  }
}

onMounted(loadData)
</script>

<template>
  <div>
    <NSpace justify="space-between" align="center" style="margin-bottom: 24px">
      <h2 style="margin: 0">授权管理</h2>
      <NButton type="primary" @click="showCreate = true">新建授权</NButton>
    </NSpace>
    
    <NCard>
      <NDataTable
        :columns="columns"
        :data="licenses"
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
    
    <!-- 新建授权弹窗 -->
    <NModal v-model:show="showCreate" title="新建授权" preset="card" style="width: 500px">
      <NForm label-placement="left" label-width="80">
        <NFormItem label="客户ID">
          <NInput v-model:value="createForm.user_id" type="number" placeholder="输入客户ID" />
        </NFormItem>
        <NFormItem label="版本类型">
          <NSelect v-model:value="createForm.plan_type" :options="planOptions" />
        </NFormItem>
        <NFormItem label="到期日期">
          <NDatePicker v-model:value="createForm.expire_date" type="date" clearable style="width: 100%" />
        </NFormItem>
        <NFormItem label="用户数">
          <NInput v-model:value="createForm.max_users" type="number" />
        </NFormItem>
        <NFormItem label="备注">
          <NInput v-model:value="createForm.notes" type="textarea" />
        </NFormItem>
      </NForm>
      
      <template #footer>
        <NSpace justify="end">
          <NButton @click="showCreate = false">取消</NButton>
          <NButton type="primary" :loading="creating" @click="handleCreate">创建</NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

