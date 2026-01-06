"""
统一响应格式
"""
from typing import Any, Optional


def success(data: Any = None, message: str = "操作成功") -> dict:
    """成功响应"""
    return {
        "code": 200,
        "message": message,
        "data": data,
    }


def error(message: str, code: int = 400, data: Any = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data,
    }
