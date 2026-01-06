<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, useMessage } from 'naive-ui'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const loading = ref(false)
const form = ref({
  username: '',
  password: '',
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    message.warning('请输入用户名和密码')
    return
  }
  
  loading.value = true
  try {
    const success = await userStore.login(form.value.username, form.value.password)
    if (success) {
      message.success('登录成功')
      router.push('/')
    } else {
      message.error('用户名或密码错误')
    }
  } catch (e: any) {
    message.error(e.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <NCard class="login-card" title="ZenTea License 管理后台">
      <NForm>
        <NFormItem label="用户名">
          <NInput v-model:value="form.username" placeholder="请输入用户名" @keyup.enter="handleLogin" />
        </NFormItem>
        <NFormItem label="密码">
          <NInput v-model:value="form.password" type="password" placeholder="请输入密码" @keyup.enter="handleLogin" />
        </NFormItem>
        <NButton type="primary" block :loading="loading" @click="handleLogin">
          登录
        </NButton>
      </NForm>
    </NCard>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a472a 0%, #2d5a3f 100%);
}

.login-card {
  width: 400px;
}
</style>

