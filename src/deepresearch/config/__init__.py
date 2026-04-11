# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

"""
DeepResearch 配置模块。

提供统一的配置管理功能，支持：
- 多层级配置覆盖（环境变量 > 配置文件 > 默认值）
- 配置验证
- 敏感信息脱敏
- 动态配置目录
"""

from .base import (
    # 配置基类
    BaseConfig,
    ChoiceValidator,
    # 异常类
    ConfigError,
    # 配置字段定义
    ConfigField,
    # 配置管理器
    ConfigManager,
    # 枚举
    ConfigSource,
    # 验证器
    ConfigValidator,
    # 配置值包装
    ConfigValue,
    RangeValidator,
    TypeValidator,
    ValidationError,
    WATCHDOG_AVAILABLE,
    add_sensitive_key,
    clear_config_cache,
    config_manager,
    # 原有函数（向后兼容）
    get_config_dir,
    # 便捷函数
    load_config,
    load_toml_config,
    redact_config,
    remove_sensitive_key,
    start_watching,
    stop_watching,
)

__all__ = [
    # 异常类
    "ConfigError",
    "ValidationError",
    # 枚举
    "ConfigSource",
    # 配置值
    "ConfigValue",
    # 验证器
    "ConfigValidator",
    "RangeValidator",
    "ChoiceValidator",
    "TypeValidator",
    # 配置字段
    "ConfigField",
    # 配置基类
    "BaseConfig",
    # 配置管理器
    "ConfigManager",
    "config_manager",
    # 便捷函数
    "load_config",
    # 配置热加载
    "start_watching",
    "stop_watching",
    "WATCHDOG_AVAILABLE",
    # 向后兼容
    "get_config_dir",
    "load_toml_config",
    "redact_config",
    "clear_config_cache",
    "add_sensitive_key",
    "remove_sensitive_key",
]
