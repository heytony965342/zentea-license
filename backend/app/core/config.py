"""
配置管理
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
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
    
    class Config:
        env_file = ".env"


settings = Settings()
