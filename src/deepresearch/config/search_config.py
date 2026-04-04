# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from dataclasses import dataclass
from typing import TypeVar

from .base import load_toml_config, redact_config

T = TypeVar("T", bound="SearchConfig")


@dataclass(kw_only=True)
class SearchConfig:
    """Search engine configuration class containing search service parameters"""

    engine: str
    jina_api_key: str
    tavily_api_key: str
    timeout: int = 30

    @classmethod
    def from_dict(cls: type[T], config_dict: dict[str, str]) -> T:
        """
        Create an instance from a dictionary with validation

        Args:
            config_dict: Dictionary containing search configuration parameters

        Returns:
            Instance of SearchConfig

        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = ["engine"]
        for field in required_fields:
            if field not in config_dict:
                raise ValueError(f"Configuration missing required field: {field}")

        timeout = config_dict.get("timeout", 30)
        try:
            timeout = int(timeout)
            if timeout < 1 or timeout > 300:
                raise ValueError("Timeout must be between 1 and 300 seconds")
        except ValueError, TypeError:
            raise ValueError("Timeout must be a valid integer")

        return cls(
            engine=config_dict["engine"],
            jina_api_key=config_dict.get("jina_api_key", ""),
            tavily_api_key=config_dict.get("tavily_api_key", ""),
            timeout=timeout,
        )


def load_search_config() -> SearchConfig:
    """
    Load and parse search configuration file, return SearchConfig instance

    Returns:
        SearchConfig instance containing search service configuration

    Raises:
        FileNotFoundError: If the configuration file does not exist
        ValueError: If the configuration file has an invalid format
    """
    raw_config = load_toml_config("search.toml")
    if "search" not in raw_config:
        raise ValueError(
            "Invalid configuration file format. Expected [search] section."
        )
    return SearchConfig.from_dict(raw_config["search"])


def get_redacted_search_config() -> dict:
    """获取脱敏后的搜索配置（隐藏敏感信息）。"""
    raw_config = load_toml_config("search.toml")
    return redact_config(raw_config)


search_config = load_search_config()
