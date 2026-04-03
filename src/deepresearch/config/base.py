# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any


class ConfigError(Exception):
    """配置加载错误。"""
    pass


def _clone_toml_value(value: Any) -> Any:
    """深拷贝 TOML 配置值。"""
    if isinstance(value, dict):
        return {k: _clone_toml_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clone_toml_value(v) for v in value]
    return value


@lru_cache(maxsize=16)
def _load_toml_table_from_path(resolved_path: str) -> dict[str, Any]:
    """从文件路径加载 TOML 配置（带缓存）。"""
    try:
        with Path(resolved_path).open("rb") as file_handle:
            data = tomllib.load(file_handle)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"配置文件解析失败：{resolved_path}") from exc
    except OSError as exc:
        raise ConfigError(f"无法读取配置文件：{resolved_path}") from exc
    if not isinstance(data, dict):
        raise ConfigError("配置文件必须解析为 TOML table")
    return data


def get_config_dir() -> Path:
    """获取项目配置目录路径。"""
    return Path(__file__).parent.parent.parent.parent / "config"


def load_toml_config(config_filename: str) -> dict[str, Any]:
    """加载 TOML 配置文件（返回深拷贝）。"""
    config_path = get_config_dir() / config_filename
    path = config_path.expanduser().resolve()
    data = _load_toml_table_from_path(str(path))
    return _clone_toml_value(data)


def redact_config(config: dict[str, Any]) -> dict[str, Any]:
    """脱敏配置，隐藏敏感字段（api_key, password, secret 等）。"""
    cloned: dict[str, Any] = _clone_toml_value(config)
    
    sensitive_keys = {"api_key", "password", "secret", "jina_api_key", "tavily_api_key"}
    
    def _redact_dict(d: dict[str, Any]) -> None:
        for k, v in d.items():
            if isinstance(v, dict):
                _redact_dict(v)
            elif k.lower() in sensitive_keys:
                d[k] = "***"
    
    _redact_dict(cloned)
    return cloned


def clear_config_cache() -> None:
    """清理配置读取缓存（用于测试或动态更新配置文件的场景）。"""
    _load_toml_table_from_path.cache_clear()
