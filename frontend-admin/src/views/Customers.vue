<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard,
  NDataTable,
  NButton,
  NPagination,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NSwitch,
  NSpace,
  NPopconfirm,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, FormInst } from 'naive-ui'
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
const saving = ref(false)
const customers = ref<Customer[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const generatedPassword = ref<string | null>(null)
const formRef = ref<FormInst | null>(null)

const form = ref({
  username: '',
  email: '',
  password: '', // 仅新建时可填，不填则后端自动生成
  company_name: '',
  contact_name: '',
  phone: '',
  address: '',
  is_active: true,
})

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
    width: 220,
    render: (row) =>
      h(
        NSpace,
        { size: 8 },
        () => [
          h(
            NButton,
            { size: 'small', onClick: () => router.push(`/customers/${row.id}`) },
            () => '详情'
          ),
          h(
            NButton,
            { size: 'small', type: 'primary', onClick: () => openEdit(row.id) },
            () => '编辑'
          ),
          h(
            NPopconfirm,
            {
              onPositiveClick: () => handleDelete(row.id),
            },
            {
              trigger: () =>
                h(
                  NButton,
                  { size: 'small', type: 'error' },
                  () => '删除'
                ),
              default: () => '确认删除该客户？（会同时删除其授权/订单记录）',
            }
          ),
        ]
      )
  },
]

const loadData = async () => {
  loading.value = true
  try {
    const res = await adminApi.getCustomers({ page: page.value, page_size: pageSize.value })
    if (res.code === 200) {
      customers.value = res.data.items
      total.value = res.data.total || 0
    }
  } catch (e) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  generatedPassword.value = null
  form.value = {
    username: '',
    email: '',
    password: '',
    company_name: '',
    contact_name: '',
    phone: '',
    address: '',
    is_active: true,
  }
}

const openCreate = () => {
  isEdit.value = false
  editingId.value = null
  resetForm()
  showModal.value = true
}

const openEdit = async (id: number) => {
  isEdit.value = true
  editingId.value = id
  generatedPassword.value = null
  showModal.value = true
  saving.value = true
  try {
    const res = await adminApi.getCustomer(id)
    if (res.code === 200) {
      form.value.username = res.data.username || ''
      form.value.email = res.data.email || ''
      form.value.password = ''
      form.value.company_name = res.data.company_name || ''
      form.value.contact_name = res.data.contact_name || ''
      form.value.phone = res.data.phone || ''
      form.value.address = res.data.address || ''
      form.value.is_active = !!res.data.is_active
    } else {
      message.error(res.message || '加载详情失败')
    }
  } catch (e) {
    message.error('加载详情失败')
  } finally {
    saving.value = false
  }
}

const handleSubmit = async () => {
  await formRef.value?.validate()

  saving.value = true
  generatedPassword.value = null
  try {
    if (isEdit.value && editingId.value) {
      const res = await adminApi.updateCustomer(editingId.value, {
        username: form.value.username,
        email: form.value.email,
        company_name: form.value.company_name || undefined,
        contact_name: form.value.contact_name || undefined,
        phone: form.value.phone || undefined,
        address: form.value.address || undefined,
        is_active: form.value.is_active,
      })
      if (res.code === 200) {
        message.success('更新成功')
        showModal.value = false
        await loadData()
      } else {
        message.error(res.message || '更新失败')
      }
      return
    }

    const res = await adminApi.createCustomer({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password || undefined,
      company_name: form.value.company_name || undefined,
      contact_name: form.value.contact_name || undefined,
      phone: form.value.phone || undefined,
      address: form.value.address || undefined,
      is_active: form.value.is_active,
    })
    if (res.code === 200) {
      message.success('创建成功')
      generatedPassword.value = res.data?.initial_password || null
      await loadData()
      // 让用户可以复制初始密码（若后端自动生成）
      if (!generatedPassword.value) {
        showModal.value = false
      }
    } else {
      message.error(res.message || '创建失败')
    }
  } catch (e) {
    message.error('操作失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id: number) => {
  try {
    const res = await adminApi.deleteCustomer(id)
    if (res.code === 200) {
      message.success('删除成功')
      if (customers.value.length === 1 && page.value > 1) {
        page.value -= 1
      }
      await loadData()
    } else {
      message.error(res.message || '删除失败')
    }
  } catch {
    message.error('删除失败')
  }
}

const handlePageChange = async (p: number) => {
  page.value = p
  await loadData()
}

const handlePageSizeChange = async (ps: number) => {
  pageSize.value = ps
  page.value = 1
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <div>
    <NSpace align="center" justify="space-between" style="margin-bottom: 24px">
      <h2 style="margin: 0">客户管理</h2>
      <NButton type="primary" @click="openCreate">新建客户</NButton>
    </NSpace>
    
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
          :item-count="total"
          :page-sizes="[20, 50, 100]"
          show-size-picker
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </NCard>

    <NModal v-model:show="showModal" preset="card" style="width: 560px" :title="isEdit ? '编辑客户' : '新建客户'">
      <NForm ref="formRef" :model="form" label-placement="left" label-width="90">
        <NFormItem label="用户名" path="username" :rule="{ required: true, message: '请输入用户名', trigger: ['blur', 'input'] }">
          <NInput v-model:value="form.username" placeholder="请输入用户名" />
        </NFormItem>
        <NFormItem label="邮箱" path="email" :rule="{ required: true, message: '请输入邮箱', trigger: ['blur', 'input'] }">
          <NInput v-model:value="form.email" placeholder="请输入邮箱" />
        </NFormItem>
        <NFormItem v-if="!isEdit" label="初始密码" path="password">
          <NInput v-model:value="form.password" placeholder="不填则自动生成" />
        </NFormItem>
        <NFormItem label="企业名称" path="company_name">
          <NInput v-model:value="form.company_name" placeholder="可选" />
        </NFormItem>
        <NFormItem label="联系人" path="contact_name">
          <NInput v-model:value="form.contact_name" placeholder="可选" />
        </NFormItem>
        <NFormItem label="电话" path="phone">
          <NInput v-model:value="form.phone" placeholder="可选" />
        </NFormItem>
        <NFormItem label="地址" path="address">
          <NInput v-model:value="form.address" placeholder="可选" />
        </NFormItem>
        <NFormItem label="启用" path="is_active">
          <NSwitch v-model:value="form.is_active" />
        </NFormItem>
      </NForm>

      <div v-if="generatedPassword" style="margin-top: 12px; padding: 10px 12px; background: #fffbe6; border: 1px solid #ffe58f; border-radius: 6px">
        <div style="font-weight: 600; margin-bottom: 6px">系统已自动生成初始密码（请及时复制保存）：</div>
        <div style="font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace">
          {{ generatedPassword }}
        </div>
      </div>

      <template #footer>
        <NSpace justify="end">
          <NButton @click="showModal = false">取消</NButton>
          <NButton type="primary" :loading="saving" @click="handleSubmit">
            {{ isEdit ? '保存' : '创建' }}
          </NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

