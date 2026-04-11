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


# ========== MCP (Multi-Agent Collaboration Platform) Models ==========

class MCPAgentInfo(BaseModel):
    """MCP 智能体信息。"""

    id: str = Field(..., description="智能体ID")
    name: str = Field(..., description="智能体名称")
    avatar: str = Field(..., description="头像emoji")
    role: str = Field(..., description="角色")
    specialty: list[str] = Field(default_factory=list, description="专长领域")
    description: str = Field(..., description="描述")
    skills: list[str] = Field(default_factory=list, description="技能列表")
    level: int = Field(..., description="能力等级 0-100")
    collaboration_mode: str = Field(..., description="协作模式")
    enabled: bool = Field(default=True, description="是否启用")


class MCPListAgentsResponse(BaseModel):
    """获取智能体列表响应。"""

    agents: list[MCPAgentInfo] = Field(default_factory=list, description="智能体列表")
    total: int = Field(..., description="总数")


class MCPCollaborationCreateRequest(BaseModel):
    """创建协作请求。"""

    title: str = Field(..., description="协作标题", min_length=1)
    agent_ids: list[str] = Field(..., description="选中的智能体ID列表", min_length=1)
    tasks: list[dict[str, Any]] | None = Field(
        default=None, description="预定义任务列表"
    )
    mode: str = Field(
        default="serial",
        description="协作模式: serial(串行) | parallel(并行) | round_robin(轮询)"
    )
    description: str | None = Field(default=None, description="额外描述")


class MCPCollaborationCreateResponse(BaseModel):
    """创建协作响应。"""

    session_id: str = Field(..., description="会话ID")
    status: str = Field(..., description="会话状态")
    message: str = Field(
        default="Collaboration session created successfully",
        description="响应消息"
    )


class MCPTask(BaseModel):
    """MCP 任务信息。"""

    id: str = Field(..., description="任务ID")
    title: str = Field(..., description="任务标题")
    description: str = Field(..., description="任务描述")
    status: str = Field(..., description="任务状态")
    priority: str = Field(..., description="优先级")
    progress: float = Field(default=0.0, description="进度 0-100")
    assigned_agent_id: str | None = Field(default=None, description="分配的智能体ID")
    estimated_time: int | None = Field(default=None, description="预估时间（分钟）")
    result: str | None = Field(default=None, description="任务结果")
    quality_score: float | None = Field(default=None, description="质量评分")


class MCPMessage(BaseModel):
    """MCP 消息。"""

    id: str = Field(..., description="消息ID")
    from_agent_id: str = Field(..., description="发送者智能体ID")
    from_agent_name: str = Field(..., description="发送者名称")
    to_agent_id: str | None = Field(default=None, description="接收者智能体ID")
    to_agent_name: str | None = Field(default=None, description="接收者名称")
    type: str = Field(..., description="消息类型")
    content: str = Field(..., description="消息内容")
    timestamp: str = Field(..., description="时间戳")


class MCPAgentResult(BaseModel):
    """智能体结果。"""

    agent_id: str = Field(..., description="智能体ID")
    agent_name: str = Field(..., description="智能体名称")
    output: str = Field(..., description="输出内容")
    score: float = Field(..., description="评分")
    feedback: str | None = Field(default=None, description="反馈")
    timestamp: str = Field(..., description="时间戳")


class MCPCollaborationResult(BaseModel):
    """协作结果。"""

    id: str = Field(..., description="结果ID")
    session_id: str = Field(..., description="会话ID")
    summary: str = Field(..., description="汇总")
    agent_results: list[MCPAgentResult] = Field(default_factory=list, description="智能体结果列表")
    overall_score: float = Field(..., description="总体评分")
    export_formats: list[str] = Field(default_factory=list, description="可导出格式")


class MCPCollaborationStatusResponse(BaseModel):
    """获取协作状态响应。"""

    session_id: str = Field(..., description="会话ID")
    title: str = Field(..., description="协作标题")
    status: str = Field(..., description="会话状态")
    created_at: datetime = Field(..., description="创建时间")
    started_at: datetime | None = Field(default=None, description="开始时间")
    completed_at: datetime | None = Field(default=None, description="完成时间")
    progress: float = Field(default=0.0, description="进度 0-1")
    agent_ids: list[str] = Field(default_factory=list, description="参与的智能体ID列表")
    tasks: list[MCPTask] = Field(default_factory=list, description="任务列表")
    messages: list[MCPMessage] = Field(default_factory=list, description="消息列表")
    result: MCPCollaborationResult | None = Field(default=None, description="协作结果")
    error: str | None = Field(default=None, description="错误信息")


class MCPProgressEvent(BaseModel):
    """MCP SSE 进度事件。"""

    session_id: str = Field(..., description="会话ID")
    status: str = Field(..., description="当前状态")
    progress: float = Field(..., description="进度 0-1")
    current_step: str | None = Field(default=None, description="当前步骤")
    message: str | None = Field(default=None, description="进度消息")
    timestamp: str = Field(..., description="时间戳")
    new_message: MCPMessage | None = Field(default=None, description="新消息")
    task_update: MCPTask | None = Field(default=None, description="任务更新")


class MCPSendMessageRequest(BaseModel):
    """发送消息请求。"""

    from_agent_id: str = Field(..., description="发送者智能体ID")
    from_agent_name: str = Field(..., description="发送者名称")
    to_agent_id: str | None = Field(default=None, description="接收者智能体ID")
    to_agent_name: str | None = Field(default=None, description="接收者名称")
    content: str = Field(..., description="消息内容", min_length=1)
    message_type: str = Field(default="request", description="消息类型")


class MCPSendMessageResponse(BaseModel):
    """发送消息响应。"""

    message_id: str = Field(..., description="消息ID")
    status: str = Field(..., description="发送状态")
