# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from dataclasses import dataclass
from typing import Dict, Type, TypeVar, Literal
from .base import load_toml_config, redact_config


T = TypeVar('T', bound='BaseLLMConfig')


@dataclass(kw_only=True)
class BaseLLMConfig:
    """Base LLM configuration class containing common configuration items for all LLMs"""
    base_url: str
    api_base: str
    model: str
    api_key: str

    @classmethod
    def from_dict(cls: Type[T], config_dict: Dict[str, str]) -> T:
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
                base_url=config_dict.get('base_url', ''),
                api_base=config_dict.get('api_base', ''),
                model=config_dict['model'],
                api_key=config_dict['api_key']
            )
        except KeyError as e:
            raise ValueError(f"Configuration missing required field: {e}") from e


def load_llm_configs() -> Dict[str, BaseLLMConfig]:
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


llm_configs = load_llm_configs()

LLMType = Literal["basic", "clarify", "planner", "query_generation", "evaluate", "report"]

basic_llm = llm_configs['basic']
clarify_llm = llm_configs['clarify']
planner_llm = llm_configs['planner']
query_generation_llm = llm_configs['query_generation']
evaluate_llm = llm_configs['evaluate']
report_llm = llm_configs['report']
