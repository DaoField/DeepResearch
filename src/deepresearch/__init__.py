# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from deepresearch.agent.agent import build_agent
from deepresearch.errors import (
    ConfigError,
    DeepResearchError,
    LLMError,
    ReportError,
    SearchError,
)
from deepresearch.logging_config import configure_logging, get_logger

try:
    from deepresearch._version import __version__
except ImportError:
    __version__ = "unknown"

__all__ = [
    "build_agent",
    "configure_logging",
    "get_logger",
    "DeepResearchError",
    "ConfigError",
    "SearchError",
    "LLMError",
    "ReportError",
    "__version__",
]
