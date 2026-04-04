# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
CLI 模块异常定义

提供CLI相关的异常类，用于错误处理和用户反馈。
"""

from deepresearch.errors import DeepResearchError


class CLIError(DeepResearchError):
    """CLI 错误基类。"""

    def __init__(self, message: str, *, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class ConfigurationError(CLIError):
    """配置错误，如配置文件缺失或配置项不合法。"""

    def __init__(self, message: str) -> None:
        super().__init__(message, exit_code=2)


class UserInterruptError(CLIError):
    """用户中断错误，如按Ctrl+C中断程序。"""

    def __init__(self, message: str = "用户中断操作") -> None:
        super().__init__(message, exit_code=130)


class AgentExecutionError(CLIError):
    """Agent 执行错误。"""

    def __init__(
        self, message: str, *, original_error: Exception | None = None
    ) -> None:
        super().__init__(message, exit_code=3)
        self.original_error = original_error


class ValidationError(CLIError):
    """输入验证错误。"""

    def __init__(self, message: str) -> None:
        super().__init__(message, exit_code=4)


class FileOperationError(CLIError):
    """文件操作错误。"""

    def __init__(self, message: str, *, path: str | None = None) -> None:
        super().__init__(message, exit_code=5)
        self.path = path
