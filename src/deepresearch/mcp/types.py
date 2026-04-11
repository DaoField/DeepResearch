# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional
from uuid import uuid4


class CollaborationStatus(str, Enum):
    """协作会话状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class MessageType(str, Enum):
    """消息类型"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    WARNING = "warning"
    CONFLICT = "conflict"
    SYSTEM = "system"


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    ERROR = "error"


class TaskPriority(str, Enum):
    """任务优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CollaborationMode(str, Enum):
    """协作模式"""
    SERIAL = "serial"
    PARALLEL = "parallel"
    ROUND_ROBIN = "round_robin"


class AgentCollaborationMode(str, Enum):
    """智能体协作角色模式"""
    LEADER = "leader"
    COLLABORATOR = "collaborator"
    REVIEWER = "reviewer"


class ResponseStyle(str, Enum):
    """响应风格"""
    FORMAL = "formal"
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"


class OutputDetail(str, Enum):
    """输出详细程度"""
    CONCISE = "concise"
    NORMAL = "normal"
    DETAILED = "detailed"


@dataclass
class AgentConfig:
    """智能体配置"""
    id: str
    name: str
    avatar: str
    role: str
    specialty: list[str]
    description: str
    skills: list[str]
    level: int
    response_style: ResponseStyle
    output_detail: OutputDetail
    tools: list[str]
    collaboration_mode: AgentCollaborationMode
    llm_config_id: str = "default"
    system_prompt: Optional[str] = None
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "avatar": self.avatar,
            "role": self.role,
            "specialty": self.specialty,
            "description": self.description,
            "skills": self.skills,
            "level": self.level,
            "response_style": self.response_style.value,
            "output_detail": self.output_detail.value,
            "tools": self.tools,
            "collaboration_mode": self.collaboration_mode.value,
            "llm_config_id": self.llm_config_id,
            "system_prompt": self.system_prompt,
            "enabled": self.enabled,
        }


@dataclass
class Task:
    """协作任务"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    progress: float = 0.0
    assigned_agent_id: Optional[str] = None
    subtasks: list["Task"] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_time: Optional[int] = None
    result: Optional[str] = None
    quality_score: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "progress": self.progress,
            "assigned_agent_id": self.assigned_agent_id,
            "subtasks": [t.to_dict() for t in self.subtasks],
            "dependencies": self.dependencies,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "estimated_time": self.estimated_time,
            "result": self.result,
            "quality_score": self.quality_score,
        }


@dataclass
class Message:
    """智能体间消息"""
    id: str
    from_agent_id: str
    from_agent_name: str
    to_agent_id: Optional[str]
    to_agent_name: Optional[str]
    message_type: MessageType
    content: str
    timestamp: datetime
    session_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "from_agent_id": self.from_agent_id,
            "from_agent_name": self.from_agent_name,
            "to_agent_id": self.to_agent_id,
            "to_agent_name": self.to_agent_name,
            "type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
        }

    @classmethod
    def create(
        cls,
        from_agent_id: str,
        from_agent_name: str,
        content: str,
        session_id: str,
        to_agent_id: Optional[str] = None,
        to_agent_name: Optional[str] = None,
        message_type: MessageType = MessageType.REQUEST,
    ) -> "Message":
        return cls(
            id=str(uuid4()),
            from_agent_id=from_agent_id,
            from_agent_name=from_agent_name,
            to_agent_id=to_agent_id,
            to_agent_name=to_agent_name,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            session_id=session_id,
        )


@dataclass
class AgentResult:
    """智能体输出结果"""
    agent_id: str
    agent_name: str
    output: str
    score: float
    feedback: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "output": self.output,
            "score": self.score,
            "feedback": self.feedback,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class CollaborationResult:
    """协作结果"""
    id: str
    session_id: str
    summary: str
    agent_results: list[AgentResult]
    overall_score: float
    export_formats: list[str] = field(default_factory=lambda: ["markdown", "json"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "summary": self.summary,
            "agent_results": [ar.to_dict() for ar in self.agent_results],
            "overall_score": self.overall_score,
            "export_formats": self.export_formats,
        }


@dataclass
class CollaborationSession:
    """协作会话"""
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    agent_ids: list[str]
    tasks: list[Task]
    status: CollaborationStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[CollaborationResult] = None
    mode: CollaborationMode = CollaborationMode.SERIAL
    created_by: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "agent_ids": self.agent_ids,
            "tasks": [t.to_dict() for t in self.tasks],
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
            "mode": self.mode.value,
            "created_by": self.created_by,
        }

    @classmethod
    def create(
        cls,
        title: str,
        agent_ids: list[str],
        tasks: list[Task],
        mode: CollaborationMode = CollaborationMode.SERIAL,
        created_by: Optional[str] = None,
    ) -> "CollaborationSession":
        now = datetime.now()
        return cls(
            session_id=str(uuid4()),
            title=title,
            created_at=now,
            updated_at=now,
            started_at=None,
            completed_at=None,
            agent_ids=agent_ids,
            tasks=tasks,
            status=CollaborationStatus.PENDING,
            mode=mode,
            created_by=created_by,
        )


@dataclass
class ProgressEvent:
    """进度事件"""
    session_id: str
    status: CollaborationStatus
    progress: float
    current_step: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    new_message: Optional[Message] = None
    task_update: Optional[Task] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "new_message": self.new_message.to_dict() if self.new_message else None,
            "task_update": self.task_update.to_dict() if self.task_update else None,
        }


@dataclass
class MCPCollaborationCreateRequest:
    """创建协作请求"""
    title: str
    agent_ids: list[str]
    tasks: Optional[list[dict[str, Any]]] = None
    mode: str = "serial"
    description: Optional[str] = None


@dataclass
class MCPCollaborationCreateResponse:
    """创建协作响应"""
    session_id: str
    status: str
    message: str


@dataclass
class MCPCollaborationStatusResponse:
    """获取协作状态响应"""
    session_id: str
    title: str
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress: float
    agent_ids: list[str]
    tasks: list[dict[str, Any]]
    messages: list[dict[str, Any]]
    result: Optional[dict[str, Any]]
    error: Optional[str] = None


@dataclass
class MCPAgentInfo:
    """智能体信息响应"""
    id: str
    name: str
    avatar: str
    role: str
    specialty: list[str]
    description: str
    skills: list[str]
    level: int
    collaboration_mode: str
    enabled: bool


@dataclass
class MCPListAgentsResponse:
    """获取智能体列表响应"""
    agents: list[MCPAgentInfo]
    total: int
