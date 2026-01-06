<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NCard, NDataTable, NButton, NTag, NModal, NForm, NFormItem, NInput, NDatePicker, NSpace, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { request } from '@/api/request'

const message = useMessage()

interface Promo {
  id: number
  name: string
  code: string
  description: string
  start_date: string
  end_date: string
  is_active: boolean
  max_uses: number | null
  current_uses: number
  created_at: string
}

const loading = ref(false)
const promos = ref<Promo[]>([])

// 新建活动
const showCreate = ref(false)
const creating = ref(false)
const createForm = ref({
  name: '',
  code: '',
  description: '',
  start_date: null as number | null,
  end_date: null as number | null,
  max_uses: null as number | null,
})

const columns: DataTableColumns<Promo> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '活动名称', key: 'name', width: 150 },
  { 
    title: '活动码', 
    key: 'code', 
    width: 120,
    render: (row) => h('code', row.code)
  },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { 
    title: '开始时间', 
    key: 'start_date',
    width: 110,
    render: (row) => new Date(row.start_date).toLocaleDateString('zh-CN')
  },
  { 
    title: '结束时间', 
    key: 'end_date',
    width: 110,
    render: (row) => new Date(row.end_date).toLocaleDateString('zh-CN')
  },
  { 
    title: '状态', 
    key: 'is_active', 
    width: 80,
    render: (row) => {
      const now = new Date()
      const start = new Date(row.start_date)
      const end = new Date(row.end_date)
      
      if (!row.is_active) {
        return h(NTag, { type: 'default', size: 'small' }, () => '已停用')
      }
      if (now < start) {
        return h(NTag, { type: 'info', size: 'small' }, () => '未开始')
      }
      if (now > end) {
        return h(NTag, { type: 'error', size: 'small' }, () => '已结束')
      }
      return h(NTag, { type: 'success', size: 'small' }, () => '进行中')
    }
  },
  { 
    title: '使用次数', 
    key: 'uses',
    width: 100,
    render: (row) => `${row.current_uses}${row.max_uses ? `/${row.max_uses}` : ''}`
  },
]

import { h } from 'vue'

const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/admin/promos')
    if (res.code === 200) {
      promos.value = res.data || []
    }
  } catch (e) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!createForm.value.name || !createForm.value.code) {
    message.warning('请填写活动名称和活动码')
    return
  }
  if (!createForm.value.start_date || !createForm.value.end_date) {
    message.warning('请选择活动时间')
    return
  }
  
  creating.value = true
  try {
    const data = {
      name: createForm.value.name,
      code: createForm.value.code,
      description: createForm.value.description,
      start_date: new Date(createForm.value.start_date).toISOString().split('T')[0],
      end_date: new Date(createForm.value.end_date).toISOString().split('T')[0],
      max_uses: createForm.value.max_uses || undefined,
    }
    
    const res = await request.post('/admin/promos', data)
    if (res.code === 200) {
      message.success('创建成功')
      showCreate.value = false
      createForm.value = { name: '', code: '', description: '', start_date: null, end_date: null, max_uses: null }
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

onMounted(loadData)
</script>

<template>
  <div>
    <NSpace justify="space-between" align="center" style="margin-bottom: 24px">
      <h2 style="margin: 0">促销活动</h2>
      <NButton type="primary" @click="showCreate = true">新建活动</NButton>
    </NSpace>
    
    <NCard>
      <NDataTable
        :columns="columns"
        :data="promos"
        :loading="loading"
        :bordered="false"
      />
    </NCard>
    
    <!-- 新建活动弹窗 -->
    <NModal v-model:show="showCreate" title="新建促销活动" preset="card" style="width: 500px">
      <NForm label-placement="left" label-width="80">
        <NFormItem label="活动名称">
          <NInput v-model:value="createForm.name" placeholder="如：2025新年限免" />
        </NFormItem>
        <NFormItem label="活动码">
          <NInput v-model:value="createForm.code" placeholder="如：NY2025" />
        </NFormItem>
        <NFormItem label="描述">
          <NInput v-model:value="createForm.description" type="textarea" placeholder="活动说明" />
        </NFormItem>
        <NFormItem label="开始时间">
          <NDatePicker v-model:value="createForm.start_date" type="date" style="width: 100%" />
        </NFormItem>
        <NFormItem label="结束时间">
          <NDatePicker v-model:value="createForm.end_date" type="date" style="width: 100%" />
        </NFormItem>
        <NFormItem label="限制次数">
          <NInput v-model:value="createForm.max_uses" type="number" placeholder="不填则不限制" />
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

