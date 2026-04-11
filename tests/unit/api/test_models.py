#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pydantic 模型验证单元测试
"""
from __future__ import annotations

from datetime import datetime
import pytest
from pydantic import ValidationError

from deepresearch.api.models import (
    TaskStatus,
    CreateResearchRequest,
    CreateResearchResponse,
    ProgressStep,
    ResearchStatusResponse,
    ProgressEvent,
    ErrorResponse,
    VersionInfo,
    HealthResponse,
)


def test_create_research_request_valid():
    """测试有效的创建研究请求"""
    request = CreateResearchRequest(topic="人工智能发展趋势")
    assert request.topic == "人工智能发展趋势"
    assert request.domain is None
    assert request.details is None

    request_full = CreateResearchRequest(
        topic="人工智能发展趋势",
        domain="technology",
        details="重点关注大模型"
    )
    assert request_full.topic == "人工智能发展趋势"
    assert request_full.domain == "technology"
    assert request_full.details == "重点关注大模型"


def test_create_research_request_empty_topic():
    """测试空主题应该验证失败"""
    with pytest.raises(ValidationError):
        CreateResearchRequest(topic="")


def test_create_research_request_whitespace_topic():
    """测试仅包含空白字符的主题应该验证失败"""
    with pytest.raises(ValidationError):
        CreateResearchRequest(topic="   ")


def test_create_research_response_valid():
    """测试有效的创建研究响应"""
    response = CreateResearchResponse(
        task_id="test-task-id",
        status=TaskStatus.PENDING
    )
    assert response.task_id == "test-task-id"
    assert response.status == TaskStatus.PENDING
    assert response.message == "Research task created successfully"


def test_progress_step_valid():
    """测试有效的进度步骤"""
    step = ProgressStep(
        name="search",
        description="Searching for relevant information",
        status=TaskStatus.RUNNING
    )
    assert step.name == "search"
    assert step.description == "Searching for relevant information"
    assert step.status == TaskStatus.RUNNING


def test_research_status_response_valid():
    """测试有效的研究状态响应"""
    created_at = datetime.utcnow()
    response = ResearchStatusResponse(
        task_id="test-task-id",
        status=TaskStatus.RUNNING,
        topic="人工智能发展趋势",
        created_at=created_at,
        progress=0.5,
        current_step="searching"
    )
    assert response.task_id == "test-task-id"
    assert response.status == TaskStatus.RUNNING
    assert response.topic == "人工智能发展趋势"
    assert response.created_at == created_at
    assert response.progress == 0.5
    assert response.current_step == "searching"
    assert response.steps == []
    assert response.result is None
    assert response.error is None


def test_research_status_response_invalid_progress():
    """测试进度超出范围应该验证失败"""
    created_at = datetime.utcnow()
    with pytest.raises(ValidationError):
        ResearchStatusResponse(
            task_id="test-task-id",
            status=TaskStatus.RUNNING,
            topic="人工智能",
            created_at=created_at,
            progress=1.5
        )

    with pytest.raises(ValidationError):
        ResearchStatusResponse(
            task_id="test-task-id",
            status=TaskStatus.RUNNING,
            topic="人工智能",
            created_at=created_at,
            progress=-0.1
        )


def test_progress_event_defaults():
    """测试进度事件默认值"""
    event = ProgressEvent(
        event="progress",
        task_id="test-task-id",
        status=TaskStatus.RUNNING,
        progress=0.5
    )
    assert event.event == "progress"
    assert event.task_id == "test-task-id"
    assert event.status == TaskStatus.RUNNING
    assert event.progress == 0.5
    assert event.current_step is None
    assert event.message is None
    assert event.data is None
    assert isinstance(event.timestamp, datetime)


def test_error_response_valid():
    """测试有效的错误响应"""
    error = ErrorResponse(
        detail="Not found",
        status_code=404
    )
    assert error.detail == "Not found"
    assert error.status_code == 404
    assert isinstance(error.timestamp, datetime)


def test_version_info_valid():
    """测试有效的版本信息"""
    version = VersionInfo(
        version="1.0.0",
        deepresearch_version="1.1.1"
    )
    assert version.version == "1.0.0"
    assert version.deepresearch_version == "1.1.1"
    assert version.name == "DeepResearch API"
    assert version.description == "Deep Research API Service"


def test_health_response_valid():
    """测试有效的健康检查响应"""
    health = HealthResponse(
        status="ok",
        uptime_seconds=123.45
    )
    assert health.status == "ok"
    assert health.uptime_seconds == 123.45
    assert isinstance(health.timestamp, datetime)


def test_task_status_enum():
    """测试任务状态枚举值"""
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.RUNNING == "running"
    assert TaskStatus.COMPLETED == "completed"
    assert TaskStatus.FAILED == "failed"
    assert TaskStatus.CANCELLED == "cancelled"


def test_research_status_response_with_steps():
    """测试包含步骤的研究状态响应"""
    created_at = datetime.utcnow()
    steps = [
        ProgressStep(name="prep", description="Preparation", status=TaskStatus.COMPLETED),
        ProgressStep(name="search", description="Searching", status=TaskStatus.RUNNING),
    ]
    response = ResearchStatusResponse(
        task_id="test-task-id",
        status=TaskStatus.RUNNING,
        topic="人工智能",
        created_at=created_at,
        progress=0.5,
        steps=steps
    )
    assert len(response.steps) == 2
    assert response.steps[0].name == "prep"
    assert response.steps[1].status == TaskStatus.RUNNING


def test_progress_event_with_data():
    """测试带数据的进度事件"""
    data = {"tokens": 1000, "sources": 5}
    event = ProgressEvent(
        event="progress",
        task_id="test-task-id",
        status=TaskStatus.RUNNING,
        progress=0.5,
        current_step="search",
        message="Found 5 sources",
        data=data
    )
    assert event.data == data
    assert event.message == "Found 5 sources"
    assert event.current_step == "search"
