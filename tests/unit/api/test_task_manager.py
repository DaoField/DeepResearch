#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
任务管理器功能单元测试
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import pytest

from deepresearch.api.models import TaskStatus, ProgressEvent
from deepresearch.api.task_manager import ResearchTask, TaskManager, task_manager


def test_research_task_init():
    """测试研究任务初始化"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain="technology",
        details="测试",
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow()
    )
    assert task.task_id == "test-id"
    assert task.topic == "人工智能"
    assert task.domain == "technology"
    assert task.details == "测试"
    assert task.status == TaskStatus.PENDING
    assert task.progress == 0.0
    assert task._queue is not None
    assert not task.is_cancelled()


def test_research_task_add_step():
    """测试添加步骤"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow()
    )
    task.add_step("prep", "准备阶段", TaskStatus.COMPLETED)
    task.add_step("search", "搜索阶段", TaskStatus.PENDING)

    assert len(task.steps) == 2
    assert task.steps[0].name == "prep"
    assert task.steps[1].status == TaskStatus.PENDING


def test_research_task_update_progress():
    """测试更新进度"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.RUNNING,
        created_at=datetime.utcnow()
    )
    task.update_progress(0.5, "search", "搜索中", {"found": 10})
    assert task.progress == 0.5
    assert task.current_step == "search"


def test_research_task_update_progress_clamps_range():
    """测试进度会被限制在 0-1 范围内"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.RUNNING,
        created_at=datetime.utcnow()
    )
    task.update_progress(-0.5)
    assert task.progress == 0.0

    task.update_progress(1.5)
    assert task.progress == 1.0


def test_research_task_start():
    """测试任务开始"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow()
    )
    task.start()
    assert task.status == TaskStatus.RUNNING
    assert task.started_at is not None
    assert task.progress == 0.0


def test_research_task_complete():
    """测试任务完成"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.RUNNING,
        created_at=datetime.utcnow()
    )
    result = {"report": "# 测试报告\n\n内容..."}
    task.complete(result)
    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None
    assert task.result == result
    assert task.progress == 1.0


def test_research_task_fail():
    """测试任务失败"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.RUNNING,
        created_at=datetime.utcnow()
    )
    error_msg = "网络错误"
    task.fail(error_msg)
    assert task.status == TaskStatus.FAILED
    assert task.completed_at is not None
    assert task.error == error_msg


def test_research_task_cancel_pending():
    """测试取消等待中的任务"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow()
    )
    result = task.cancel()
    assert result is True
    assert task.status == TaskStatus.CANCELLED
    assert task.is_cancelled()
    assert task.completed_at is not None


def test_research_task_cancel_running():
    """测试取消运行中的任务"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.RUNNING,
        created_at=datetime.utcnow()
    )
    result = task.cancel()
    assert result is True
    assert task.status == TaskStatus.CANCELLED
    assert task.is_cancelled()


def test_research_task_cancel_already_completed():
    """测试取消已完成的任务返回 False"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.COMPLETED,
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    result = task.cancel()
    assert result is False
    assert task.status == TaskStatus.COMPLETED
    assert not task.is_cancelled()


def test_task_manager_create_task():
    """测试创建任务"""
    manager = TaskManager()
    task = manager.create_task("人工智能", "technology", "测试详情")

    assert task.task_id is not None
    assert len(task.task_id) > 0
    assert task.topic == "人工智能"
    assert task.domain == "technology"
    assert task.details == "测试详情"
    assert task.status == TaskStatus.PENDING
    assert isinstance(task.created_at, datetime)
    assert manager.get_task(task.task_id) is task


def test_task_manager_get_task():
    """测试获取任务"""
    manager = TaskManager()
    task = manager.create_task("测试主题")
    retrieved = manager.get_task(task.task_id)
    assert retrieved is task
    assert retrieved.task_id == task.task_id


def test_task_manager_get_nonexistent_task():
    """测试获取不存在的任务返回 None"""
    manager = TaskManager()
    assert manager.get_task("nonexistent-id") is None


def test_task_manager_list_tasks():
    """测试列出所有任务"""
    manager = TaskManager()
    assert len(manager.list_tasks()) == 0

    manager.create_task("任务1")
    manager.create_task("任务2")
    manager.create_task("任务3")

    assert len(manager.list_tasks()) == 3


def test_task_manager_cancel_task():
    """测试取消任务"""
    manager = TaskManager()
    task = manager.create_task("测试主题")
    result = manager.cancel_task(task.task_id)
    assert result is True
    assert task.status == TaskStatus.CANCELLED


def test_task_manager_cancel_nonexistent_task():
    """测试取消不存在的任务返回 False"""
    manager = TaskManager()
    result = manager.cancel_task("nonexistent-id")
    assert result is False


def test_task_manager_counts():
    """测试任务计数"""
    manager = TaskManager(max_concurrent_tasks=5)

    assert manager.total_tasks_count == 0
    assert manager.active_tasks_count == 0

    task1 = manager.create_task("任务1")
    task2 = manager.create_task("任务2")
    task3 = manager.create_task("任务3")

    assert manager.total_tasks_count == 3
    assert manager.active_tasks_count == 3

    task1.complete({})
    assert manager.active_tasks_count == 2

    task2.cancel()
    assert manager.active_tasks_count == 1


def test_task_manager_clean_old_tasks():
    """测试清理旧任务"""
    manager = TaskManager()
    now = datetime.utcnow()

    task1 = manager.create_task("新任务")
    task1.start()
    task1.complete({})
    task1.completed_at = now - timedelta(seconds=100)

    task2 = manager.create_task("旧任务")
    task2.start()
    task2.complete({})
    task2.completed_at = now - timedelta(seconds=2000)

    task3 = manager.create_task("运行中任务")
    task3.start()

    cleaned = manager.clean_old_tasks(max_age_seconds=3600)
    assert cleaned == 1
    assert manager.get_task(task1.task_id) is not None
    assert manager.get_task(task2.task_id) is None
    assert manager.get_task(task3.task_id) is not None


def test_task_manager_clean_no_old_tasks():
    """测试没有旧任务时清理返回 0"""
    manager = TaskManager()
    task = manager.create_task("测试")
    task.start()
    task.complete({})

    cleaned = manager.clean_old_tasks(max_age_seconds=10)
    assert cleaned == 0


def test_task_manager_uptime():
    """测试获取运行时间"""
    manager = TaskManager()
    uptime = manager.get_uptime_seconds()
    assert uptime >= 0
    assert isinstance(uptime, float)


def test_singleton_instance():
    """测试全局单例实例存在"""
    assert task_manager is not None
    assert isinstance(task_manager, TaskManager)


@pytest.mark.asyncio
async def test_task_manager_run_task():
    """测试运行任务"""
    manager = TaskManager()
    task = manager.create_task("测试主题")

    async def executor(t):
        return {"result": f"done: {t.topic}"}

    await manager.run_task(task, executor)
    assert task.status == TaskStatus.COMPLETED
    assert task.result == {"result": "done: 测试主题"}


@pytest.mark.asyncio
async def test_task_manager_run_task_executor_raises_error():
    """测试运行任务时执行器抛出异常会标记任务失败"""
    manager = TaskManager()
    task = manager.create_task("测试主题")

    def bad_executor(t):
        raise ValueError("Something went wrong")

    await manager.run_task(task, bad_executor)
    assert task.status == TaskStatus.FAILED
    assert "Something went wrong" in task.error


@pytest.mark.asyncio
async def test_task_manager_run_task_already_cancelled():
    """测试运行已取消的任务直接返回"""
    manager = TaskManager()
    task = manager.create_task("测试主题")
    task.cancel()

    executed = False

    async def executor(t):
        nonlocal executed
        executed = True
        return {}

    await manager.run_task(task, executor)
    assert not executed
    assert task.status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_task_manager_concurrency_limit():
    """测试并发限制功能"""
    max_concurrent = 2
    manager = TaskManager(max_concurrent_tasks=max_concurrent)
    running_count = 0
    max_running_reached = 0

    async def slow_task(task):
        nonlocal running_count, max_running_reached
        running_count += 1
        max_running_reached = max(max_running_reached, running_count)
        await asyncio.sleep(0.1)
        running_count -= 1
        return {}

    tasks = [manager.create_task(f"任务{i}") for i in range(5)]

    coroutines = [manager.run_task(t, slow_task) for t in tasks]
    await asyncio.gather(*coroutines)

    assert max_running_reached <= max_concurrent
    for task in tasks:
        assert task.status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_progress_stream_yields_initial_event():
    """测试进度流生成初始事件"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow()
    )

    events = []
    async for event in task.progress_stream():
        events.append(event)
        break

    assert len(events) == 1
    assert events[0].event == "initial"
    assert events[0].task_id == "test-id"


@pytest.mark.asyncio
async def test_progress_stream_yields_progress_events():
    """测试进度流能接收进度事件"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.RUNNING,
        created_at=datetime.utcnow()
    )

    async def producer():
        await asyncio.sleep(0.05)
        task.update_progress(0.3, "step1", "halfway")
        await asyncio.sleep(0.05)
        task.complete({"done": True})

    events = []
    producer_task = asyncio.create_task(producer())

    async for event in task.progress_stream():
        events.append(event)
        if event.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            break

    await producer_task

    assert len(events) >= 2
    assert events[0].event == "initial"
    assert any(e.event == "progress" and e.progress == 0.3 for e in events)
    assert any(e.event == "complete" for e in events)
    assert events[-1].status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_progress_stream_yields_final_event_on_error():
    """测试任务失败时进度流输出最终错误事件"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.RUNNING,
        created_at=datetime.utcnow()
    )

    async def producer():
        await asyncio.sleep(0.05)
        task.fail("测试错误")

    events = []
    producer_task = asyncio.create_task(producer())

    async for event in task.progress_stream():
        events.append(event)
        if event.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            break

    await producer_task

    assert events[-1].event == "error"
    assert events[-1].status == TaskStatus.FAILED
    assert events[-1].message == "测试错误"


@pytest.mark.asyncio
async def test_progress_stream_yields_final_event_on_cancel():
    """测试任务取消时进度流输出最终取消事件"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.RUNNING,
        created_at=datetime.utcnow()
    )

    async def producer():
        await asyncio.sleep(0.05)
        task.cancel()

    events = []
    producer_task = asyncio.create_task(producer())

    async for event in task.progress_stream():
        events.append(event)
        if event.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            break

    await producer_task

    assert events[-1].event == "cancelled"
    assert events[-1].status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_progress_stream_sends_ping_keepalive():
    """测试空闲时发送 ping 保活"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.RUNNING,
        created_at=datetime.utcnow()
    )

    got_ping = False

    try:
        async for event in task.progress_stream():
            if event.event == "ping":
                got_ping = True
                task.complete({})
                break

    except asyncio.TimeoutError:
        pass

    assert got_ping


def test_task_init_creates_queue():
    """测试任务初始化自动创建队列"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow(),
        _queue=None
    )
    assert task._queue is not None
    assert isinstance(task._queue, asyncio.Queue)


def test_update_progress_ignores_full_queue():
    """测试队列满时不会抛出异常"""
    task = ResearchTask(
        task_id="test-id",
        topic="人工智能",
        domain=None,
        details=None,
        status=TaskStatus.RUNNING,
        created_at=datetime.utcnow()
    )

    for i in range(200):
        task.update_progress(i / 200)

    assert task.progress == 1.0
