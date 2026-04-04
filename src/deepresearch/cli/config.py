# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
CLI 配置模块

提供CLI配置管理和默认值设置。
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from deepresearch.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class CLIConfig:
    """CLI 配置类。

    Attributes:
        max_depth: 最大搜索深度，范围 1-10
        save_as_html: 是否保存为HTML格式
        save_path: 报告保存路径
        log_level: 日志级别
        log_file: 日志文件路径，None表示只输出到控制台
        history_file: 命令历史文件路径
        max_history: 最大历史记录数
        stream_output: 是否流式输出
        timeout: Agent执行超时时间（秒）
        theme: 输出主题样式
        config_dir: 配置文件目录路径，None表示使用默认路径
    """

    max_depth: int = 3
    save_as_html: bool = True
    save_path: str = "./example/report"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_file: str | None = None
    history_file: str | None = None
    max_history: int = 100
    stream_output: bool = True
    timeout: int = 300
    theme: Literal["default", "minimal", "colorful"] = "default"
    config_dir: str | None = None

    def __post_init__(self) -> None:
        """验证配置值的有效性。"""
        object.__setattr__(self, "max_depth", max(1, min(self.max_depth, 10)))
        object.__setattr__(self, "max_history", max(10, min(self.max_history, 1000)))
        object.__setattr__(self, "timeout", max(30, min(self.timeout, 3600)))

    @classmethod
    def from_env(cls) -> CLIConfig:
        """从环境变量加载配置。"""
        return cls(
            max_depth=int(os.getenv("DEEPRESEARCH_MAX_DEPTH", "3")),
            save_as_html=os.getenv("DEEPRESEARCH_SAVE_AS_HTML", "true").lower()
            == "true",
            save_path=os.getenv("DEEPRESEARCH_SAVE_PATH", "./example/report"),
            log_level=os.getenv("DEEPRESEARCH_LOG_LEVEL", "INFO"),  # type: ignore
            log_file=os.getenv("DEEPRESEARCH_LOG_FILE"),
            history_file=os.getenv("DEEPRESEARCH_HISTORY_FILE"),
            max_history=int(os.getenv("DEEPRESEARCH_MAX_HISTORY", "100")),
            stream_output=os.getenv("DEEPRESEARCH_STREAM_OUTPUT", "true").lower()
            == "true",
            timeout=int(os.getenv("DEEPRESEARCH_TIMEOUT", "300")),
            theme=os.getenv("DEEPRESEARCH_THEME", "default"),  # type: ignore
            config_dir=os.getenv("DEEPRESEARCH_CONFIG_DIR"),
        )

    def get_save_path(self) -> Path:
        """获取保存路径的Path对象。"""
        return Path(self.save_path).expanduser().resolve()

    def get_history_path(self) -> Path | None:
        """获取历史文件路径。"""
        if self.history_file:
            return Path(self.history_file).expanduser().resolve()
        return None

    def get_config_dir(self) -> Path:
        """获取配置目录的Path对象。

        Returns:
            配置目录的Path对象。如果config_dir为None，则返回默认路径
        """
        if self.config_dir:
            return Path(self.config_dir).expanduser().resolve()
        # 默认配置目录：用户主目录下的 .deepresearch 文件夹
        return Path.home() / ".deepresearch"


def get_cli_config(
    max_depth: int | None = None,
    save_as_html: bool | None = None,
    save_path: str | None = None,
    log_level: str | None = None,
    config_dir: str | None = None,
) -> CLIConfig:
    """获取CLI配置，支持从环境变量和参数合并。

    Args:
        max_depth: 最大搜索深度
        save_as_html: 是否保存为HTML
        save_path: 保存路径
        log_level: 日志级别
        config_dir: 配置文件目录路径

    Returns:
        合并后的CLI配置
    """
    config = CLIConfig.from_env()

    kwargs: dict[str, object] = {}
    if max_depth is not None:
        kwargs["max_depth"] = max_depth
    if save_as_html is not None:
        kwargs["save_as_html"] = save_as_html
    if save_path is not None:
        kwargs["save_path"] = save_path
    if log_level is not None:
        kwargs["log_level"] = log_level  # type: ignore
    if config_dir is not None:
        kwargs["config_dir"] = config_dir

    if kwargs:
        config = CLIConfig(
            **{
                **{k: getattr(config, k) for k in CLIConfig.__dataclass_fields__},
                **kwargs,
            }
        )

    logger.debug(
        f"CLI配置加载完成: max_depth={config.max_depth}, "
        f"save_as_html={config.save_as_html}, save_path={config.save_path}"
    )

    return config
