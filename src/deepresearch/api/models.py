# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态枚举。"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CreateResearchRequest(BaseModel):
    """创建研究请求模型。"""

    topic: str = Field(..., description="研究主题", min_length=1)
    domain: str | None = Field(
        default=None, description="研究领域，如 'technology'、'medicine' 等"
    )
    details: str | None = Field(default=None, description="额外的研究细节要求")


class CreateResearchResponse(BaseModel):
    """创建研究响应模型。"""

    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    message: str = Field(
        default="Research task created successfully", description="响应消息"
    )


class ProgressStep(BaseModel):
    """进度步骤。"""

    name: str = Field(..., description="步骤名称")
    description: str = Field(..., description="步骤描述")
    status: TaskStatus = Field(..., description="步骤状态")


class ResearchStatusResponse(BaseModel):
    """研究任务状态响应。"""

    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务当前状态")
    topic: str = Field(..., description="研究主题")
    created_at: datetime = Field(..., description="创建时间")
    started_at: datetime | None = Field(default=None, description="开始时间")
    completed_at: datetime | None = Field(default=None, description="完成时间")
    progress: float = Field(default=0.0, description="进度百分比 (0-1)", ge=0, le=1)
    current_step: str | None = Field(default=None, description="当前步骤")
    steps: list[ProgressStep] = Field(default_factory=list, description="步骤列表")
    result: dict[str, Any] | None = Field(
        default=None, description="研究结果（完成时返回）"
    )
    error: str | None = Field(default=None, description="错误信息（失败时返回）")


class ProgressEvent(BaseModel):
    """SSE 进度事件。"""

    event: str = Field(..., description="事件类型")
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="当前状态")
    progress: float = Field(..., description="进度百分比 (0-1)")
    current_step: str | None = Field(default=None, description="当前步骤")
    message: str | None = Field(default=None, description="进度消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")
    data: dict[str, Any] | None = Field(default=None, description="附加数据")


class ErrorResponse(BaseModel):
    """错误响应。"""

    detail: str = Field(..., description="错误详情")
    status_code: int = Field(..., description="HTTP 状态码")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class VersionInfo(BaseModel):
    """版本信息响应。"""

    version: str = Field(..., description="API 版本")
    deepresearch_version: str = Field(..., description="DeepResearch 版本")
    name: str = Field(default="DeepResearch API", description="API 名称")
    description: str = Field(
        default="Deep Research API Service", description="API 描述"
    )


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="当前时间戳"
    )
    uptime_seconds: float = Field(..., description="服务运行时间（秒）")
