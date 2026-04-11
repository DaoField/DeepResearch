# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Optional
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from deepresearch.llms.llm import _get_llm_instance
# We don't need get_prompt since we build prompts directly in agent node
# from deepresearch.prompts.template import apply_prompt_template

from .agent_registry import AgentRegistry, agent_registry
from .exceptions import (
    AgentNotFoundError,
    CollaborationAlreadyRunningError,
    CollaborationSessionNotFoundError,
    OrchestrationError,
)
from .message_bus import MessageBus, message_bus
from .result_aggregator import ResultAggregator, result_aggregator
from .types import (
    AgentConfig,
    CollaborationMode,
    CollaborationSession,
    CollaborationStatus,
    Message,
    MessageType,
    ProgressEvent,
    Task,
    TaskPriority,
    TaskStatus,
)

logger = logging.getLogger(__name__)


class CollaborationOrchestrator:
    """协作编排器

    根据用户选择的智能体动态构建协作工作流，执行并管理协作过程。
    支持多种协作模式：串行流水线、并行探索、轮询讨论。
    """

    def __init__(
        self,
        registry: AgentRegistry = agent_registry,
        bus: MessageBus = message_bus,
        aggregator: ResultAggregator = result_aggregator,
    ):
        self._registry = registry
        self._bus = bus
        self._aggregator = aggregator
        self._sessions: dict[str, CollaborationSession] = {}
        self._compiled_graphs: dict[str, CompiledStateGraph] = {}

    def create_session(
        self,
        title: str,
        agent_ids: list[str],
        tasks: Optional[list[dict[str, Any]]] = None,
        mode: CollaborationMode = CollaborationMode.SERIAL,
        created_by: Optional[str] = None,
    ) -> CollaborationSession:
        """创建新的协作会话

        Args:
            title: 会话标题
            agent_ids: 选中的智能体ID列表
            tasks: 可选，预定义任务列表
            mode: 协作模式
            created_by: 创建者

        Returns:
            创建的协作会话

        Raises:
            AgentNotFoundError: 如果某个智能体不存在
        """
        for agent_id in agent_ids:
            if not self._registry.has_agent(agent_id):
                raise AgentNotFoundError(agent_id)

        parsed_tasks = []
        if tasks:
            for i, t in enumerate(tasks):
                task = Task(
                    id=t.get("id", f"task-{i}"),
                    title=t.get("title", f"Task {i+1}"),
                    description=t.get("description", ""),
                    status=TaskStatus(t.get("status", "pending")),
                    priority=TaskPriority(t.get("priority", "medium")),
                    progress=t.get("progress", 0.0),
                    assigned_agent_id=t.get("assigned_agent_id"),
                )
                parsed_tasks.append(task)

        session = CollaborationSession.create(
            title=title,
            agent_ids=agent_ids,
            tasks=parsed_tasks,
            mode=mode,
            created_by=created_by,
        )

        self._sessions[session.session_id] = session

        # 发布系统消息
        welcome = Message.create(
            from_agent_id="system",
            from_agent_name="系统",
            content=f"已创建协作会话: {title}，选中 {len(agent_ids)} 个智能体，协作模式: {mode.value}",
            session_id=session.session_id,
            message_type=MessageType.SYSTEM,
        )
        self._bus.publish_message(welcome)

        logger.info(f"Created collaboration session: {session.session_id} with agents: {agent_ids}")
        return session

    def get_session(self, session_id: str) -> CollaborationSession:
        """获取协作会话

        Args:
            session_id: 会话ID

        Returns:
            协作会话

        Raises:
            CollaborationSessionNotFoundError: 如果会话不存在
        """
        if session_id not in self._sessions:
            raise CollaborationSessionNotFoundError(session_id)
        return self._sessions[session_id]

    def list_sessions(self) -> list[CollaborationSession]:
        """列出所有会话

        Returns:
            会话列表
        """
        return list(self._sessions.values())

    def cancel_session(self, session_id: str) -> bool:
        """取消协作会话

        Args:
            session_id: 会话ID

        Returns:
            是否成功取消

        Raises:
            CollaborationSessionNotFoundError: 如果会话不存在
        """
        session = self.get_session(session_id)
        if session.status == CollaborationStatus.COMPLETED:
            logger.warning(f"Cannot cancel already completed session: {session_id}")
            return False

        session.status = CollaborationStatus.CANCELLED
        session.updated_at = datetime.now()

        # 发布取消事件
        event = ProgressEvent(
            session_id=session_id,
            status=CollaborationStatus.CANCELLED,
            progress=0.0,
            message="协作已取消",
        )
        self._bus.publish_progress(event)

        logger.info(f"Cancelled collaboration session: {session_id}")
        return True

    def build_graph(
        self,
        session: CollaborationSession,
    ) -> CompiledStateGraph:
        """根据会话配置动态构建 LangGraph 工作流

        当前第一阶段实现：串行流水线模式
        每个智能体依次执行，输出传递给下一个智能体

        Args:
            session: 协作会话

        Returns:
            编译好的工作流
        """
        agents = [self._registry.get(aid) for aid in session.agent_ids]

        graph_builder = StateGraph(dict)

        # 为每个智能体添加节点
        for agent in agents:
            node_name = f"agent_{agent.id}"

            def node_func(state: dict[str, Any], agent_config=agent) -> dict[str, Any]:
                return self._agent_node(state, agent_config)

            graph_builder.add_node(node_name, node_func)

        # 连接节点
        if session.mode == CollaborationMode.SERIAL:
            # 串行流水线：START -> agent1 -> agent2 -> ... -> END
            prev_node = START
            for agent in agents:
                node_name = f"agent_{agent.id}"
                graph_builder.add_edge(prev_node, node_name)
                prev_node = node_name
            graph_builder.add_edge(prev_node, END)

        elif session.mode == CollaborationMode.PARALLEL:
            # 并行：START 同时到所有 agent，然后聚合（第一阶段简化实现）
            # 后续版本完善并行执行
            for agent in agents:
                node_name = f"agent_{agent.id}"
                graph_builder.add_edge(START, node_name)
            # 所有节点都到 END（简化处理）
            for agent in agents:
                node_name = f"agent_{agent.id}"
                graph_builder.add_edge(node_name, END)

        else:  # ROUND_ROBIN
            # 轮询讨论模式，第一阶段简化为串行
            prev_node = START
            for agent in agents:
                node_name = f"agent_{agent.id}"
                graph_builder.add_edge(prev_node, node_name)
                prev_node = node_name
            graph_builder.add_edge(prev_node, END)

        compiled = graph_builder.compile()
        self._compiled_graphs[session.session_id] = compiled
        return compiled

    async def execute_session(
        self,
        session: CollaborationSession,
        progress_callback: Optional[Callable[[ProgressEvent], None]] = None,
    ) -> CollaborationSession:
        """执行协作会话

        Args:
            session: 协作会话
            progress_callback: 进度回调

        Returns:
            执行完成后的会话

        Raises:
            CollaborationAlreadyRunningError: 如果会话已在运行
            OrchestrationError: 执行出错
        """
        if session.status == CollaborationStatus.RUNNING:
            raise CollaborationAlreadyRunningError(session.session_id)

        session.status = CollaborationStatus.RUNNING
        session.started_at = datetime.now()
        session.updated_at = datetime.now()

        # 发布开始事件
        self._publish_progress(session, 0.0, "开始协作", progress_callback)

        try:
            graph = self.build_graph(session)
            initial_state = {
                "title": session.title,
                "agent_ids": session.agent_ids,
                "tasks": [t.to_dict() for t in session.tasks],
                "mode": session.mode.value,
            }

            total_agents = len(session.agent_ids)
            current_step = 0

            async def progress_hook(event: ProgressEvent):
                event.session_id = session.session_id
                self._bus.publish_progress(event)
                if progress_callback:
                    progress_callback(event)

            # 执行工作流
            result = await graph.ainvoke(initial_state)

            # 更新任务进度
            for i, agent_id in enumerate(session.agent_ids):
                current_step = i + 1
                progress = current_step / total_agents
                agent_config = self._registry.get(agent_id)

                # 更新任务状态
                for task in session.tasks:
                    if task.assigned_agent_id == agent_id:
                        task.status = TaskStatus.COMPLETED
                        task.progress = 100.0
                        task.end_time = datetime.now()

                progress_hook(ProgressEvent(
                    session_id=session.session_id,
                    status=CollaborationStatus.RUNNING,
                    progress=progress,
                    current_step=f"agent_{agent_id}",
                    message=f"{agent_config.name} 已完成",
                ))

                # 添加系统消息
                msg = Message.create(
                    from_agent_id="system",
                    from_agent_name="系统",
                    content=f"{agent_config.name} 已完成任务",
                    session_id=session.session_id,
                    message_type=MessageType.SYSTEM,
                )
                self._bus.publish_message(msg)

            # 聚合结果
            if "output" in result and isinstance(result["output"], dict):
                for agent_id, output in result["output"].items():
                    if agent := self._registry.get(agent_id):
                        self._aggregator.add_agent_result(
                            session,
                            agent_id,
                            agent.name,
                            str(output),
                            score=0.85,
                        )

            final_result = self._aggregator.get_final_result(session)
            if final_result:
                session.result = final_result

            session.status = CollaborationStatus.COMPLETED
            session.completed_at = datetime.now()
            session.updated_at = datetime.now()

            progress_hook(ProgressEvent(
                session_id=session.session_id,
                status=CollaborationStatus.COMPLETED,
                progress=1.0,
                message="协作完成",
            ))

            logger.info(f"Completed collaboration session: {session.session_id}")
            return session

        except Exception as e:
            session.status = CollaborationStatus.FAILED
            session.updated_at = datetime.now()

            error_msg = str(e)
            progress_hook(ProgressEvent(
                session_id=session.session_id,
                status=CollaborationStatus.FAILED,
                progress=0.0,
                message=f"协作失败: {error_msg}",
            ))

            logger.error(f"Failed to execute collaboration {session.session_id}: {e}")
            raise OrchestrationError(f"Execution failed: {e}") from e

    def _agent_node(
        self,
        state: dict[str, Any],
        agent: AgentConfig,
    ) -> dict[str, Any]:
        """单个智能体节点执行

        Args:
            state: 当前状态
            agent: 智能体配置

        Returns:
            更新后的状态
        """
        from deepresearch.config.llms_config import LLMType
        llm_type = LLMType(agent.llm_config_id)
        llm = _get_llm_instance(llm_type)

        # 构建提示词
        system_prompt = agent.system_prompt or self._get_default_system_prompt(agent)

        user_content = self._build_agent_input(state, agent)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        # 调用 LLM
        response = llm.invoke(messages)
        output = response.content if hasattr(response, "content") else str(response)

        # 保存输出
        if "output" not in state:
            state["output"] = {}
        state["output"][agent.id] = output

        return state

    def _get_default_system_prompt(self, agent: AgentConfig) -> str:
        """获取默认系统提示词"""
        specialties = ", ".join(agent.specialty)
        skills = ", ".join(agent.skills)

        return f"""你是 {agent.name}，角色是 {agent.role}。
你的专长: {specialties}
你的技能: {skills}
请根据你的专长和技能，认真完成分配给你的任务。
给出专业、清晰、结构化的输出。"""

    def _build_agent_input(self, state: dict[str, Any], agent: AgentConfig) -> str:
        """构建智能体输入"""
        title = state.get("title", "")
        previous_outputs = state.get("output", {})

        parts = [f"任务标题: {title}"]

        if previous_outputs:
            parts.append("\n--- 之前智能体的输出 ---")
            for prev_agent_id, output in previous_outputs.items():
                parts.append(f"\n【{prev_agent_id}】:\n{output}\n")

        parts.append(f"\n--- 你的任务 ---")
        parts.append(f"你是 {agent.name} ({agent.role})，请基于上述信息完成你的工作。")

        return "\n".join(parts)

    def _publish_progress(
        self,
        session: CollaborationSession,
        progress: float,
        message: str,
        callback: Optional[Callable[[ProgressEvent], None]],
    ):
        """发布进度"""
        event = ProgressEvent(
            session_id=session.session_id,
            status=session.status,
            progress=progress,
            message=message,
        )
        self._bus.publish_progress(event)
        if callback:
            callback(event)


# 全局单例
collaboration_orchestrator = CollaborationOrchestrator()
