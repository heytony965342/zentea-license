"""
配置管理
"""
import os
import json
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 运行环境：development / production
    ENV: str = os.getenv("ENV", "development")
    
    # 数据库
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://license_admin:license_secure_pwd_2025@localhost:5433/zentea_license"
    )
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 授权服务
    LICENSE_SERVER_URL: str = os.getenv("LICENSE_SERVER_URL", "https://sq.jinghuatea.com")
    
    # RSA 密钥路径（可选，用于签名验证）
    RSA_PRIVATE_KEY_PATH: str = os.getenv("RSA_PRIVATE_KEY_PATH", "keys/private.pem")
    RSA_PUBLIC_KEY_PATH: str = os.getenv("RSA_PUBLIC_KEY_PATH", "keys/public.pem")
    
    # 登录安全配置（防暴力破解）
    LOGIN_MAX_ATTEMPTS: int = 5  # 最大尝试次数
    LOGIN_LOCKOUT_MINUTES: int = 15  # 锁定时间（分钟）

    # 管理员初始化（首次安装时用）
    # - 建议生产环境通过环境变量覆盖，避免固定默认密码
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@zentea.local")

    # CORS（管理后台/门户前端使用 Bearer Token，不需要 cookies，默认关闭 allow_credentials）
    BACKEND_CORS_ORIGINS: str = os.getenv(
        "BACKEND_CORS_ORIGINS",
        '["http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3002", "http://127.0.0.1:3002"]'
    )
    CORS_ALLOW_CREDENTIALS: bool = str(os.getenv("CORS_ALLOW_CREDENTIALS", "false")).lower() == "true"

    @property
    def cors_origins(self) -> List[str]:
        """解析 CORS 来源列表（支持 JSON 数组或逗号分隔字符串）"""
        raw = (self.BACKEND_CORS_ORIGINS or "").strip()
        if not raw:
            return []
        try:
            v = json.loads(raw)
            if isinstance(v, list):
                return [str(x).strip() for x in v if str(x).strip()]
        except Exception:
            # fallback: comma separated
            pass
        return [s.strip() for s in raw.split(",") if s.strip()]

    @property
    def is_production(self) -> bool:
        return str(self.ENV or "").lower() in {"prod", "production"}
    
    class Config:
        env_file = ".env"


settings = Settings()
