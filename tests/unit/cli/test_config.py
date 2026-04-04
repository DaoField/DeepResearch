# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
CLI配置模块单元测试
"""

import os
import pytest
from pathlib import Path

from deepresearch.cli.config import CLIConfig, get_cli_config


class TestCLIConfig:
    """测试CLIConfig类。"""

    def test_default_values(self):
        """测试默认值。"""
        config = CLIConfig()
        assert config.max_depth == 3
        assert config.save_as_html is True
        assert config.save_path == "./example/report"
        assert config.log_level == "INFO"
        assert config.log_file is None
        assert config.history_file is None
        assert config.max_history == 100
        assert config.stream_output is True
        assert config.timeout == 300
        assert config.theme == "default"

    def test_custom_values(self):
        """测试自定义值。"""
        config = CLIConfig(
            max_depth=5,
            save_as_html=False,
            save_path="./custom/path",
            log_level="DEBUG",
        )
        assert config.max_depth == 5
        assert config.save_as_html is False
        assert config.save_path == "./custom/path"
        assert config.log_level == "DEBUG"

    def test_max_depth_validation(self):
        """测试max_depth范围验证。"""
        # 测试小于1的值
        config = CLIConfig(max_depth=0)
        assert config.max_depth == 1

        # 测试大于10的值
        config = CLIConfig(max_depth=15)
        assert config.max_depth == 10

        # 测试边界值
        config = CLIConfig(max_depth=1)
        assert config.max_depth == 1
        config = CLIConfig(max_depth=10)
        assert config.max_depth == 10

    def test_max_history_validation(self):
        """测试max_history范围验证。"""
        # 测试小于10的值
        config = CLIConfig(max_history=5)
        assert config.max_history == 10

        # 测试大于1000的值
        config = CLIConfig(max_history=2000)
        assert config.max_history == 1000

    def test_timeout_validation(self):
        """测试timeout范围验证。"""
        # 测试小于30的值
        config = CLIConfig(timeout=10)
        assert config.timeout == 30

        # 测试大于3600的值
        config = CLIConfig(timeout=5000)
        assert config.timeout == 3600

    def test_get_save_path(self):
        """测试获取保存路径。"""
        config = CLIConfig(save_path="~/test/report")
        path = config.get_save_path()
        assert isinstance(path, Path)
        assert "test" in str(path)

    def test_get_history_path(self):
        """测试获取历史文件路径。"""
        # 有历史文件配置
        config = CLIConfig(history_file="~/test/history.json")
        path = config.get_history_path()
        assert isinstance(path, Path)
        assert "test" in str(path)

        # 无历史文件配置
        config = CLIConfig(history_file=None)
        assert config.get_history_path() is None


class TestGetCLIConfig:
    """测试get_cli_config函数。"""

    def test_default_config(self):
        """测试获取默认配置。"""
        config = get_cli_config()
        assert isinstance(config, CLIConfig)
        assert config.max_depth == 3

    def test_override_params(self):
        """测试参数覆盖。"""
        config = get_cli_config(
            max_depth=7,
            save_as_html=False,
            save_path="./override",
            log_level="ERROR",
        )
        assert config.max_depth == 7
        assert config.save_as_html is False
        assert config.save_path == "./override"
        assert config.log_level == "ERROR"

    def test_partial_override(self):
        """测试部分参数覆盖。"""
        config = get_cli_config(max_depth=5)
        assert config.max_depth == 5
        assert config.save_as_html is True  # 默认值

    def test_from_env(self, monkeypatch):
        """测试从环境变量加载配置。"""
        monkeypatch.setenv("DEEPRESEARCH_MAX_DEPTH", "8")
        monkeypatch.setenv("DEEPRESEARCH_SAVE_AS_HTML", "false")
        monkeypatch.setenv("DEEPRESEARCH_SAVE_PATH", "/env/path")
        monkeypatch.setenv("DEEPRESEARCH_LOG_LEVEL", "DEBUG")

        config = CLIConfig.from_env()
        assert config.max_depth == 8
        assert config.save_as_html is False
        assert config.save_path == "/env/path"
        assert config.log_level == "DEBUG"

    def test_env_and_param_merge(self, monkeypatch):
        """测试环境变量和参数合并。"""
        monkeypatch.setenv("DEEPRESEARCH_MAX_DEPTH", "8")

        # 环境变量设置max_depth=8，但参数覆盖为5
        config = get_cli_config(max_depth=5)
        assert config.max_depth == 5

    def test_invalid_env_values(self, monkeypatch):
        """测试无效的环境变量值。"""
        monkeypatch.setenv("DEEPRESEARCH_MAX_DEPTH", "invalid")

        # 应该使用默认值
        with pytest.raises(ValueError):
            CLIConfig.from_env()


class TestCLIConfigImmutability:
    """测试CLIConfig的不可变性。"""

    def test_frozen_dataclass(self):
        """测试dataclass是否frozen。"""
        config = CLIConfig()

        with pytest.raises(AttributeError):
            config.max_depth = 5

    def test_post_init_modification(self):
        """测试__post_init__中的修改。"""
        # 虽然dataclass是frozen的，但__post_init__可以修改
        config = CLIConfig(max_depth=0)
        # 应该被限制为1
        assert config.max_depth == 1
