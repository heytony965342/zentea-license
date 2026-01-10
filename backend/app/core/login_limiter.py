"""
登录限制器 - 防暴力破解
使用内存缓存实现，支持按 IP 和用户名限制
"""
import time
from typing import Dict, Tuple, Optional
from threading import Lock
from app.core.config import settings


class LoginLimiter:
    """登录限制器"""
    
    def __init__(self):
        # 存储格式: {key: (fail_count, first_fail_time, lockout_until)}
        self._attempts: Dict[str, Tuple[int, float, float]] = {}
        self._lock = Lock()
    
    def _get_key(self, ip: str, username: str) -> str:
        """生成缓存键（同时限制 IP 和用户名）"""
        return f"{ip}:{username}"
    
    def _cleanup_expired(self):
        """清理过期的记录"""
        now = time.time()
        expired_keys = [
            key for key, (_, _, lockout_until) in self._attempts.items()
            if lockout_until > 0 and now > lockout_until
        ]
        for key in expired_keys:
            del self._attempts[key]
    
    def is_locked(self, ip: str, username: str) -> Tuple[bool, Optional[int]]:
        """
        检查是否被锁定
        返回: (是否锁定, 剩余秒数)
        """
        key = self._get_key(ip, username)
        
        with self._lock:
            self._cleanup_expired()
            
            if key not in self._attempts:
                return False, None
            
            fail_count, first_fail_time, lockout_until = self._attempts[key]
            now = time.time()
            
            # 检查是否在锁定期内
            if lockout_until > 0 and now < lockout_until:
                remaining = int(lockout_until - now)
                return True, remaining
            
            # 锁定期已过，重置
            if lockout_until > 0 and now >= lockout_until:
                del self._attempts[key]
                return False, None
            
            return False, None
    
    def record_failure(self, ip: str, username: str) -> Tuple[int, bool, Optional[int]]:
        """
        记录登录失败
        返回: (失败次数, 是否触发锁定, 锁定秒数)
        """
        key = self._get_key(ip, username)
        now = time.time()
        
        with self._lock:
            if key not in self._attempts:
                # 首次失败
                self._attempts[key] = (1, now, 0)
                return 1, False, None
            
            fail_count, first_fail_time, lockout_until = self._attempts[key]
            
            # 如果已经被锁定，返回剩余时间
            if lockout_until > 0 and now < lockout_until:
                remaining = int(lockout_until - now)
                return fail_count, True, remaining
            
            # 增加失败次数
            fail_count += 1
            
            # 检查是否达到锁定阈值
            if fail_count >= settings.LOGIN_MAX_ATTEMPTS:
                lockout_until = now + (settings.LOGIN_LOCKOUT_MINUTES * 60)
                self._attempts[key] = (fail_count, first_fail_time, lockout_until)
                return fail_count, True, settings.LOGIN_LOCKOUT_MINUTES * 60
            
            self._attempts[key] = (fail_count, first_fail_time, 0)
            return fail_count, False, None
    
    def record_success(self, ip: str, username: str):
        """登录成功，清除记录"""
        key = self._get_key(ip, username)
        
        with self._lock:
            if key in self._attempts:
                del self._attempts[key]
    
    def get_remaining_attempts(self, ip: str, username: str) -> int:
        """获取剩余尝试次数"""
        key = self._get_key(ip, username)
        
        with self._lock:
            if key not in self._attempts:
                return settings.LOGIN_MAX_ATTEMPTS
            
            fail_count, _, lockout_until = self._attempts[key]
            
            # 如果被锁定，返回 0
            if lockout_until > 0 and time.time() < lockout_until:
                return 0
            
            return max(0, settings.LOGIN_MAX_ATTEMPTS - fail_count)


# 全局单例
login_limiter = LoginLimiter()



