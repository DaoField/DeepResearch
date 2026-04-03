# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from .base import load_toml_config, redact_config


def load_workflow_configs() -> dict:
    """
    Load and parse workflow configuration file

    Returns:
        Dictionary containing workflow configuration

    Raises:
        FileNotFoundError: If the configuration file does not exist
        ValueError: If the configuration file has an invalid format
    """
    return load_toml_config("workflow.toml")


def get_redacted_workflow_configs() -> dict:
    """获取脱敏后的工作流配置。"""
    raw_config = load_toml_config("workflow.toml")
    return redact_config(raw_config)


workflow_configs = load_workflow_configs()
