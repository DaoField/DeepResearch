"""日志配置模块。

提供统一的日志配置功能，支持控制台和文件输出。
"""

import logging
import sys
from pathlib import Path
from typing import Literal

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
    log_file: Path | str | None = None,
    format_string: str | None = None,
    date_format: str | None = None,
) -> None:
    """配置日志系统。

    Args:
        level: 日志级别，默认为 "INFO"。
        log_file: 日志文件路径，如果为 None 则只输出到控制台。
        format_string: 日志格式字符串，如果为 None 则使用默认格式。
        date_format: 日期格式字符串，如果为 None 则使用默认格式。
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    log_fmt = format_string or _LOG_FORMAT
    log_date_fmt = date_format or _DATE_FORMAT

    handlers: list[logging.Handler] = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_fmt, datefmt=log_date_fmt))
    handlers.append(console_handler)

    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_fmt, datefmt=log_date_fmt))
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        format=log_fmt,
        datefmt=log_date_fmt,
        handlers=handlers,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器。

    Args:
        name: 日志记录器名称，通常使用 __name__。

    Returns:
        配置好的 Logger 实例。
    """
    return logging.getLogger(name)
