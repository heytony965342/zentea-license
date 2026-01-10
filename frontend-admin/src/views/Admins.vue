<script setup lang="ts">
import { ref, onMounted, h, computed } from 'vue'
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
  NTag,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, FormInst } from 'naive-ui'
import { adminApi } from '@/api'
import { useUserStore } from '@/stores/user'

const message = useMessage()
const userStore = useUserStore()

interface AdminUser {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
}

const loading = ref(false)
const saving = ref(false)
const admins = ref<AdminUser[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInst | null>(null)

const form = ref({
  username: '',
  email: '',
  password: '', // 仅新建需要
  is_active: true,
})

const showPwdModal = ref(false)
const pwdFormRef = ref<FormInst | null>(null)
const pwdTarget = ref<AdminUser | null>(null)
const pwdForm = ref({
  new_password: '',
  confirm_password: '',
})

const currentAdminId = computed(() => userStore.user?.id || 0)

const columns: DataTableColumns<AdminUser> = [
  { title: 'ID', key: 'id', width: 70 },
  {
    title: '用户名',
    key: 'username',
    width: 160,
    render: (row) =>
      h(NSpace, { size: 8, align: 'center' }, () => [
        h('span', row.username),
        row.id === currentAdminId.value ? h(NTag, { size: 'small', type: 'info' }, () => '当前') : null,
      ]),
  },
  { title: '邮箱', key: 'email', minWidth: 220, ellipsis: { tooltip: true } },
  {
    title: '状态',
    key: 'is_active',
    width: 90,
    render: (row) => h(NTag, { size: 'small', type: row.is_active ? 'success' : 'error' }, () => (row.is_active ? '启用' : '禁用')),
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 170,
    render: (row) => (row.created_at ? new Date(row.created_at).toLocaleString('zh-CN') : '-'),
  },
  {
    title: '操作',
    key: 'actions',
    width: 280,
    render: (row) =>
      h(NSpace, { size: 8 }, () => [
        h(NButton, { size: 'small', type: 'primary', onClick: () => openEdit(row) }, () => '编辑'),
        h(NButton, { size: 'small', onClick: () => openChangePassword(row) }, () => '改密'),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete(row) },
          {
            trigger: () => h(NButton, { size: 'small', type: 'error', disabled: row.id === currentAdminId.value }, () => '删除'),
            default: () => '确认删除该管理员？',
          }
        ),
      ]),
  },
]

const loadData = async () => {
  loading.value = true
  try {
    const res = await adminApi.getAdmins({ page: page.value, page_size: pageSize.value })
    if (res.code === 200) {
      admins.value = res.data.items || []
      total.value = res.data.total || 0
    } else {
      message.error(res.message || '加载失败')
    }
  } catch {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = { username: '', email: '', password: '', is_active: true }
}

const openCreate = () => {
  isEdit.value = false
  editingId.value = null
  resetForm()
  showModal.value = true
}

const openEdit = (row: AdminUser) => {
  isEdit.value = true
  editingId.value = row.id
  form.value.username = row.username || ''
  form.value.email = row.email || ''
  form.value.password = ''
  form.value.is_active = !!row.is_active
  showModal.value = true
}

const handleSubmit = async () => {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (isEdit.value && editingId.value) {
      const res = await adminApi.updateAdmin(editingId.value, {
        username: form.value.username,
        email: form.value.email,
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

    const res = await adminApi.createAdmin({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      is_active: form.value.is_active,
    })
    if (res.code === 200) {
      message.success('创建成功')
      showModal.value = false
      await loadData()
    } else {
      message.error(res.message || '创建失败')
    }
  } catch {
    message.error('操作失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row: AdminUser) => {
  try {
    const res = await adminApi.deleteAdmin(row.id)
    if (res.code === 200) {
      message.success('删除成功')
      if (admins.value.length === 1 && page.value > 1) page.value -= 1
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

const openChangePassword = (row: AdminUser) => {
  pwdTarget.value = row
  pwdForm.value.new_password = ''
  pwdForm.value.confirm_password = ''
  showPwdModal.value = true
}

const handleChangePassword = async () => {
  await pwdFormRef.value?.validate()
  if (pwdForm.value.new_password !== pwdForm.value.confirm_password) {
    message.error('两次输入的密码不一致')
    return
  }
  saving.value = true
  try {
    const target = pwdTarget.value
    if (!target) return
    const res = await adminApi.setAdminPassword(target.id, pwdForm.value.new_password)
    if (res.code === 200) {
      message.success('密码已更新')
      showPwdModal.value = false
    } else {
      message.error(res.message || '更新失败')
    }
  } catch {
    message.error('更新失败')
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div>
    <NSpace align="center" justify="space-between" style="margin-bottom: 24px">
      <h2 style="margin: 0">管理员设置</h2>
      <NButton type="primary" @click="openCreate">新增管理员</NButton>
    </NSpace>

    <NCard>
      <NDataTable :columns="columns" :data="admins" :loading="loading" :bordered="false" />

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

    <NModal v-model:show="showModal" preset="card" style="width: 520px" :title="isEdit ? '编辑管理员' : '新增管理员'">
      <NForm ref="formRef" :model="form" label-placement="left" label-width="90">
        <NFormItem label="用户名" path="username" :rule="{ required: true, message: '请输入用户名', trigger: ['blur', 'input'] }">
          <NInput v-model:value="form.username" placeholder="请输入用户名" />
        </NFormItem>
        <NFormItem label="邮箱" path="email" :rule="{ required: true, message: '请输入邮箱', trigger: ['blur', 'input'] }">
          <NInput v-model:value="form.email" placeholder="请输入邮箱" />
        </NFormItem>
        <NFormItem v-if="!isEdit" label="初始密码" path="password" :rule="{ required: true, message: '请输入密码', trigger: ['blur', 'input'] }">
          <NInput v-model:value="form.password" type="password" show-password-on="click" placeholder="至少 6 位" />
        </NFormItem>
        <NFormItem label="启用" path="is_active">
          <NSwitch v-model:value="form.is_active" />
        </NFormItem>
      </NForm>

      <template #footer>
        <NSpace justify="end">
          <NButton @click="showModal = false">取消</NButton>
          <NButton type="primary" :loading="saving" @click="handleSubmit">{{ isEdit ? '保存' : '创建' }}</NButton>
        </NSpace>
      </template>
    </NModal>

    <NModal v-model:show="showPwdModal" preset="card" style="width: 520px" title="修改管理员密码">
      <NForm ref="pwdFormRef" :model="pwdForm" label-placement="left" label-width="90">
        <NFormItem label="新密码" path="new_password" :rule="{ required: true, message: '请输入新密码', trigger: ['blur', 'input'] }">
          <NInput v-model:value="pwdForm.new_password" type="password" show-password-on="click" placeholder="至少 6 位" />
        </NFormItem>
        <NFormItem label="确认密码" path="confirm_password" :rule="{ required: true, message: '请再次输入新密码', trigger: ['blur', 'input'] }">
          <NInput v-model:value="pwdForm.confirm_password" type="password" show-password-on="click" placeholder="再次输入" />
        </NFormItem>
      </NForm>

      <template #footer>
        <NSpace justify="end">
          <NButton @click="showPwdModal = false">取消</NButton>
          <NButton type="primary" :loading="saving" @click="handleChangePassword">保存</NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>



