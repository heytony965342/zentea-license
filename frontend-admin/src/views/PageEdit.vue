<script setup lang="ts">
/**
 * 页面编辑
 */
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NCard,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NSpace,
  NSwitch,
  NInputNumber,
  NAlert,
  NSpin,
  useMessage,
} from 'naive-ui'
import { pageApi } from '@/api'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const loading = ref(false)
const saving = ref(false)

// 判断是新建还是编辑
const isNew = computed(() => route.params.id === 'new')
const pageId = computed(() => isNew.value ? null : Number(route.params.id))

// 表单数据
const form = reactive({
  slug: '',
  title: '',
  subtitle: '',
  content: '',
  meta_description: '',
  status: 'draft',
  sort_order: 0,
})

// 发布状态
const isPublished = computed({
  get: () => form.status === 'published',
  set: (val) => { form.status = val ? 'published' : 'draft' }
})

// 加载页面数据
const loadPage = async () => {
  if (isNew.value) return
  
  loading.value = true
  try {
    const res = await pageApi.getDetail(pageId.value!)
    if (res.code === 200 && res.data) {
      const data = res.data
      form.slug = data.slug || ''
      form.title = data.title || ''
      form.subtitle = data.subtitle || ''
      form.content = data.content || ''
      form.meta_description = data.meta_description || ''
      form.status = data.status || 'draft'
      form.sort_order = data.sort_order || 0
    } else {
      message.error(res.message || '加载页面失败')
      router.push({ name: 'Pages' })
    }
  } catch (e) {
    message.error('加载页面失败')
    router.push({ name: 'Pages' })
  } finally {
    loading.value = false
  }
}

// 保存页面
const savePage = async () => {
  // 验证
  if (!form.slug.trim()) {
    message.warning('请输入页面标识')
    return
  }
  if (!form.title.trim()) {
    message.warning('请输入页面标题')
    return
  }
  
  saving.value = true
  try {
    let res
    if (isNew.value) {
      res = await pageApi.create({
        slug: form.slug,
        title: form.title,
        subtitle: form.subtitle,
        content: form.content,
        meta_description: form.meta_description,
        status: form.status,
        sort_order: form.sort_order,
      })
    } else {
      res = await pageApi.update(pageId.value!, {
        title: form.title,
        subtitle: form.subtitle,
        content: form.content,
        meta_description: form.meta_description,
        status: form.status,
        sort_order: form.sort_order,
      })
    }
    
    if (res.code === 200) {
      message.success(isNew.value ? '页面创建成功' : '页面保存成功')
      router.push({ name: 'Pages' })
    } else {
      message.error(res.message || '保存失败')
    }
  } catch (e) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 返回列表
const goBack = () => {
  router.push({ name: 'Pages' })
}

onMounted(() => {
  loadPage()
})
</script>

<template>
  <div class="page-edit">
    <NCard :title="isNew ? '新建页面' : '编辑页面'">
      <template #header-extra>
        <NSpace>
          <NButton @click="goBack">返回</NButton>
          <NButton type="primary" :loading="saving" @click="savePage">
            💾 保存
          </NButton>
        </NSpace>
      </template>
      
      <NSpin :show="loading">
        <NForm label-placement="left" label-width="100px" style="max-width: 900px">
          <NFormItem label="页面标识" required>
            <NInput 
              v-model:value="form.slug" 
              placeholder="如 features、pricing（用于 URL）"
              :disabled="!isNew"
            />
            <template #feedback>
              <span style="color: #999; font-size: 12px">
                访问地址将是：/{{ form.slug || 'xxx' }}
              </span>
            </template>
          </NFormItem>
          
          <NFormItem label="页面标题" required>
            <NInput v-model:value="form.title" placeholder="页面标题" />
          </NFormItem>
          
          <NFormItem label="页面副标题">
            <NInput v-model:value="form.subtitle" placeholder="可选的副标题" />
          </NFormItem>
          
          <NFormItem label="SEO 描述">
            <NInput 
              v-model:value="form.meta_description" 
              type="textarea"
              :rows="2"
              placeholder="用于搜索引擎的页面描述"
            />
          </NFormItem>
          
          <NFormItem label="发布状态">
            <NSpace align="center">
              <NSwitch v-model:value="isPublished" />
              <span>{{ isPublished ? '已发布' : '草稿' }}</span>
            </NSpace>
          </NFormItem>
          
          <NFormItem label="排序">
            <NInputNumber 
              v-model:value="form.sort_order" 
              :min="0" 
              :max="999"
              style="width: 150px"
            />
            <template #feedback>
              <span style="color: #999; font-size: 12px">数字越小排序越靠前</span>
            </template>
          </NFormItem>
          
          <NFormItem label="页面内容">
            <NAlert type="info" :bordered="false" style="margin-bottom: 12px; width: 100%">
              支持 Markdown 格式，可使用标题（##）、列表（-）、加粗（**文字**）等语法
            </NAlert>
            <NInput 
              v-model:value="form.content" 
              type="textarea"
              :rows="20"
              placeholder="页面内容（支持 Markdown 格式）"
              style="font-family: monospace; width: 100%"
            />
          </NFormItem>
        </NForm>
      </NSpin>
    </NCard>
  </div>
</template>

<style scoped>
.page-edit {
  padding: 0;
}
</style>

