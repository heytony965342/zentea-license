<script setup lang="ts">
/**
 * 首页配置页面
 * 配置用户门户首页的所有展示内容
 */
import { ref, reactive, onMounted } from 'vue'
import {
  NCard,
  NTabs,
  NTabPane,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NSpace,
  NAlert,
  useMessage,
} from 'naive-ui'
import { settingApi } from '@/api'

const message = useMessage()
const loading = ref(false)
const saving = ref(false)

// 首页配置
const homepageForm = reactive({
  // Hero 区（首屏）
  home_hero_title: '茶企专属 ERP 管理系统',
  home_hero_subtitle: '专为茶叶行业打造，覆盖进销存、财务、客户、报表全流程管理',
  home_cta_text: '免费试用 7 天',
  home_secondary_text: '预约演示',
  
  // Showcase 区（产品展示）
  showcase_tag: '多端协同',
  showcase_title: '跨平台无缝办公体验',
  showcase_subtitle: '无论是在办公室使用电脑，还是在茶园使用手机，数据实时同步，触手可及',
  mockup_laptop_image: '',
  mockup_phone_image: '',
  
  // Features 区（核心功能）
  features_tag: '核心能力',
  features_title: '为茶企量身打造的全流程解决方案',
  features_subtitle: '从采购到销售，从库存到财务，一站式管理您的茶叶生意',
  features_list: '[]',
  
  // AI Demo 区
  ai_section_tag: 'AI 赋能',
  ai_section_title: '认识「小茗」—— 您的智能经营管家',
  ai_section_subtitle: '用自然语言提问，即刻获得专业的数据分析与决策建议',
  ai_demo_queries: '[]',
  
  // Testimonials 区（客户评价）
  testimonials_tag: '客户心声',
  testimonials_title: '深受全国茶企信赖',
  testimonials_list: '[]',
  
  // CTA 区（行动号召）
  cta_title: '开启智能茶企管理之旅',
  cta_subtitle: '免费试用 7 天，体验 AI 驱动的进销存管理',
  cta_button_text: '立即免费试用',
  cta_secondary_text: '查看价格方案',
  
  // Footer（页脚）
  footer_brand_name: '茗管家',
  footer_brand_slogan: '茶企专属 ERP 管理系统',
  footer_copyright: '© 2025 茗管家 ZenTea ERP. All rights reserved.',
  footer_links: '[]',
  
  // 粒子效果配置
  particle_primary_color: '#1a472a',
  particle_accent_color: '#d4af37',
  particle_count: '8000',
  particle_growth_speed: '0.001',
  particle_interaction: '0.3',
})

// 功能卡片列表
const featuresList = ref<any[]>([])
// 客户评价列表
const testimonialsList = ref<any[]>([])
// 页脚链接列表
const footerLinksList = ref<any[]>([])

// 加载首页配置
const loadHomepageSettings = async () => {
  loading.value = true
  try {
    const res = await settingApi.getHomepage()
    if (res.code === 200 && res.data) {
      res.data.forEach((item: any) => {
        const key = item.key as keyof typeof homepageForm
        if (key in homepageForm) {
          (homepageForm as any)[key] = item.value || (homepageForm as any)[key]
        }
      })
      
      // 解析 JSON 字段
      try {
        featuresList.value = JSON.parse(homepageForm.features_list || '[]')
      } catch { featuresList.value = [] }
      
      try {
        testimonialsList.value = JSON.parse(homepageForm.testimonials_list || '[]')
      } catch { testimonialsList.value = [] }
      
      try {
        footerLinksList.value = JSON.parse(homepageForm.footer_links || '[]')
      } catch { footerLinksList.value = [] }
    }
  } catch (e) {
    message.error('加载首页配置失败')
  } finally {
    loading.value = false
  }
}

// 添加功能卡片
const addFeature = () => {
  featuresList.value.push({
    icon: '📦',
    title: '新功能',
    description: '功能描述',
    features: ['特点1', '特点2', '特点3']
  })
}

// 删除功能卡片
const removeFeature = (index: number) => {
  featuresList.value.splice(index, 1)
}

// 添加客户评价
const addTestimonial = () => {
  testimonialsList.value.push({
    content: '客户评价内容',
    author: '客户姓名',
    company: '公司名称'
  })
}

// 删除客户评价
const removeTestimonial = (index: number) => {
  testimonialsList.value.splice(index, 1)
}

// 保存首页配置
const saveHomepageSettings = async () => {
  saving.value = true
  try {
    // 序列化 JSON 字段
    const formData = {
      ...homepageForm,
      features_list: JSON.stringify(featuresList.value),
      testimonials_list: JSON.stringify(testimonialsList.value),
      footer_links: JSON.stringify(footerLinksList.value),
    }
    
    const res = await settingApi.update(formData as unknown as Record<string, string>)
    if (res.code === 200) {
      message.success('首页配置保存成功')
    } else {
      message.error(res.message || '保存失败')
    }
  } catch (e) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadHomepageSettings()
})
</script>

<template>
  <div class="homepage-setting-page">
    <NCard title="首页配置">
      <template #header-extra>
        <NButton type="primary" :loading="saving" @click="saveHomepageSettings">
          💾 保存所有配置
        </NButton>
      </template>
      
      <NAlert type="info" :bordered="false" style="margin-bottom: 16px">
        配置用户门户首页的所有展示内容，修改后刷新首页即可生效。
      </NAlert>
      
      <NTabs type="card" animated>
        <!-- 首屏区域 -->
        <NTabPane name="hero" tab="🏠 首屏区域">
          <NForm label-placement="left" label-width="120px" :disabled="loading" style="max-width: 800px">
            <NFormItem label="主标题">
              <NInput v-model:value="homepageForm.home_hero_title" placeholder="茶企专属 ERP 管理系统" />
            </NFormItem>
            
            <NFormItem label="副标题">
              <NInput 
                v-model:value="homepageForm.home_hero_subtitle" 
                type="textarea"
                :rows="2"
                placeholder="专为茶叶行业打造..."
              />
            </NFormItem>
            
            <NFormItem label="主按钮文字">
              <NInput v-model:value="homepageForm.home_cta_text" placeholder="免费试用 7 天" style="width: 280px" />
            </NFormItem>
            
            <NFormItem label="次按钮文字">
              <NInput v-model:value="homepageForm.home_secondary_text" placeholder="预约演示" style="width: 280px" />
            </NFormItem>
          </NForm>
        </NTabPane>
        
        <!-- 产品展示区 -->
        <NTabPane name="showcase" tab="📱 产品展示">
          <NForm label-placement="left" label-width="120px" :disabled="loading" style="max-width: 800px">
            <NFormItem label="区块标签">
              <NInput v-model:value="homepageForm.showcase_tag" placeholder="多端协同" style="width: 200px" />
            </NFormItem>
            
            <NFormItem label="区块标题">
              <NInput v-model:value="homepageForm.showcase_title" placeholder="跨平台无缝办公体验" />
            </NFormItem>
            
            <NFormItem label="区块副标题">
              <NInput v-model:value="homepageForm.showcase_subtitle" type="textarea" :rows="2" />
            </NFormItem>
            
            <NFormItem label="PC端截图">
              <NInput v-model:value="homepageForm.mockup_laptop_image" placeholder="https://... 留空使用默认" />
            </NFormItem>
            
            <NFormItem label="App端截图">
              <NInput v-model:value="homepageForm.mockup_phone_image" placeholder="https://... 留空使用默认" />
            </NFormItem>
          </NForm>
        </NTabPane>
        
        <!-- 核心功能区 -->
        <NTabPane name="features" tab="⚡ 核心功能">
          <NForm label-placement="left" label-width="120px" :disabled="loading">
            <NFormItem label="区块标签">
              <NInput v-model:value="homepageForm.features_tag" placeholder="核心能力" style="width: 200px" />
            </NFormItem>
            
            <NFormItem label="区块标题">
              <NInput v-model:value="homepageForm.features_title" style="max-width: 600px" />
            </NFormItem>
            
            <NFormItem label="区块副标题">
              <NInput v-model:value="homepageForm.features_subtitle" type="textarea" :rows="2" style="max-width: 600px" />
            </NFormItem>
            
            <NFormItem label="功能卡片">
              <div style="width: 100%; max-width: 800px">
                <NSpace vertical style="width: 100%">
                  <NCard 
                    v-for="(f, i) in featuresList" 
                    :key="i" 
                    size="small" 
                    style="margin-bottom: 8px"
                  >
                    <template #header>
                      <NSpace align="center">
                        <NInput v-model:value="f.icon" placeholder="图标" style="width: 60px" />
                        <NInput v-model:value="f.title" placeholder="标题" style="width: 150px" />
                        <NButton text type="error" size="small" @click="removeFeature(i)">删除</NButton>
                      </NSpace>
                    </template>
                    <NInput v-model:value="f.description" placeholder="功能描述" style="margin-bottom: 8px" />
                    <NInput 
                      :value="f.features?.join('、')" 
                      @update:value="v => f.features = v.split('、')"
                      placeholder="特点列表，用顿号分隔"
                    />
                  </NCard>
                </NSpace>
                <NButton dashed style="width: 100%; margin-top: 8px" @click="addFeature">+ 添加功能卡片</NButton>
              </div>
            </NFormItem>
          </NForm>
        </NTabPane>
        
        <!-- AI 演示区 -->
        <NTabPane name="ai" tab="🤖 AI 演示">
          <NForm label-placement="left" label-width="120px" :disabled="loading" style="max-width: 800px">
            <NFormItem label="区块标签">
              <NInput v-model:value="homepageForm.ai_section_tag" placeholder="AI 赋能" style="width: 200px" />
            </NFormItem>
            
            <NFormItem label="区块标题">
              <NInput v-model:value="homepageForm.ai_section_title" placeholder="认识「小茗」—— 您的智能经营管家" />
            </NFormItem>
            
            <NFormItem label="区块副标题">
              <NInput v-model:value="homepageForm.ai_section_subtitle" type="textarea" :rows="2" />
            </NFormItem>
          </NForm>
        </NTabPane>
        
        <!-- 客户评价区 -->
        <NTabPane name="testimonials" tab="💬 客户评价">
          <NForm label-placement="left" label-width="120px" :disabled="loading">
            <NFormItem label="区块标签">
              <NInput v-model:value="homepageForm.testimonials_tag" placeholder="客户心声" style="width: 200px" />
            </NFormItem>
            
            <NFormItem label="区块标题">
              <NInput v-model:value="homepageForm.testimonials_title" placeholder="深受全国茶企信赖" style="max-width: 400px" />
            </NFormItem>
            
            <NFormItem label="客户评价">
              <div style="width: 100%; max-width: 800px">
                <NSpace vertical style="width: 100%">
                  <NCard 
                    v-for="(t, i) in testimonialsList" 
                    :key="i" 
                    size="small" 
                    style="margin-bottom: 8px"
                  >
                    <template #header>
                      <NSpace align="center">
                        <NInput v-model:value="t.author" placeholder="客户姓名" style="width: 100px" />
                        <NInput v-model:value="t.company" placeholder="公司名称" style="width: 200px" />
                        <NButton text type="error" size="small" @click="removeTestimonial(i)">删除</NButton>
                      </NSpace>
                    </template>
                    <NInput v-model:value="t.content" type="textarea" :rows="2" placeholder="评价内容" />
                  </NCard>
                </NSpace>
                <NButton dashed style="width: 100%; margin-top: 8px" @click="addTestimonial">+ 添加客户评价</NButton>
              </div>
            </NFormItem>
          </NForm>
        </NTabPane>
        
        <!-- CTA 区 -->
        <NTabPane name="cta" tab="🚀 行动号召">
          <NForm label-placement="left" label-width="120px" :disabled="loading" style="max-width: 800px">
            <NFormItem label="区块标题">
              <NInput v-model:value="homepageForm.cta_title" placeholder="开启智能茶企管理之旅" />
            </NFormItem>
            
            <NFormItem label="区块副标题">
              <NInput v-model:value="homepageForm.cta_subtitle" type="textarea" :rows="2" />
            </NFormItem>
            
            <NFormItem label="主按钮文字">
              <NInput v-model:value="homepageForm.cta_button_text" placeholder="立即免费试用" style="width: 280px" />
            </NFormItem>
            
            <NFormItem label="次按钮文字">
              <NInput v-model:value="homepageForm.cta_secondary_text" placeholder="查看价格方案" style="width: 280px" />
            </NFormItem>
          </NForm>
        </NTabPane>
        
        <!-- 页脚区 -->
        <NTabPane name="footer" tab="📄 页脚">
          <NForm label-placement="left" label-width="120px" :disabled="loading" style="max-width: 800px">
            <NFormItem label="品牌名称">
              <NInput v-model:value="homepageForm.footer_brand_name" placeholder="茗管家" style="width: 200px" />
            </NFormItem>
            
            <NFormItem label="品牌标语">
              <NInput v-model:value="homepageForm.footer_brand_slogan" placeholder="茶企专属 ERP 管理系统" />
            </NFormItem>
            
            <NFormItem label="版权信息">
              <NInput v-model:value="homepageForm.footer_copyright" placeholder="© 2025 茗管家 ZenTea ERP." />
            </NFormItem>
          </NForm>
        </NTabPane>
        
        <!-- 粒子效果 -->
        <NTabPane name="particles" tab="✨ 粒子效果">
          <NForm label-placement="left" label-width="140px" :disabled="loading" style="max-width: 600px">
            <NFormItem label="主色（森林绿）">
              <NSpace align="center">
                <input 
                  type="color" 
                  v-model="homepageForm.particle_primary_color"
                  style="width: 50px; height: 32px; border: none; cursor: pointer;"
                />
                <NInput v-model:value="homepageForm.particle_primary_color" style="width: 120px" />
              </NSpace>
            </NFormItem>
            
            <NFormItem label="点缀色（数字金）">
              <NSpace align="center">
                <input 
                  type="color" 
                  v-model="homepageForm.particle_accent_color"
                  style="width: 50px; height: 32px; border: none; cursor: pointer;"
                />
                <NInput v-model:value="homepageForm.particle_accent_color" style="width: 120px" />
              </NSpace>
            </NFormItem>
            
            <NFormItem label="粒子数量">
              <NSpace align="center">
                <NInput v-model:value="homepageForm.particle_count" placeholder="8000" style="width: 150px" />
                <span style="color: #666; font-size: 12px">建议 2000-10000</span>
              </NSpace>
            </NFormItem>
            
            <NFormItem label="生长速度">
              <NInput v-model:value="homepageForm.particle_growth_speed" placeholder="0.001" style="width: 150px" />
            </NFormItem>
            
            <NFormItem label="交互灵敏度">
              <NInput v-model:value="homepageForm.particle_interaction" placeholder="0.3" style="width: 150px" />
            </NFormItem>
          </NForm>
        </NTabPane>
      </NTabs>
    </NCard>
  </div>
</template>

<style scoped>
.homepage-setting-page {
  padding: 0;
}
</style>

