#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API 密钥认证单元测试
"""
from __future__ import annotations

import os
import pytest
from fastapi import HTTPException

from deepresearch.api.auth import APIKeyAuth, api_key_auth, get_api_key


def test_api_key_auth_init_empty():
    """测试空初始化"""
    auth = APIKeyAuth()
    assert auth.has_keys is False
    assert auth.validate_key(None) is True


def test_api_key_auth_init_with_keys():
    """测试使用密钥列表初始化"""
    auth = APIKeyAuth(api_keys=["key1", "key2", "key3"])
    assert auth.has_keys is True
    assert auth.validate_key("key1") is True
    assert auth.validate_key("key2") is True
    assert auth.validate_key("key3") is True
    assert auth.validate_key("wrong") is False
    assert auth.validate_key(None) is False


def test_api_key_auth_add_key():
    """测试添加密钥"""
    auth = APIKeyAuth()
    assert auth.has_keys is False

    auth.add_key("new-key")
    assert auth.has_keys is True
    assert auth.validate_key("new-key") is True


def test_api_key_auth_add_key_strips_whitespace():
    """测试添加密钥时自动去除空白字符"""
    auth = APIKeyAuth()
    auth.add_key("  my-key  ")
    assert auth.validate_key("my-key") is True
    assert auth.validate_key("  my-key  ") is False


def test_api_key_auth_remove_key():
    """测试移除密钥"""
    auth = APIKeyAuth(api_keys=["key1", "key2"])
    assert auth.validate_key("key1") is True

    auth.remove_key("key1")
    assert auth.validate_key("key1") is False
    assert auth.validate_key("key2") is True


def test_api_key_auth_remove_nonexistent_key():
    """测试移除不存在的密钥不报错"""
    auth = APIKeyAuth(api_keys=["key1"])
    auth.remove_key("nonexistent")
    assert auth.validate_key("key1") is True


def test_api_key_auth_validate_key_when_no_keys():
    """测试没有配置密钥时，任何密钥都通过验证"""
    auth = APIKeyAuth()
    assert auth.validate_key(None) is True
    assert auth.validate_key("any-key") is True


def test_api_key_auth_validate_key_none_with_keys_configured():
    """测试配置了密钥后，None 密钥验证失败"""
    auth = APIKeyAuth(api_keys=["key1"])
    assert auth.validate_key(None) is False


def test_api_key_auth_validate_key_correct_with_keys_configured():
    """测试配置了密钥后，正确密钥验证通过，错误密钥验证失败"""
    auth = APIKeyAuth(api_keys=["valid-key"])
    assert auth.validate_key("valid-key") is True
    assert auth.validate_key("invalid-key") is False


def test_api_key_auth_from_environment(monkeypatch):
    """测试从环境变量加载密钥"""
    monkeypatch.setenv("DEEPRESEARCH_API_KEYS", "env-key1, env-key2 , env-key3")
    auth = APIKeyAuth()
    assert auth.has_keys is True
    assert auth.validate_key("env-key1") is True
    assert auth.validate_key("env-key2") is True
    assert auth.validate_key("env-key3") is True
    assert auth.validate_key("key1") is False


def test_api_key_auth_from_environment_empty(monkeypatch):
    """测试空环境变量不添加密钥"""
    monkeypatch.setenv("DEEPRESEARCH_API_KEYS", "")
    auth = APIKeyAuth()
    assert auth.has_keys is False


def test_api_key_auth_combined_initial_keys_and_env(monkeypatch):
    """测试初始化密钥和环境变量密钥合并"""
    monkeypatch.setenv("DEEPRESEARCH_API_KEYS", "env-key1, env-key2")
    auth = APIKeyAuth(api_keys=["init-key1", "init-key2"])
    assert auth.has_keys is True
    assert auth.validate_key("init-key1") is True
    assert auth.validate_key("env-key1") is True


def test_singleton_instance():
    """测试全局单例实例存在"""
    assert api_key_auth is not None


@pytest.mark.asyncio
async def test_get_api_key_valid():
    """测试 get_api_key 依赖在有效密钥时返回密钥"""
    from deepresearch.api.auth import APIKeyAuth
    import deepresearch.api.auth as auth_module
    original_auth = auth_module.api_key_auth
    auth_module.api_key_auth = APIKeyAuth(api_keys=["test-key"])

    result = await get_api_key("test-key")
    assert result == "test-key"

    auth_module.api_key_auth = original_auth


@pytest.mark.asyncio
async def test_get_api_key_invalid():
    """测试 get_api_key 依赖在无效密钥时抛出 401 异常"""
    from deepresearch.api.auth import APIKeyAuth
    import deepresearch.api.auth as auth_module
    original_auth = auth_module.api_key_auth
    auth_module.api_key_auth = APIKeyAuth(api_keys=["valid-key"])

    with pytest.raises(HTTPException) as exc_info:
        await get_api_key("wrong-key")

    assert exc_info.value.status_code == 401
    assert "Invalid or missing API key" in exc_info.value.detail

    auth_module.api_key_auth = original_auth


@pytest.mark.asyncio
async def test_get_api_key_missing():
    """测试 get_api_key 依赖在缺少密钥时抛出 401 异常"""
    from deepresearch.api.auth import APIKeyAuth
    import deepresearch.api.auth as auth_module
    original_auth = auth_module.api_key_auth
    auth_module.api_key_auth = APIKeyAuth(api_keys=["valid-key"])

    with pytest.raises(HTTPException) as exc_info:
        await get_api_key(None)

    assert exc_info.value.status_code == 401

    auth_module.api_key_auth = original_auth


@pytest.mark.asyncio
async def test_get_api_key_no_keys_configured():
    """测试没有配置密钥时，任何密钥都通过"""
    from deepresearch.api.auth import APIKeyAuth
    import deepresearch.api.auth as auth_module
    original_auth = auth_module.api_key_auth
    auth_module.api_key_auth = APIKeyAuth()

    result = await get_api_key(None)
    assert result is None

    auth_module.api_key_auth = original_auth


def test_has_keys_property():
    """测试 has_keys 属性"""
    auth = APIKeyAuth()
    assert auth.has_keys is False

    auth.add_key("test")
    assert auth.has_keys is True

    auth.remove_key("test")
    assert auth.has_keys is False
