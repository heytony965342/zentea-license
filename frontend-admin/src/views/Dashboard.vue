<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NCard, NGrid, NGi, NStatistic, NSpace, useMessage } from 'naive-ui'
import { adminApi } from '@/api'

const message = useMessage()

const stats = ref({
  total_customers: 0,
  licenses: {
    active: 0,
    pending: 0,
    expired: 0,
    expiring_soon: 0,
  },
})

const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const res = await adminApi.getDashboard()
    if (res.code === 200) {
      stats.value = res.data
    }
  } catch (e) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div>
    <h2 style="margin-bottom: 24px">仪表盘</h2>
    
    <NGrid :cols="4" :x-gap="16" :y-gap="16">
      <NGi>
        <NCard>
          <NStatistic label="客户总数" :value="stats.total_customers" />
        </NCard>
      </NGi>
      <NGi>
        <NCard>
          <NStatistic label="有效授权" :value="stats.licenses.active">
            <template #suffix>
              <span style="color: #18a058">个</span>
            </template>
          </NStatistic>
        </NCard>
      </NGi>
      <NGi>
        <NCard>
          <NStatistic label="待激活" :value="stats.licenses.pending">
            <template #suffix>
              <span style="color: #f0a020">个</span>
            </template>
          </NStatistic>
        </NCard>
      </NGi>
      <NGi>
        <NCard>
          <NStatistic label="即将到期（7天内）" :value="stats.licenses.expiring_soon">
            <template #suffix>
              <span style="color: #d03050">个</span>
            </template>
          </NStatistic>
        </NCard>
      </NGi>
    </NGrid>
    
    <NCard title="快速操作" style="margin-top: 24px">
      <NSpace>
        <router-link to="/customers">
          <n-button>管理客户</n-button>
        </router-link>
        <router-link to="/licenses">
          <n-button>管理授权</n-button>
        </router-link>
      </NSpace>
    </NCard>
  </div>
</template>

