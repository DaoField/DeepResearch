# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
CLI异常模块单元测试
"""

import pytest

from deepresearch.cli.exceptions import (
    CLIError,
    ConfigurationError,
    UserInterruptError,
    AgentExecutionError,
    ValidationError,
    FileOperationError,
)
from deepresearch.errors import DeepResearchError


class TestCLIError:
    """测试CLIError基类。"""

    def test_inheritance(self):
        """测试继承关系。"""
        error = CLIError("test message")
        assert isinstance(error, DeepResearchError)
        assert isinstance(error, Exception)

    def test_default_exit_code(self):
        """测试默认退出码。"""
        error = CLIError("test message")
        assert error.exit_code == 1
        assert str(error) == "test message"

    def test_custom_exit_code(self):
        """测试自定义退出码。"""
        error = CLIError("test message", exit_code=42)
        assert error.exit_code == 42


class TestConfigurationError:
    """测试ConfigurationError类。"""

    def test_exit_code(self):
        """测试退出码。"""
        error = ConfigurationError("config error")
        assert error.exit_code == 2
        assert str(error) == "config error"

    def test_inheritance(self):
        """测试继承关系。"""
        error = ConfigurationError("test")
        assert isinstance(error, CLIError)


class TestUserInterruptError:
    """测试UserInterruptError类。"""

    def test_default_message(self):
        """测试默认消息。"""
        error = UserInterruptError()
        assert error.exit_code == 130
        assert str(error) == "用户中断操作"

    def test_custom_message(self):
        """测试自定义消息。"""
        error = UserInterruptError("custom interrupt")
        assert str(error) == "custom interrupt"
        assert error.exit_code == 130


class TestAgentExecutionError:
    """测试AgentExecutionError类。"""

    def test_exit_code(self):
        """测试退出码。"""
        error = AgentExecutionError("execution failed")
        assert error.exit_code == 3

    def test_original_error(self):
        """测试原始错误。"""
        original = ValueError("original")
        error = AgentExecutionError("execution failed", original_error=original)
        assert error.original_error is original
        assert isinstance(error.original_error, ValueError)

    def test_no_original_error(self):
        """测试无原始错误。"""
        error = AgentExecutionError("execution failed")
        assert error.original_error is None


class TestValidationError:
    """测试ValidationError类。"""

    def test_exit_code(self):
        """测试退出码。"""
        error = ValidationError("validation failed")
        assert error.exit_code == 4
        assert str(error) == "validation failed"


class TestFileOperationError:
    """测试FileOperationError类。"""

    def test_exit_code(self):
        """测试退出码。"""
        error = FileOperationError("file error")
        assert error.exit_code == 5

    def test_with_path(self):
        """测试带路径的错误。"""
        error = FileOperationError("cannot read file", path="/path/to/file")
        assert error.path == "/path/to/file"

    def test_without_path(self):
        """测试不带路径的错误。"""
        error = FileOperationError("file error")
        assert error.path is None


class TestExceptionHierarchy:
    """测试异常层次结构。"""

    def test_all_inherit_from_cli_error(self):
        """测试所有异常都继承自CLIError。"""
        exceptions = [
            ConfigurationError("test"),
            UserInterruptError(),
            AgentExecutionError("test"),
            ValidationError("test"),
            FileOperationError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, CLIError)

    def test_catch_all_cli_errors(self):
        """测试捕获所有CLI错误。"""
        exceptions = [
            ConfigurationError("test"),
            UserInterruptError(),
            AgentExecutionError("test"),
            ValidationError("test"),
            FileOperationError("test"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except CLIError as e:
                assert e is exc

    def test_unique_exit_codes(self):
        """测试每个异常类有唯一的退出码。"""
        exit_codes = {
            CLIError: CLIError("test").exit_code,
            ConfigurationError: ConfigurationError("test").exit_code,
            UserInterruptError: UserInterruptError().exit_code,
            AgentExecutionError: AgentExecutionError("test").exit_code,
            ValidationError: ValidationError("test").exit_code,
            FileOperationError: FileOperationError("test").exit_code,
        }

        # 验证每个退出码都是唯一的（CLIError默认1除外）
        unique_codes = set(exit_codes.values())
        assert len(unique_codes) == len(exit_codes)
