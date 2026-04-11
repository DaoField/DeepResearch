# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from dataclasses import dataclass
from typing import Literal, TypeVar

from .base import clear_config_cache, config_manager, load_toml_config, redact_config

T = TypeVar("T", bound="BaseLLMConfig")


@dataclass(kw_only=True)
class BaseLLMConfig:
    """Base LLM configuration class containing common configuration items for all LLMs"""

    base_url: str
    api_base: str
    model: str
    api_key: str

    @classmethod
    def from_dict(cls: type[T], config_dict: dict[str, str]) -> T:
        """
        Create an instance from a dictionary with type safety validation

        Args:
            config_dict: Dictionary containing LLM configuration parameters

        Returns:
            Instance of BaseLLMConfig or its subclass

        Raises:
            ValueError: If required fields are missing in the configuration
        """
        try:
            return cls(
                base_url=config_dict.get("base_url", ""),
                api_base=config_dict.get("api_base", ""),
                model=config_dict["model"],
                api_key=config_dict["api_key"],
            )
        except KeyError as e:
            raise ValueError(f"Configuration missing required field: {e}") from e


def load_llm_configs() -> dict[str, BaseLLMConfig]:
    """
    Load and parse LLM configuration file, return dictionary of all LLM config instances

    Returns:
        Dictionary with configuration names as keys and BaseLLMConfig instances as values

    Raises:
        FileNotFoundError: If the configuration file does not exist
        ValueError: If the configuration file has an invalid format
    """
    raw_config = load_toml_config("llms.toml")
    configs = {}
    for config_name, config_data in raw_config.items():
        configs[config_name] = BaseLLMConfig.from_dict(config_data)
    return configs


def get_redacted_llm_configs() -> dict:
    """获取脱敏后的 LLM 配置（隐藏敏感信息）。"""
    raw_config = load_toml_config("llms.toml")
    return redact_config(raw_config)


def reload_llm_configs() -> None:
    """重新加载 LLM 配置（清除缓存并重新加载）。"""
    clear_config_cache()
    global _llm_configs_cache
    _llm_configs_cache = None


def _on_config_reload() -> None:
    """配置重新加载回调（供 ConfigManager 调用）。"""
    reload_llm_configs()


_llm_configs_cache: dict[str, BaseLLMConfig] | None = None


def get_llm_configs() -> dict[str, BaseLLMConfig]:
    """获取 LLM 配置（懒加载）。"""
    global _llm_configs_cache
    if _llm_configs_cache is None:
        _llm_configs_cache = load_llm_configs()
    return _llm_configs_cache


LLMType = Literal[
    "basic", "clarify", "planner", "query_generation", "evaluate", "report"
]


def get_basic_llm() -> BaseLLMConfig:
    return get_llm_configs()["basic"]


def get_clarify_llm() -> BaseLLMConfig:
    return get_llm_configs()["clarify"]


def get_planner_llm() -> BaseLLMConfig:
    return get_llm_configs()["planner"]


def get_query_generation_llm() -> BaseLLMConfig:
    return get_llm_configs()["query_generation"]


def get_evaluate_llm() -> BaseLLMConfig:
    return get_llm_configs()["evaluate"]


def get_report_llm() -> BaseLLMConfig:
    return get_llm_configs()["report"]


# 在模块加载完成后注册重新加载回调
config_manager.register_reload_callback(_on_config_reload)
