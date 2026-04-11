# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from __future__ import annotations

import asyncio
import uuid
from asyncio import Task
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Optional

from deepresearch.api.models import ProgressEvent, ProgressStep, TaskStatus
from deepresearch.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ResearchTask:
    """研究任务数据类。"""

    task_id: str
    topic: str
    domain: str | None
    details: str | None
    status: TaskStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    progress: float = 0.0
    current_step: str | None = None
    steps: list[ProgressStep] = field(default_factory=list)
    result: dict[str, Any] | None = None
    error: str | None = None
    _async_task: Task | None = None
    _queue: asyncio.Queue[ProgressEvent] | None = None
    _cancel_event: asyncio.Event = field(default_factory=asyncio.Event)

    def __post_init__(self):
        if self._queue is None:
            self._queue = asyncio.Queue(maxsize=100)

    def add_step(self, name: str, description: str, status: TaskStatus) -> None:
        """添加一个步骤。"""
        self.steps.append(
            ProgressStep(name=name, description=description, status=status)
        )

    def update_progress(
        self,
        progress: float,
        current_step: str | None = None,
        message: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        """更新进度。"""
        self.progress = min(max(progress, 0.0), 1.0)
        if current_step:
            self.current_step = current_step

        event = ProgressEvent(
            event="progress",
            task_id=self.task_id,
            status=self.status,
            progress=self.progress,
            current_step=self.current_step,
            message=message,
            data=data,
        )

        if self._queue and not self._queue.full():
            try:
                self._queue.put_nowait(event)
            except asyncio.QueueFull:
                pass

    async def progress_stream(self) -> AsyncGenerator[ProgressEvent, None]:
        """生成进度事件流。"""
        if self._queue is None:
            self._queue = asyncio.Queue(maxsize=100)

        initial_event = ProgressEvent(
            event="initial",
            task_id=self.task_id,
            status=self.status,
            progress=self.progress,
            current_step=self.current_step,
            message=f"Task {self.status}",
        )
        yield initial_event

        while True:
            try:
                if self.status in (
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.CANCELLED,
                ):
                    final_event = ProgressEvent(
                        event="complete"
                        if self.status == TaskStatus.COMPLETED
                        else "error"
                        if self.status == TaskStatus.FAILED
                        else "cancelled",
                        task_id=self.task_id,
                        status=self.status,
                        progress=self.progress,
                        current_step=self.current_step,
                        message=self.error
                        if self.status == TaskStatus.FAILED
                        else f"Task {self.status}",
                        data=self.result
                        if self.status == TaskStatus.COMPLETED
                        else None,
                    )
                    yield final_event
                    break

                event = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=30.0,
                )
                yield event
                self._queue.task_done()
            except asyncio.TimeoutError:
                if self.status not in (
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.CANCELLED,
                ):
                    yield ProgressEvent(
                        event="ping",
                        task_id=self.task_id,
                        status=self.status,
                        progress=self.progress,
                        current_step=self.current_step,
                        message="keepalive",
                    )
                    continue
                break

    def cancel(self) -> bool:
        """取消任务。"""
        if self.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
            self._cancel_event.set()
            self.status = TaskStatus.CANCELLED
            self.completed_at = datetime.utcnow()
            self.update_progress(1.0, message="Task cancelled by user")
            logger.info(f"Task {self.task_id} cancelled")
            return True
        return False

    def is_cancelled(self) -> bool:
        """检查是否已取消。"""
        return self._cancel_event.is_set()

    def start(self) -> None:
        """标记任务开始。"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.update_progress(0.0, message="Task started")

    def complete(self, result: dict[str, Any]) -> None:
        """标记任务完成。"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.result = result
        self.progress = 1.0
        self.update_progress(1.0, message="Task completed successfully")
        logger.info(f"Task {self.task_id} completed successfully")

    def fail(self, error: str) -> None:
        """标记任务失败。"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = error
        self.update_progress(self.progress, message=f"Task failed: {error}")
        logger.error(f"Task {self.task_id} failed: {error}")


class TaskManager:
    """异步任务管理器。"""

    def __init__(self, max_concurrent_tasks: int = 10):
        self._tasks: dict[str, ResearchTask] = {}
        self._max_concurrent_tasks = max_concurrent_tasks
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._start_time = datetime.utcnow()
        logger.info(
            f"TaskManager initialized with max {max_concurrent_tasks} concurrent tasks"
        )

    def create_task(
        self,
        topic: str,
        domain: str | None = None,
        details: str | None = None,
    ) -> ResearchTask:
        """创建新任务。"""
        task_id = str(uuid.uuid4())
        task = ResearchTask(
            task_id=task_id,
            topic=topic,
            domain=domain,
            details=details,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        self._tasks[task_id] = task
        logger.debug(f"Created task {task_id} for topic: {topic}")
        return task

    def get_task(self, task_id: str) -> ResearchTask | None:
        """获取任务。"""
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[ResearchTask]:
        """列出所有任务。"""
        return list(self._tasks.values())

    def cancel_task(self, task_id: str) -> bool:
        """取消任务。"""
        task = self.get_task(task_id)
        if task:
            return task.cancel()
        return False

    def clean_old_tasks(self, max_age_seconds: int = 3600) -> int:
        """清理已完成的旧任务。"""
        now = datetime.utcnow()
        to_remove: list[str] = []

        for task_id, task in self._tasks.items():
            if task.status in (
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
            ):
                if task.completed_at:
                    age = (now - task.completed_at).total_seconds()
                    if age > max_age_seconds:
                        to_remove.append(task_id)

        for task_id in to_remove:
            del self._tasks[task_id]

        if to_remove:
            logger.info(f"Cleaned {len(to_remove)} old completed tasks")

        return len(to_remove)

    def get_uptime_seconds(self) -> float:
        """获取服务运行时间。"""
        return (datetime.utcnow() - self._start_time).total_seconds()

    async def run_task(
        self,
        task: ResearchTask,
        executor: Callable[[ResearchTask], Any],
    ) -> None:
        """运行任务。"""
        async with self._semaphore:
            if task.is_cancelled():
                return

            try:
                task.start()
                result = (
                    await executor(task)
                    if asyncio.iscoroutinefunction(executor)
                    else executor(task)
                )
                if not task.is_cancelled():
                    task.complete(result)
            except Exception as e:
                if not task.is_cancelled():
                    task.fail(str(e))
                logger.exception(f"Error executing task {task.task_id}")

    @property
    def active_tasks_count(self) -> int:
        """获取活跃任务数量。"""
        return sum(
            1
            for task in self._tasks.values()
            if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING)
        )

    @property
    def total_tasks_count(self) -> int:
        """获取总任务数量。"""
        return len(self._tasks)


task_manager = TaskManager()
