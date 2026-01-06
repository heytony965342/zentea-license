<script setup lang="ts">
/**
 * 页面管理列表
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard,
  NDataTable,
  NButton,
  NSpace,
  NTag,
  NPopconfirm,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { pageApi } from '@/api'

const router = useRouter()
const message = useMessage()
const loading = ref(false)
const pages = ref<any[]>([])

// 表格列定义
const columns: DataTableColumns<any> = [
  {
    title: 'ID',
    key: 'id',
    width: 60,
  },
  {
    title: '页面标识',
    key: 'slug',
    width: 120,
    render: (row) => {
      return `/${row.slug}`
    },
  },
  {
    title: '页面标题',
    key: 'title',
    ellipsis: {
      tooltip: true,
    },
  },
  {
    title: '副标题',
    key: 'subtitle',
    ellipsis: {
      tooltip: true,
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => {
      return row.status === 'published'
        ? h(NTag, { type: 'success', size: 'small' }, { default: () => '已发布' })
        : h(NTag, { type: 'warning', size: 'small' }, { default: () => '草稿' })
    },
  },
  {
    title: '排序',
    key: 'sort_order',
    width: 80,
  },
  {
    title: '更新时间',
    key: 'updated_at',
    width: 160,
    render: (row) => {
      if (!row.updated_at) return '-'
      return new Date(row.updated_at).toLocaleString('zh-CN')
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 160,
    fixed: 'right',
    render: (row) => {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, 
            { 
              size: 'small', 
              type: 'primary',
              onClick: () => editPage(row.id)
            }, 
            { default: () => '编辑' }
          ),
          h(NButton, 
            { 
              size: 'small', 
              type: 'info',
              onClick: () => previewPage(row.slug)
            }, 
            { default: () => '预览' }
          ),
          h(NPopconfirm, 
            {
              onPositiveClick: () => deletePage(row.id)
            },
            {
              trigger: () => h(NButton, { size: 'small', type: 'error' }, { default: () => '删除' }),
              default: () => '确定要删除此页面吗？'
            }
          ),
        ]
      })
    },
  },
]

import { h } from 'vue'

// 加载页面列表
const loadPages = async () => {
  loading.value = true
  try {
    const res = await pageApi.getList()
    if (res.code === 200) {
      pages.value = res.data || []
    } else {
      message.error(res.message || '加载失败')
    }
  } catch (e) {
    message.error('加载页面列表失败')
  } finally {
    loading.value = false
  }
}

// 编辑页面
const editPage = (id: number) => {
  router.push({ name: 'PageEdit', params: { id } })
}

// 预览页面
const previewPage = (slug: string) => {
  // 打开门户网站对应页面
  window.open(`http://localhost:3002/${slug}`, '_blank')
}

// 删除页面
const deletePage = async (id: number) => {
  try {
    const res = await pageApi.delete(id)
    if (res.code === 200) {
      message.success('删除成功')
      loadPages()
    } else {
      message.error(res.message || '删除失败')
    }
  } catch (e) {
    message.error('删除失败')
  }
}

// 创建新页面
const createPage = () => {
  router.push({ name: 'PageEdit', params: { id: 'new' } })
}

onMounted(() => {
  loadPages()
})
</script>

<template>
  <div class="pages-page">
    <NCard title="页面管理">
      <template #header-extra>
        <NButton type="primary" @click="createPage">
          ➕ 新建页面
        </NButton>
      </template>
      
      <NDataTable
        :columns="columns"
        :data="pages"
        :loading="loading"
        :bordered="false"
        :single-line="false"
        :scroll-x="900"
      />
    </NCard>
  </div>
</template>

<style scoped>
.pages-page {
  padding: 0;
}
</style>

