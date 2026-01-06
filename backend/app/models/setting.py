"""
系统设置模型
存储支付接口配置、客服联系方式等
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class SystemSetting(SQLModel, table=True):
    """系统设置表"""
    __tablename__ = "system_settings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True, description="设置键名")
    value: str = Field(default="", description="设置值")
    description: Optional[str] = Field(default=None, description="设置说明")
    category: str = Field(default="general", description="分类：payment/contact/general")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# 预定义的设置键名
class SettingKeys:
    """设置键名常量"""
    # 支付宝设置
    ALIPAY_ENABLED = "alipay_enabled"
    ALIPAY_APP_ID = "alipay_app_id"
    ALIPAY_PRIVATE_KEY = "alipay_private_key"
    ALIPAY_PUBLIC_KEY = "alipay_public_key"
    ALIPAY_NOTIFY_URL = "alipay_notify_url"
    ALIPAY_RETURN_URL = "alipay_return_url"
    
    # 微信支付设置
    WECHAT_ENABLED = "wechat_enabled"
    WECHAT_APP_ID = "wechat_app_id"
    WECHAT_MCH_ID = "wechat_mch_id"
    WECHAT_API_KEY = "wechat_api_key"
    WECHAT_NOTIFY_URL = "wechat_notify_url"
    
    # 客服联系方式
    CONTACT_PHONE = "contact_phone"
    CONTACT_EMAIL = "contact_email"
    CONTACT_WECHAT = "contact_wechat"
    CONTACT_QQ = "contact_qq"
    CONTACT_ADDRESS = "contact_address"
    CONTACT_WORK_TIME = "contact_work_time"
    
    # 其他设置
    SITE_NAME = "site_name"
    SITE_LOGO = "site_logo"
    COPYRIGHT = "copyright"
    
    # 服务器运行模式
    SERVER_MODE = "server_mode"  # local / production
    SERVER_URL = "server_url"    # 当前服务器地址
    
    # ============ 首页配置 ============
    # Hero 区（首屏）
    HOME_HERO_TITLE = "home_hero_title"
    HOME_HERO_SUBTITLE = "home_hero_subtitle"
    HOME_CTA_TEXT = "home_cta_text"
    HOME_SECONDARY_TEXT = "home_secondary_text"
    
    # Showcase 区（产品展示）
    SHOWCASE_TAG = "showcase_tag"
    SHOWCASE_TITLE = "showcase_title"
    SHOWCASE_SUBTITLE = "showcase_subtitle"
    
    # Features 区（核心功能）
    FEATURES_TAG = "features_tag"
    FEATURES_TITLE = "features_title"
    FEATURES_SUBTITLE = "features_subtitle"
    FEATURES_LIST = "features_list"  # JSON 数组
    
    # AI Demo 区
    AI_SECTION_TAG = "ai_section_tag"
    AI_SECTION_TITLE = "ai_section_title"
    AI_SECTION_SUBTITLE = "ai_section_subtitle"
    AI_DEMO_QUERIES = "ai_demo_queries"  # JSON 数组
    
    # Testimonials 区（客户评价）
    TESTIMONIALS_TAG = "testimonials_tag"
    TESTIMONIALS_TITLE = "testimonials_title"
    TESTIMONIALS_LIST = "testimonials_list"  # JSON 数组
    
    # CTA 区（行动号召）
    CTA_TITLE = "cta_title"
    CTA_SUBTITLE = "cta_subtitle"
    CTA_BUTTON_TEXT = "cta_button_text"
    CTA_SECONDARY_TEXT = "cta_secondary_text"
    
    # Footer（页脚）
    FOOTER_BRAND_NAME = "footer_brand_name"
    FOOTER_BRAND_SLOGAN = "footer_brand_slogan"
    FOOTER_COPYRIGHT = "footer_copyright"
    FOOTER_LINKS = "footer_links"  # JSON 数组
    
    # 粒子效果配置
    PARTICLE_PRIMARY_COLOR = "particle_primary_color"
    PARTICLE_ACCENT_COLOR = "particle_accent_color"
    PARTICLE_COUNT = "particle_count"
    PARTICLE_GROWTH_SPEED = "particle_growth_speed"
    PARTICLE_INTERACTION = "particle_interaction"
    
    # Mockup 图片
    MOCKUP_LAPTOP_IMAGE = "mockup_laptop_image"
    MOCKUP_PHONE_IMAGE = "mockup_phone_image"


# 默认设置
DEFAULT_SETTINGS = [
    # 支付宝
    {"key": SettingKeys.ALIPAY_ENABLED, "value": "false", "description": "支付宝支付开关", "category": "payment"},
    {"key": SettingKeys.ALIPAY_APP_ID, "value": "", "description": "支付宝应用ID", "category": "payment"},
    {"key": SettingKeys.ALIPAY_PRIVATE_KEY, "value": "", "description": "支付宝应用私钥", "category": "payment"},
    {"key": SettingKeys.ALIPAY_PUBLIC_KEY, "value": "", "description": "支付宝公钥", "category": "payment"},
    {"key": SettingKeys.ALIPAY_NOTIFY_URL, "value": "", "description": "支付宝异步通知地址", "category": "payment"},
    {"key": SettingKeys.ALIPAY_RETURN_URL, "value": "", "description": "支付宝同步跳转地址", "category": "payment"},
    # 微信支付
    {"key": SettingKeys.WECHAT_ENABLED, "value": "false", "description": "微信支付开关", "category": "payment"},
    {"key": SettingKeys.WECHAT_APP_ID, "value": "", "description": "微信应用ID", "category": "payment"},
    {"key": SettingKeys.WECHAT_MCH_ID, "value": "", "description": "微信商户号", "category": "payment"},
    {"key": SettingKeys.WECHAT_API_KEY, "value": "", "description": "微信API密钥", "category": "payment"},
    {"key": SettingKeys.WECHAT_NOTIFY_URL, "value": "", "description": "微信支付回调地址", "category": "payment"},
    # 客服联系方式
    {"key": SettingKeys.CONTACT_PHONE, "value": "", "description": "客服电话", "category": "contact"},
    {"key": SettingKeys.CONTACT_EMAIL, "value": "", "description": "客服邮箱", "category": "contact"},
    {"key": SettingKeys.CONTACT_WECHAT, "value": "", "description": "客服微信", "category": "contact"},
    {"key": SettingKeys.CONTACT_QQ, "value": "", "description": "客服QQ", "category": "contact"},
    {"key": SettingKeys.CONTACT_ADDRESS, "value": "", "description": "公司地址", "category": "contact"},
    {"key": SettingKeys.CONTACT_WORK_TIME, "value": "周一至周五 9:00-18:00", "description": "工作时间", "category": "contact"},
    # 站点设置
    {"key": SettingKeys.SITE_NAME, "value": "ZenTea 授权中心", "description": "站点名称", "category": "general"},
    {"key": SettingKeys.SITE_LOGO, "value": "", "description": "站点Logo", "category": "general"},
    {"key": SettingKeys.COPYRIGHT, "value": "© 2024 ZenTea. All rights reserved.", "description": "版权信息", "category": "general"},
    # 服务器模式
    {"key": SettingKeys.SERVER_MODE, "value": "local", "description": "运行模式: local=本地调试, production=生产环境", "category": "server"},
    {"key": SettingKeys.SERVER_URL, "value": "http://localhost:8001", "description": "当前服务器地址", "category": "server"},
    # ============ 首页配置 ============
    # Hero 区（首屏）
    {"key": SettingKeys.HOME_HERO_TITLE, "value": "茶企专属 ERP 管理系统", "description": "首页主标题", "category": "homepage"},
    {"key": SettingKeys.HOME_HERO_SUBTITLE, "value": "专为茶叶行业打造，覆盖进销存、财务、客户、报表全流程管理", "description": "首页副标题", "category": "homepage"},
    {"key": SettingKeys.HOME_CTA_TEXT, "value": "免费试用 7 天", "description": "主按钮文字", "category": "homepage"},
    {"key": SettingKeys.HOME_SECONDARY_TEXT, "value": "预约演示", "description": "次按钮文字", "category": "homepage"},
    
    # Showcase 区（产品展示）
    {"key": SettingKeys.SHOWCASE_TAG, "value": "多端协同", "description": "产品展示区标签", "category": "homepage"},
    {"key": SettingKeys.SHOWCASE_TITLE, "value": "跨平台无缝办公体验", "description": "产品展示区标题", "category": "homepage"},
    {"key": SettingKeys.SHOWCASE_SUBTITLE, "value": "无论是在办公室使用电脑，还是在茶园使用手机，数据实时同步，触手可及", "description": "产品展示区副标题", "category": "homepage"},
    {"key": SettingKeys.MOCKUP_LAPTOP_IMAGE, "value": "", "description": "PC端截图URL", "category": "homepage"},
    {"key": SettingKeys.MOCKUP_PHONE_IMAGE, "value": "", "description": "App端截图URL", "category": "homepage"},
    
    # Features 区（核心功能）
    {"key": SettingKeys.FEATURES_TAG, "value": "核心能力", "description": "核心功能区标签", "category": "homepage"},
    {"key": SettingKeys.FEATURES_TITLE, "value": "为茶企量身打造的全流程解决方案", "description": "核心功能区标题", "category": "homepage"},
    {"key": SettingKeys.FEATURES_SUBTITLE, "value": "从采购到销售，从库存到财务，一站式管理您的茶叶生意", "description": "核心功能区副标题", "category": "homepage"},
    {"key": SettingKeys.FEATURES_LIST, "value": '[{"icon":"📦","title":"智能采购","description":"供应商比价、自动补货建议、采购成本分析","features":["多供应商比价","智能补货预测","AI 成本优化"]},{"icon":"✅","title":"多级审批","description":"移动端审批、流程合规、实时通知提醒","features":["手机一键审批","自定义流程","操作留痕"]},{"icon":"💰","title":"合规财务","description":"标准财务报表、成本核算、税务管理","features":["一键生成报表","多维成本分析","应收应付管理"]},{"icon":"🤖","title":"AI 经营大脑","description":"自然语言查询、销量预测、智能决策建议","features":["对话式查数据","AI 销量预测","经营诊断报告"]}]', "description": "核心功能列表（JSON数组）", "category": "homepage"},
    
    # AI Demo 区
    {"key": SettingKeys.AI_SECTION_TAG, "value": "AI 赋能", "description": "AI区标签", "category": "homepage"},
    {"key": SettingKeys.AI_SECTION_TITLE, "value": "认识「小茗」—— 您的智能经营管家", "description": "AI区标题", "category": "homepage"},
    {"key": SettingKeys.AI_SECTION_SUBTITLE, "value": "用自然语言提问，即刻获得专业的数据分析与决策建议", "description": "AI区副标题", "category": "homepage"},
    {"key": SettingKeys.AI_DEMO_QUERIES, "value": "[]", "description": "AI演示对话（JSON数组）", "category": "homepage"},
    
    # Testimonials 区（客户评价）
    {"key": SettingKeys.TESTIMONIALS_TAG, "value": "客户心声", "description": "客户评价区标签", "category": "homepage"},
    {"key": SettingKeys.TESTIMONIALS_TITLE, "value": "深受全国茶企信赖", "description": "客户评价区标题", "category": "homepage"},
    {"key": SettingKeys.TESTIMONIALS_LIST, "value": '[{"content":"系统非常好用，AI 助手帮我们节省了大量统计时间，强烈推荐！","author":"张总","company":"福建某茶业公司"},{"content":"移动端审批太方便了，出差在外也能及时处理订单。","author":"李经理","company":"杭州某茶叶批发商"},{"content":"财务报表一键生成，再也不用加班做账了。","author":"王会计","company":"云南某普洱茶厂"}]', "description": "客户评价列表（JSON数组）", "category": "homepage"},
    
    # CTA 区（行动号召）
    {"key": SettingKeys.CTA_TITLE, "value": "开启智能茶企管理之旅", "description": "CTA区标题", "category": "homepage"},
    {"key": SettingKeys.CTA_SUBTITLE, "value": "免费试用 7 天，体验 AI 驱动的进销存管理", "description": "CTA区副标题", "category": "homepage"},
    {"key": SettingKeys.CTA_BUTTON_TEXT, "value": "立即免费试用", "description": "CTA主按钮文字", "category": "homepage"},
    {"key": SettingKeys.CTA_SECONDARY_TEXT, "value": "查看价格方案", "description": "CTA次按钮文字", "category": "homepage"},
    
    # Footer（页脚）
    {"key": SettingKeys.FOOTER_BRAND_NAME, "value": "茗管家", "description": "页脚品牌名称", "category": "homepage"},
    {"key": SettingKeys.FOOTER_BRAND_SLOGAN, "value": "茶企专属 ERP 管理系统", "description": "页脚品牌标语", "category": "homepage"},
    {"key": SettingKeys.FOOTER_COPYRIGHT, "value": "© 2025 茗管家 ZenTea ERP. All rights reserved.", "description": "版权信息", "category": "homepage"},
    {"key": SettingKeys.FOOTER_LINKS, "value": '[{"title":"产品","links":[{"text":"功能介绍","href":"/features"},{"text":"价格方案","href":"/pricing"}]},{"title":"支持","links":[{"text":"使用文档","href":"/docs"},{"text":"常见问题","href":"/faq"}]},{"title":"联系我们","links":[{"text":"客服热线","href":"/contact"},{"text":"商务合作","href":"/business"}]}]', "description": "页脚链接组（JSON数组）", "category": "homepage"},
    
    # 粒子效果配置
    {"key": SettingKeys.PARTICLE_PRIMARY_COLOR, "value": "#1a472a", "description": "粒子主色（森林绿）", "category": "particles"},
    {"key": SettingKeys.PARTICLE_ACCENT_COLOR, "value": "#d4af37", "description": "粒子点缀色（数字金）", "category": "particles"},
    {"key": SettingKeys.PARTICLE_COUNT, "value": "8000", "description": "粒子数量", "category": "particles"},
    {"key": SettingKeys.PARTICLE_GROWTH_SPEED, "value": "0.001", "description": "生长速度", "category": "particles"},
    {"key": SettingKeys.PARTICLE_INTERACTION, "value": "0.3", "description": "交互灵敏度", "category": "particles"},
]

