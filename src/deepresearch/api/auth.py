# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from __future__ import annotations

import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from deepresearch.logging_config import get_logger

logger = get_logger(__name__)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


class APIKeyAuth:
    """API 密钥认证管理器。"""

    def __init__(self, api_keys: list[str] | None = None):
        self._api_keys: set[str] = set()

        if api_keys:
            self._api_keys.update(api_keys)

        env_keys = os.getenv("DEEPRESEARCH_API_KEYS", "")
        if env_keys:
            for key in env_keys.split(","):
                key = key.strip()
                if key:
                    self._api_keys.add(key)

        logger.info(f"API key auth initialized with {len(self._api_keys)} valid keys")

    def add_key(self, api_key: str) -> None:
        """添加 API 密钥。"""
        self._api_keys.add(api_key.strip())

    def remove_key(self, api_key: str) -> None:
        """移除 API 密钥。"""
        self._api_keys.discard(api_key.strip())

    def validate_key(self, api_key: str | None) -> bool:
        """验证 API 密钥是否有效。"""
        if not self._api_keys:
            return True
        if api_key is None:
            return False
        return api_key.strip() in self._api_keys

    @property
    def has_keys(self) -> bool:
        """检查是否配置了密钥。"""
        return len(self._api_keys) > 0


api_key_auth = APIKeyAuth()


async def get_api_key(
    api_key: Optional[str] = Depends(api_key_header),
) -> str:
    """FastAPI 依赖：获取并验证 API 密钥。"""
    if not api_key_auth.validate_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key
