# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from deepresearch.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class CLIConfig:
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
        object.__setattr__(self, "max_depth", max(1, min(self.max_depth, 10)))
        object.__setattr__(self, "max_history", max(10, min(self.max_history, 1000)))
        object.__setattr__(self, "timeout", max(30, min(self.timeout, 3600)))

    @classmethod
    def from_env(cls) -> CLIConfig:
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
        return Path(self.save_path).expanduser().resolve()

    def get_history_path(self) -> Path | None:
        if self.history_file:
            return Path(self.history_file).expanduser().resolve()
        return None

    def get_config_dir(self) -> Path:
        if self.config_dir:
            return Path(self.config_dir).expanduser().resolve()
        return Path.home() / ".deepresearch"


def get_cli_config(
    max_depth: int | None = None,
    save_as_html: bool | None = None,
    save_path: str | None = None,
    log_level: str | None = None,
    config_dir: str | None = None,
) -> CLIConfig:
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
