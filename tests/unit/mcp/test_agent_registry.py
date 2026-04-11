# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

import pytest

from deepresearch.mcp.agent_registry import AgentRegistry
from deepresearch.mcp.exceptions import AgentAlreadyRegisteredError, AgentNotFoundError
from deepresearch.mcp.types import AgentConfig, AgentCollaborationMode, OutputDetail, ResponseStyle


class TestAgentRegistry:
    """测试智能体注册表"""

    def test_register_agent(self):
        """测试注册智能体"""
        registry = AgentRegistry()
        agent = AgentConfig(
            id="test-agent",
            name="Test Agent",
            avatar="🤖",
            role="Tester",
            specialty=["testing"],
            description="Test agent",
            skills=["testing"],
            level=50,
            response_style=ResponseStyle.FORMAL,
            output_detail=OutputDetail.NORMAL,
            tools=[],
            collaboration_mode=AgentCollaborationMode.COLLABORATOR,
        )
        registry.register(agent)
        assert registry.has_agent("test-agent")
        assert registry.count() == 1

    def test_register_duplicate_agent(self):
        """测试重复注册抛出异常"""
        registry = AgentRegistry()
        agent = AgentConfig(
            id="test-agent",
            name="Test Agent",
            avatar="🤖",
            role="Tester",
            specialty=["testing"],
            description="Test agent",
            skills=["testing"],
            level=50,
            response_style=ResponseStyle.FORMAL,
            output_detail=OutputDetail.NORMAL,
            tools=[],
            collaboration_mode=AgentCollaborationMode.COLLABORATOR,
        )
        registry.register(agent)
        with pytest.raises(AgentAlreadyRegisteredError):
            registry.register(agent)

    def test_get_agent(self):
        """测试获取智能体"""
        registry = AgentRegistry()
        agent = AgentConfig(
            id="test-agent",
            name="Test Agent",
            avatar="🤖",
            role="Tester",
            specialty=["testing"],
            description="Test agent",
            skills=["testing"],
            level=50,
            response_style=ResponseStyle.FORMAL,
            output_detail=OutputDetail.NORMAL,
            tools=[],
            collaboration_mode=AgentCollaborationMode.COLLABORATOR,
        )
        registry.register(agent)
        retrieved = registry.get("test-agent")
        assert retrieved.id == "test-agent"
        assert retrieved.name == "Test Agent"

    def test_get_nonexistent_agent(self):
        """测试获取不存在的智能体抛出异常"""
        registry = AgentRegistry()
        with pytest.raises(AgentNotFoundError):
            registry.get("nonexistent")

    def test_unregister_agent(self):
        """测试注销智能体"""
        registry = AgentRegistry()
        agent = AgentConfig(
            id="test-agent",
            name="Test Agent",
            avatar="🤖",
            role="Tester",
            specialty=["testing"],
            description="Test agent",
            skills=["testing"],
            level=50,
            response_style=ResponseStyle.FORMAL,
            output_detail=OutputDetail.NORMAL,
            tools=[],
            collaboration_mode=AgentCollaborationMode.COLLABORATOR,
        )
        registry.register(agent)
        assert registry.unregister("test-agent") is True
        assert registry.count() == 0
        assert not registry.has_agent("test-agent")

    def test_list_agents(self):
        """测试列出智能体"""
        registry = AgentRegistry()
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
            collaboration_mode=AgentCollaborationMode.COLLABORATOR,
            enabled=True,
        )
        agent2 = AgentConfig(
            id="agent-2",
            name="Agent 2",
            avatar="🤖",
            role="Tester",
            specialty=["testing"],
            description="Test agent 2",
            skills=["testing"],
            level=50,
            response_style=ResponseStyle.FORMAL,
            output_detail=OutputDetail.NORMAL,
            tools=[],
            collaboration_mode=AgentCollaborationMode.COLLABORATOR,
            enabled=False,
        )
        registry.register(agent1)
        registry.register(agent2)

        all_agents = registry.list_agents(only_enabled=False)
        assert len(all_agents) == 2

        enabled_only = registry.list_agents(only_enabled=True)
        assert len(enabled_only) == 1
        assert enabled_only[0].id == "agent-1"

    def test_count(self):
        """测试计数"""
        registry = AgentRegistry()
        assert registry.count() == 0
        agent = AgentConfig(
            id="test-agent",
            name="Test Agent",
            avatar="🤖",
            role="Tester",
            specialty=["testing"],
            description="Test agent",
            skills=["testing"],
            level=50,
            response_style=ResponseStyle.FORMAL,
            output_detail=OutputDetail.NORMAL,
            tools=[],
            collaboration_mode=AgentCollaborationMode.COLLABORATOR,
        )
        registry.register(agent)
        assert registry.count() == 1
