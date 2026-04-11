# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

import pytest

from deepresearch.mcp.agent_registry import AgentRegistry
from deepresearch.mcp.collaboration_orchestrator import CollaborationOrchestrator
from deepresearch.mcp.exceptions import AgentNotFoundError
from deepresearch.mcp.message_bus import MessageBus
from deepresearch.mcp.result_aggregator import ResultAggregator
from deepresearch.mcp.types import AgentConfig, AgentCollaborationMode, CollaborationMode, OutputDetail, ResponseStyle


class TestCollaborationOrchestrator:
    """测试协作编排器"""

    @pytest.fixture
    def orchestrator(self):
        registry = AgentRegistry()
        bus = MessageBus()
        aggregator = ResultAggregator()

        agent1 = AgentConfig(
            id="agent-1",
            name="Agent 1",
            avatar="🤖",
            role="Tester",
            specialty=["testing"],
            description="Test agent 1",
            skills=["testing"],
            level=50,
            response_style=ResponseStyle.FORMAL,
            output_detail=OutputDetail.NORMAL,
            tools=[],
            collaboration_mode=AgentCollaborationMode.LEADER,
        )
        agent2 = AgentConfig(
            id="agent-2",
            name="Agent 2",
            avatar="🧪",
            role="Tester",
            specialty=["testing"],
            description="Test agent 2",
            skills=["testing"],
            level=50,
            response_style=ResponseStyle.FORMAL,
            output_detail=OutputDetail.NORMAL,
            tools=[],
            collaboration_mode=AgentCollaborationMode.COLLABORATOR,
        )
        registry.register(agent1)
        registry.register(agent2)

        return CollaborationOrchestrator(registry, bus, aggregator)

    def test_create_session(self, orchestrator):
        """测试创建会话"""
        session = orchestrator.create_session(
            title="Test Collaboration",
            agent_ids=["agent-1", "agent-2"],
        )
        assert session.session_id is not None
        assert session.title == "Test Collaboration"
        assert session.agent_ids == ["agent-1", "agent-2"]
        assert session.mode == CollaborationMode.SERIAL
        assert orchestrator.get_session(session.session_id) is session

    def test_create_session_nonexistent_agent(self, orchestrator):
        """测试创建会话包含不存在智能体抛出异常"""
        with pytest.raises(AgentNotFoundError):
            orchestrator.create_session(
                title="Test",
                agent_ids=["agent-1", "nonexistent"],
            )

    def test_list_sessions(self, orchestrator):
        """测试列出会话"""
        session1 = orchestrator.create_session("Session 1", ["agent-1"])
        session2 = orchestrator.create_session("Session 2", ["agent-2"])
        sessions = orchestrator.list_sessions()
        assert len(sessions) == 2
        assert {s.session_id for s in sessions} == {session1.session_id, session2.session_id}

    def test_cancel_session(self, orchestrator):
        """测试取消会话"""
        session = orchestrator.create_session("Test", ["agent-1"])
        success = orchestrator.cancel_session(session.session_id)
        assert success is True
        assert session.status.value == "cancelled"

    def test_build_graph_serial(self, orchestrator):
        """测试构建串行图"""
        session = orchestrator.create_session(
            title="Test Serial",
            agent_ids=["agent-1", "agent-2"],
            mode=CollaborationMode.SERIAL,
        )
        graph = orchestrator.build_graph(session)
        assert graph is not None

    def test_build_graph_parallel(self, orchestrator):
        """测试构建并行图"""
        session = orchestrator.create_session(
            title="Test Parallel",
            agent_ids=["agent-1", "agent-2"],
            mode=CollaborationMode.PARALLEL,
        )
        graph = orchestrator.build_graph(session)
        assert graph is not None

    def test_get_session_not_found(self, orchestrator):
        """测试获取不存在会话抛出异常"""
        with pytest.raises(Exception):
            orchestrator.get_session("nonexistent")
