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
    ResearchStatusResponse,
    TaskStatus,
    VersionInfo,
)
from deepresearch.api.task_manager import ResearchTask, task_manager
from deepresearch.logging_config import get_logger

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
