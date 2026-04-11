# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from deepresearch.api.auth import APIKeyAuth, api_key_auth
from deepresearch.api.main import app
from deepresearch.api.models import (
    CreateResearchRequest,
    CreateResearchResponse,
    ErrorResponse,
    ProgressEvent,
    ResearchStatusResponse,
    VersionInfo,
)
from deepresearch.api.task_manager import ResearchTask, TaskManager, task_manager

__all__ = [
    "app",
    "APIKeyAuth",
    "api_key_auth",
    "CreateResearchRequest",
    "CreateResearchResponse",
    "ResearchStatusResponse",
    "ProgressEvent",
    "ErrorResponse",
    "VersionInfo",
    "ResearchTask",
    "TaskManager",
    "task_manager",
]
