<script setup lang="ts">
/**
 * 系统设置页面
 * 包含支付接口设置、客服联系方式设置、服务器模式设置
 */
import { ref, reactive, onMounted } from 'vue'
import {
  NCard,
  NTabs,
  NTabPane,
  NForm,
  NFormItem,
  NInput,
  NSwitch,
  NButton,
  NSpace,
  NDivider,
  NAlert,
  NRadioGroup,
  NRadio,
  NTag,
  useMessage,
} from 'naive-ui'
import { settingApi } from '@/api'

const message = useMessage()
const loading = ref(false)
const saving = ref(false)

// 服务器模式设置
const serverForm = reactive({
  server_mode: 'local',
  server_url: 'http://localhost:8001',
})

// 服务器模式选项
const serverModeOptions = [
  { 
    value: 'local', 
    label: '本地调试环境',
    url: 'http://localhost:8001',
    description: '用于本地开发和测试'
  },
  { 
    value: 'production', 
    label: '生产环境',
    url: 'https://sq.jinghuatea.com',
    description: '正式授权验证服务器'
  },
]

// 支付设置
const paymentForm = reactive({
  // 支付宝
  alipay_enabled: false,
  alipay_app_id: '',
  alipay_private_key: '',
  alipay_public_key: '',
  alipay_notify_url: '',
  alipay_return_url: '',
  alipay_private_key_configured: false,
  alipay_public_key_configured: false,
  // 微信支付
  wechat_enabled: false,
  wechat_app_id: '',
  wechat_mch_id: '',
  wechat_api_key: '',
  wechat_notify_url: '',
  wechat_api_key_configured: false,
})

// 客服联系方式
const contactForm = reactive({
  contact_phone: '',
  contact_email: '',
  contact_wechat: '',
  contact_qq: '',
  contact_address: '',
  contact_work_time: '',
})

// 加载服务器设置
const loadServerSettings = async () => {
  try {
    const res = await settingApi.getAll('server')
    if (res.code === 200 && res.data) {
      res.data.forEach((item: any) => {
        if (item.key === 'server_mode') serverForm.server_mode = item.value || 'local'
        if (item.key === 'server_url') serverForm.server_url = item.value || 'http://localhost:8001'
      })
    }
  } catch (e) {
    // 忽略
  }
}

// 保存服务器设置
const saveServerSettings = async () => {
  saving.value = true
  try {
    // 根据模式自动设置 URL
    const selectedMode = serverModeOptions.find(m => m.value === serverForm.server_mode)
    const url = selectedMode?.url || serverForm.server_url
    
    const res = await settingApi.update({
      server_mode: serverForm.server_mode,
      server_url: url,
    })
    if (res.code === 200) {
      serverForm.server_url = url
      message.success('服务器设置保存成功')
    } else {
      message.error(res.message || '保存失败')
    }
  } catch (e) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 加载设置
const loadSettings = async () => {
  loading.value = true
  try {
    // 加载服务器设置
    await loadServerSettings()
    
    // 加载支付设置
    const paymentRes = await settingApi.getPayment()
    if (paymentRes.code === 200 && paymentRes.data) {
      const data = paymentRes.data
      paymentForm.alipay_enabled = data.alipay_enabled === 'true'
      paymentForm.alipay_app_id = data.alipay_app_id || ''
      paymentForm.alipay_private_key = data.alipay_private_key || ''
      paymentForm.alipay_public_key = data.alipay_public_key || ''
      paymentForm.alipay_notify_url = data.alipay_notify_url || ''
      paymentForm.alipay_return_url = data.alipay_return_url || ''
      paymentForm.alipay_private_key_configured = data.alipay_private_key_configured || false
      paymentForm.alipay_public_key_configured = data.alipay_public_key_configured || false
      
      paymentForm.wechat_enabled = data.wechat_enabled === 'true'
      paymentForm.wechat_app_id = data.wechat_app_id || ''
      paymentForm.wechat_mch_id = data.wechat_mch_id || ''
      paymentForm.wechat_api_key = data.wechat_api_key || ''
      paymentForm.wechat_notify_url = data.wechat_notify_url || ''
      paymentForm.wechat_api_key_configured = data.wechat_api_key_configured || false
    }
    
    // 加载客服联系方式
    const contactRes = await settingApi.getContact()
    if (contactRes.code === 200 && contactRes.data) {
      Object.assign(contactForm, contactRes.data)
    }
  } catch (e) {
    message.error('加载设置失败')
  } finally {
    loading.value = false
  }
}

// 保存支付设置
const savePaymentSettings = async () => {
  saving.value = true
  try {
    const settings: Record<string, string> = {
      alipay_enabled: paymentForm.alipay_enabled ? 'true' : 'false',
      alipay_app_id: paymentForm.alipay_app_id,
      alipay_notify_url: paymentForm.alipay_notify_url,
      alipay_return_url: paymentForm.alipay_return_url,
      wechat_enabled: paymentForm.wechat_enabled ? 'true' : 'false',
      wechat_app_id: paymentForm.wechat_app_id,
      wechat_mch_id: paymentForm.wechat_mch_id,
      wechat_notify_url: paymentForm.wechat_notify_url,
    }
    
    // 只有非脱敏值才更新
    if (paymentForm.alipay_private_key && paymentForm.alipay_private_key !== '******') {
      settings.alipay_private_key = paymentForm.alipay_private_key
    }
    if (paymentForm.alipay_public_key && paymentForm.alipay_public_key !== '******') {
      settings.alipay_public_key = paymentForm.alipay_public_key
    }
    if (paymentForm.wechat_api_key && paymentForm.wechat_api_key !== '******') {
      settings.wechat_api_key = paymentForm.wechat_api_key
    }
    
    const res = await settingApi.update(settings)
    if (res.code === 200) {
      message.success('支付设置保存成功')
      loadSettings()
    } else {
      message.error(res.message || '保存失败')
    }
  } catch (e) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 保存客服联系方式
const saveContactSettings = async () => {
  saving.value = true
  try {
    const res = await settingApi.update(contactForm as unknown as Record<string, string>)
    if (res.code === 200) {
      message.success('客服联系方式保存成功')
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
  loadSettings()
})
</script>

<template>
  <div class="settings-page">
    <NCard title="系统设置">
      <NTabs type="line" animated>
        <!-- 服务器模式 -->
        <NTabPane name="server" tab="服务器模式">
          <NAlert type="info" :bordered="false" style="margin-bottom: 24px">
            设置当前授权服务器的运行模式。本地调试模式用于开发测试，生产模式用于正式运营。
          </NAlert>
          
          <NForm label-placement="left" label-width="120px" :disabled="loading">
            <NFormItem label="运行模式">
              <NRadioGroup v-model:value="serverForm.server_mode">
                <NSpace vertical>
                  <NRadio 
                    v-for="option in serverModeOptions" 
                    :key="option.value" 
                    :value="option.value"
                  >
                    <NSpace align="center">
                      <strong>{{ option.label }}</strong>
                      <NTag :type="option.value === 'production' ? 'success' : 'warning'" size="small">
                        {{ option.value === 'production' ? '正式' : '调试' }}
                      </NTag>
                    </NSpace>
                    <div style="color: #666; font-size: 12px; margin-top: 4px; margin-left: 24px">
                      {{ option.description }}
                    </div>
                    <div style="color: #999; font-size: 12px; margin-left: 24px">
                      地址: {{ option.url }}
                    </div>
                  </NRadio>
                </NSpace>
              </NRadioGroup>
            </NFormItem>
            
            <NFormItem label="当前地址">
              <NInput v-model:value="serverForm.server_url" disabled />
            </NFormItem>
            
            <NFormItem label="">
              <NButton type="primary" :loading="saving" @click="saveServerSettings">
                保存服务器设置
              </NButton>
            </NFormItem>
          </NForm>
        </NTabPane>
        
        <!-- 支付设置 -->
        <NTabPane name="payment" tab="支付设置">
          <NAlert type="info" :bordered="false" style="margin-bottom: 24px">
            配置在线支付接口后，用户可以在线购买授权。请确保填写正确的密钥信息。
          </NAlert>
          
          <NForm label-placement="left" label-width="140px" :disabled="loading">
            <!-- 支付宝配置 -->
            <NDivider title-placement="left">支付宝</NDivider>
            
            <NFormItem label="启用支付宝">
              <NSwitch v-model:value="paymentForm.alipay_enabled" />
            </NFormItem>
            
            <NFormItem label="应用ID (AppID)">
              <NInput v-model:value="paymentForm.alipay_app_id" placeholder="支付宝开放平台应用ID" />
            </NFormItem>
            
            <NFormItem label="应用私钥">
              <NInput
                v-model:value="paymentForm.alipay_private_key"
                type="textarea"
                :rows="3"
                :placeholder="paymentForm.alipay_private_key_configured ? '已配置（不修改请留空）' : '粘贴应用私钥'"
              />
            </NFormItem>
            
            <NFormItem label="支付宝公钥">
              <NInput
                v-model:value="paymentForm.alipay_public_key"
                type="textarea"
                :rows="3"
                :placeholder="paymentForm.alipay_public_key_configured ? '已配置（不修改请留空）' : '粘贴支付宝公钥'"
              />
            </NFormItem>
            
            <NFormItem label="异步通知地址">
              <NInput v-model:value="paymentForm.alipay_notify_url" placeholder="https://your-domain.com/api/v1/payment/alipay/notify" />
            </NFormItem>
            
            <NFormItem label="同步跳转地址">
              <NInput v-model:value="paymentForm.alipay_return_url" placeholder="https://your-domain.com/payment/success" />
            </NFormItem>
            
            <!-- 微信支付配置 -->
            <NDivider title-placement="left">微信支付</NDivider>
            
            <NFormItem label="启用微信支付">
              <NSwitch v-model:value="paymentForm.wechat_enabled" />
            </NFormItem>
            
            <NFormItem label="应用ID (AppID)">
              <NInput v-model:value="paymentForm.wechat_app_id" placeholder="微信公众号/小程序 AppID" />
            </NFormItem>
            
            <NFormItem label="商户号 (MchID)">
              <NInput v-model:value="paymentForm.wechat_mch_id" placeholder="微信支付商户号" />
            </NFormItem>
            
            <NFormItem label="API密钥">
              <NInput
                v-model:value="paymentForm.wechat_api_key"
                type="password"
                show-password-on="click"
                :placeholder="paymentForm.wechat_api_key_configured ? '已配置（不修改请留空）' : '微信支付 API 密钥'"
              />
            </NFormItem>
            
            <NFormItem label="支付回调地址">
              <NInput v-model:value="paymentForm.wechat_notify_url" placeholder="https://your-domain.com/api/v1/payment/wechat/notify" />
            </NFormItem>
            
            <NFormItem label="">
              <NButton type="primary" :loading="saving" @click="savePaymentSettings">
                保存支付设置
              </NButton>
            </NFormItem>
          </NForm>
        </NTabPane>
        
        <!-- 客服联系方式 -->
        <NTabPane name="contact" tab="客服联系方式">
          <NAlert type="info" :bordered="false" style="margin-bottom: 24px">
            设置客服联系方式，用户在购买授权或遇到问题时可以联系客服。
          </NAlert>
          
          <NForm label-placement="left" label-width="120px" :disabled="loading">
            <NFormItem label="客服电话">
              <NInput v-model:value="contactForm.contact_phone" placeholder="如：400-123-4567" />
            </NFormItem>
            
            <NFormItem label="客服邮箱">
              <NInput v-model:value="contactForm.contact_email" placeholder="如：support@zentea.com" />
            </NFormItem>
            
            <NFormItem label="客服微信">
              <NInput v-model:value="contactForm.contact_wechat" placeholder="微信号或二维码图片链接" />
            </NFormItem>
            
            <NFormItem label="客服QQ">
              <NInput v-model:value="contactForm.contact_qq" placeholder="QQ号或QQ群号" />
            </NFormItem>
            
            <NFormItem label="公司地址">
              <NInput v-model:value="contactForm.contact_address" placeholder="详细地址" />
            </NFormItem>
            
            <NFormItem label="工作时间">
              <NInput v-model:value="contactForm.contact_work_time" placeholder="如：周一至周五 9:00-18:00" />
            </NFormItem>
            
            <NFormItem label="">
              <NButton type="primary" :loading="saving" @click="saveContactSettings">
                保存联系方式
              </NButton>
            </NFormItem>
          </NForm>
        </NTabPane>
      </NTabs>
    </NCard>
  </div>
</template>

<style scoped>
.settings-page {
  padding: 0;
}
</style>

