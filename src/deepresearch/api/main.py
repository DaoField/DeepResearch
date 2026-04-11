# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from deepresearch import __version__ as deepresearch_version
from deepresearch.agent.agent import build_agent
from deepresearch.agent.message import ReportState
from deepresearch.api.auth import get_api_key
from deepresearch.api.models import (
    CreateResearchRequest,
    CreateResearchResponse,
    HealthResponse,
    MCPAgentInfo,
    MCPListAgentsResponse,
    MCPCollaborationCreateRequest,
    MCPCollaborationCreateResponse,
    MCPCollaborationStatusResponse,
    MCPSendMessageRequest,
    MCPSendMessageResponse,
    ResearchStatusResponse,
    VersionInfo,
)
from deepresearch.api.task_manager import ResearchTask, task_manager
from deepresearch.logging_config import get_logger
from deepresearch.mcp import (
    CollaborationMode,
    CollaborationSession,
    CollaborationStatus,
    Message,
    MessageType,
    ProgressEvent,
    agent_registry,
    collaboration_orchestrator,
    message_bus,
)
import asyncio
import json
from typing import Any, AsyncGenerator

logger = get_logger(__name__)


app = FastAPI(
    title="DeepResearch API",
    description="Deep Research API Service",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_agent = None


def get_agent():
    """获取或构建 agent。"""
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


async def execute_research(task: ResearchTask) -> dict[str, Any]:
    """执行深度研究任务。"""
    agent = get_agent()

    initial_state = ReportState(
        topic=task.topic,
        domain=task.domain or "",
        details=task.details or "",
        logic="",
        output={},
        knowledge=[],
        final_report="",
        search_id=0,
        outline=None,
        messages=[],
    )

    steps = [
        ("preprocess", "预处理查询", 0.1),
        ("rewrite", "重写查询", 0.2),
        ("classify", "分类查询", 0.3),
        ("clarify", "澄清需求", 0.4),
        ("outline_search", "大纲搜索", 0.5),
        ("outline", "生成大纲", 0.6),
        ("learning", "深度研究学习", 0.7),
        ("generate", "生成报告", 0.8),
        ("save_local_node", "保存结果", 0.9),
    ]

    for step_name, step_desc, progress in steps:
        if task.is_cancelled():
            break

        task.update_progress(
            progress=progress,
            current_step=step_name,
            message=step_desc,
        )
        await asyncio.sleep(0.1)

    result = await agent.ainvoke(initial_state)

    if task.is_cancelled():
        return {"cancelled": True, "topic": task.topic}

    final_report = result.get("final_report", "")
    outline = result.get("outline", None)
    knowledge = result.get("knowledge", [])
    output = result.get("output", {})

    return {
        "topic": task.topic,
        "domain": task.domain,
        "final_report": final_report,
        "knowledge": knowledge,
        "outline": outline,
        "output": output,
    }


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """健康检查端点。"""
    return HealthResponse(
        status="ok",
        uptime_seconds=task_manager.get_uptime_seconds(),
    )


@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """API 根路径 - 返回 API 信息和可用端点。"""
    return {
        "name": "DeepResearch API",
        "version": "1.0.0",
        "description": "Deep Research API Service - 深度研究服务",
        "documentation": {
            "openapi": "/api/v1/openapi.json",
            "swagger_docs": "/api/v1/docs",
            "redoc": "/api/v1/redoc",
        },
        "endpoints": {
            "health": "/api/v1/health",
            "version": "/api/v1/version",
            "research": "/api/v1/research",
            "mcp_agents": "/api/v1/mcp/agents",
            "collaboration": "/api/v1/mcp/collaboration",
        },
        "status": "operational",
    }


@app.get("/api/v1/version", response_model=VersionInfo, tags=["Info"])
async def get_version() -> VersionInfo:
    """获取版本信息。"""
    return VersionInfo(
        version="1.0.0",
        deepresearch_version=deepresearch_version,
    )


@app.post(
    "/api/v1/research",
    response_model=CreateResearchResponse,
    tags=["Research"],
    dependencies=[Depends(get_api_key)] if get_api_key else [],
)
async def create_research(
    request: CreateResearchRequest,
) -> CreateResearchResponse:
    """创建新的深度研究任务。"""
    task = task_manager.create_task(
        topic=request.topic,
        domain=request.domain,
        details=request.details,
    )

    asyncio.create_task(task_manager.run_task(task, execute_research))

    logger.info(f"Created research task {task.task_id} for topic: {request.topic}")

    return CreateResearchResponse(
        task_id=task.task_id,
        status=task.status,
        message="Research task created successfully",
    )


@app.get(
    "/api/v1/research/{task_id}",
    response_model=ResearchStatusResponse,
    tags=["Research"],
    dependencies=[Depends(get_api_key)] if get_api_key else [],
)
async def get_research_status(task_id: str) -> ResearchStatusResponse:
    """获取研究任务状态。"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    return ResearchStatusResponse(
        task_id=task.task_id,
        status=task.status,
        topic=task.topic,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        progress=task.progress,
        current_step=task.current_step,
        steps=task.steps,
        result=task.result,
        error=task.error,
    )


@app.get(
    "/api/v1/research/{task_id}/stream",
    tags=["Research"],
    dependencies=[Depends(get_api_key)] if get_api_key else [],
)
async def stream_research_progress(task_id: str) -> EventSourceResponse:
    """流式获取研究进度（SSE）。"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    async def event_generator() -> AsyncGenerator[dict[str, Any], None]:
        async for event in task.progress_stream():
            yield {
                "event": event.event,
                "data": json.dumps(event.model_dump(), default=str),
                "id": event.timestamp.isoformat(),
            }

    return EventSourceResponse(event_generator())


@app.delete(
    "/api/v1/research/{task_id}",
    tags=["Research"],
    dependencies=[Depends(get_api_key)] if get_api_key else [],
)
async def cancel_research(task_id: str) -> dict[str, Any]:
    """取消研究任务。"""
    cancelled = task_manager.cancel_task(task_id)
    if not cancelled:
        task = task_manager.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} cannot be cancelled (current status: {task.status})",
        )

    return {
        "task_id": task_id,
        "status": "cancelled",
        "message": "Task cancelled successfully",
    }


# ========== MCP Endpoints ==========

@app.get(
    "/api/v1/mcp/agents",
    response_model=MCPListAgentsResponse,
    tags=["MCP"],
    dependencies=[Depends(get_api_key)] if get_api_key else [],
)
async def list_mcp_agents() -> MCPListAgentsResponse:
    """获取所有可用的协作智能体列表."""
    agents = agent_registry.list_agents(only_enabled=True)
    agent_infos = [
        MCPAgentInfo(
            id=a.id,
            name=a.name,
            avatar=a.avatar,
            role=a.role,
            specialty=a.specialty,
            description=a.description,
            skills=a.skills,
            level=a.level,
            collaboration_mode=a.collaboration_mode.value,
            enabled=a.enabled,
        )
        for a in agents
    ]
    return MCPListAgentsResponse(
        agents=agent_infos,
        total=len(agent_infos),
    )


@app.post(
    "/api/v1/mcp/collaboration",
    response_model=MCPCollaborationCreateResponse,
    tags=["MCP"],
    dependencies=[Depends(get_api_key)] if get_api_key else [],
)
async def create_mcp_collaboration(
    request: MCPCollaborationCreateRequest,
) -> MCPCollaborationCreateResponse:
    """创建新的多智能体协作会话."""
    try:
        mode = CollaborationMode(request.mode)
    except ValueError:
        mode = CollaborationMode.SERIAL

    session = collaboration_orchestrator.create_session(
        title=request.title,
        agent_ids=request.agent_ids,
        tasks=request.tasks,
        mode=mode,
    )

    async def run_collaboration():
        await collaboration_orchestrator.execute_session(session)

    asyncio.create_task(run_collaboration())

    logger.info(f"Created MCP collaboration session {session.session_id} for: {request.title}")

    return MCPCollaborationCreateResponse(
        session_id=session.session_id,
        status=session.status.value,
        message="Collaboration session created successfully",
    )


@app.get(
    "/api/v1/mcp/collaboration/{session_id}",
    response_model=MCPCollaborationStatusResponse,
    tags=["MCP"],
    dependencies=[Depends(get_api_key)] if get_api_key else [],
)
async def get_mcp_collaboration_status(
    session_id: str,
) -> MCPCollaborationStatusResponse:
    """获取协作会话状态."""
    session = collaboration_orchestrator.get_session(session_id)

    # 转换任务
    tasks = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status.value,
            "priority": t.priority.value,
            "progress": t.progress,
            "assigned_agent_id": t.assigned_agent_id,
            "estimated_time": t.estimated_time,
            "result": t.result,
            "quality_score": t.quality_score,
        }
        for t in session.tasks
    ]

    # 转换消息
    messages = [
        {
            "id": m.id,
            "from_agent_id": m.from_agent_id,
            "from_agent_name": m.from_agent_name,
            "to_agent_id": m.to_agent_id,
            "to_agent_name": m.to_agent_name,
            "type": m.message_type.value,
            "content": m.content,
            "timestamp": m.timestamp.isoformat(),
        }
        for m in message_bus.get_messages(session_id)
    ]

    # 转换结果
    result = None
    if session.result:
        result = {
            "id": session.result.id,
            "session_id": session.result.session_id,
            "summary": session.result.summary,
            "agent_results": [
                {
                    "agent_id": ar.agent_id,
                    "agent_name": ar.agent_name,
                    "output": ar.output,
                    "score": ar.score,
                    "feedback": ar.feedback,
                    "timestamp": ar.timestamp.isoformat(),
                }
                for ar in session.result.agent_results
            ],
            "overall_score": session.result.overall_score,
            "export_formats": session.result.export_formats,
        }

    error = None
    if session.status == CollaborationStatus.FAILED:
        error = "协作执行失败"

    return MCPCollaborationStatusResponse(
        session_id=session.session_id,
        title=session.title,
        status=session.status.value,
        created_at=session.created_at,
        started_at=session.started_at,
        completed_at=session.completed_at,
        progress=_calculate_progress(session),
        agent_ids=session.agent_ids,
        tasks=tasks,
        messages=messages,
        result=result,
        error=error,
    )


@app.get(
    "/api/v1/mcp/collaboration/{session_id}/stream",
    tags=["MCP"],
    dependencies=[Depends(get_api_key)] if get_api_key else [],
)
async def stream_mcp_collaboration_progress(
    session_id: str,
) -> EventSourceResponse:
    """流式获取协作进度（SSE）."""
    session = collaboration_orchestrator.get_session(session_id)

    queue: asyncio.Queue[ProgressEvent] = asyncio.Queue(maxsize=100)

    def callback(event: ProgressEvent):
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            pass

    subscription_id = message_bus.subscribe_progress(callback, session_id)

    async def event_generator() -> AsyncGenerator[dict[str, Any], None]:
        try:
            while True:
                event = await queue.get()
                if event is None:
                    break
                yield {
                    "event": "progress",
                    "data": json.dumps({
                        "session_id": event.session_id,
                        "status": event.status.value if event.status else None,
                        "progress": event.progress,
                        "current_step": event.current_step,
                        "message": event.message,
                        "timestamp": event.timestamp.isoformat(),
                        "new_message": {
                            "id": event.new_message.id,
                            "from_agent_id": event.new_message.from_agent_id,
                            "from_agent_name": event.new_message.from_agent_name,
                            "to_agent_id": event.new_message.to_agent_id,
                            "to_agent_name": event.new_message.to_agent_name,
                            "type": event.new_message.message_type.value,
                            "content": event.new_message.content,
                            "timestamp": event.new_message.timestamp.isoformat(),
                        } if event.new_message else None,
                        "task_update": {
                            "id": event.task_update.id,
                            "title": event.task_update.title,
                            "status": event.task_update.status.value,
                            "progress": event.task_update.progress,
                        } if event.task_update else None,
                    }, default=str),
                    "id": event.timestamp.isoformat(),
                }

                if (event.status == CollaborationStatus.COMPLETED or
                    event.status == CollaborationStatus.FAILED or
                    event.status == CollaborationStatus.CANCELLED):
                    break
        finally:
            message_bus.unsubscribe_progress(callback, session_id)

    return EventSourceResponse(event_generator())


@app.post(
    "/api/v1/mcp/collaboration/{session_id}/message",
    response_model=MCPSendMessageResponse,
    tags=["MCP"],
    dependencies=[Depends(get_api_key)] if get_api_key else [],
)
async def mcp_send_message(
    session_id: str,
    request: MCPSendMessageRequest,
) -> MCPSendMessageResponse:
    """发送用户消息到协作会话."""
    session = collaboration_orchestrator.get_session(session_id)

    try:
        msg_type = MessageType(request.message_type)
    except ValueError:
        msg_type = MessageType.REQUEST

    message = Message.create(
        from_agent_id=request.from_agent_id,
        from_agent_name=request.from_agent_name,
        to_agent_id=request.to_agent_id,
        to_agent_name=request.to_agent_name,
        content=request.content,
        session_id=session_id,
        message_type=msg_type,
    )

    message_bus.publish_message(message)

    return MCPSendMessageResponse(
        message_id=message.id,
        status="sent",
    )


@app.delete(
    "/api/v1/mcp/collaboration/{session_id}",
    tags=["MCP"],
    dependencies=[Depends(get_api_key)] if get_api_key else [],
)
async def cancel_mcp_collaboration(
    session_id: str,
) -> dict[str, Any]:
    """取消协作会话."""
    success = collaboration_orchestrator.cancel_session(session_id)
    if not success:
        from fastapi import HTTPException, status
        session = collaboration_orchestrator.get_session(session_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Collaboration cannot be cancelled, current status: {session.status.value}",
        )

    return {
        "session_id": session_id,
        "status": "cancelled",
        "message": "Collaboration cancelled successfully",
    }


def _calculate_progress(session: CollaborationSession) -> float:
    """计算整体进度"""
    if not session.tasks:
        if session.status == CollaborationStatus.COMPLETED:
            return 1.0
        elif session.status == CollaborationStatus.RUNNING:
            return 0.5
        else:
            return 0.0

    total_progress = sum(t.progress for t in session.tasks)
    return total_progress / (len(session.tasks) * 100)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
