# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

import logging
from typing import Optional

import toml

from deepresearch.config.base import config_manager

from .exceptions import AgentAlreadyRegisteredError, AgentNotFoundError, InvalidConfigurationError
from .types import AgentConfig, AgentCollaborationMode, OutputDetail, ResponseStyle

logger = logging.getLogger(__name__)


class AgentRegistry:
    """智能体注册表

    管理所有可用的协作智能体，支持从配置文件加载和动态注册。
    """

    def __init__(self):
        self._agents: dict[str, AgentConfig] = {}

    def register(self, agent: AgentConfig) -> None:
        """注册一个新智能体

        Args:
            agent: 智能体配置

        Raises:
            AgentAlreadyRegisteredError: 如果智能体ID已存在
        """
        if agent.id in self._agents:
            raise AgentAlreadyRegisteredError(agent.id)
        self._agents[agent.id] = agent
        logger.debug(f"Registered agent: {agent.id} ({agent.name})")

    def unregister(self, agent_id: str) -> bool:
        """注销一个智能体

        Args:
            agent_id: 智能体ID

        Returns:
            是否成功注销
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            logger.debug(f"Unregistered agent: {agent_id}")
            return True
        return False

    def get(self, agent_id: str) -> AgentConfig:
        """获取智能体配置

        Args:
            agent_id: 智能体ID

        Returns:
            智能体配置

        Raises:
            AgentNotFoundError: 如果智能体不存在
        """
        if agent_id not in self._agents:
            raise AgentNotFoundError(agent_id)
        return self._agents[agent_id]

    def list_agents(self, only_enabled: bool = True) -> list[AgentConfig]:
        """列出所有已注册智能体

        Args:
            only_enabled: 是否只返回已启用的智能体

        Returns:
            智能体配置列表
        """
        if only_enabled:
            return [a for a in self._agents.values() if a.enabled]
        return list(self._agents.values())

    def has_agent(self, agent_id: str) -> bool:
        """检查智能体是否存在

        Args:
            agent_id: 智能体ID

        Returns:
            是否存在
        """
        return agent_id in self._agents

    def count(self) -> int:
        """获取已注册智能体数量

        Returns:
            智能体数量
        """
        return len(self._agents)

    def load_from_config(self, config_path: str) -> None:
        """从配置文件加载智能体配置

        Args:
            config_path: 配置文件路径

        Raises:
            InvalidConfigurationError: 配置无效
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = toml.load(f)
        except FileNotFoundError:
            logger.warning(f"MCP config file not found: {config_path}, skipping")
            return
        except Exception as e:
            raise InvalidConfigurationError(f"Failed to read config: {e}")

        agents_config = config_data.get("agents", {})
        if not isinstance(agents_config, dict):
            raise InvalidConfigurationError("'agents' must be a table in mcp.toml")

        for agent_id, agent_data in agents_config.items():
            if not isinstance(agent_data, dict):
                logger.warning(f"Invalid agent config for {agent_id}, skipping")
                continue

            try:
                agent_config = self._parse_agent_config(agent_id, agent_data)
                self.register(agent_config)
            except Exception as e:
                logger.warning(f"Failed to parse agent {agent_id}: {e}, skipping")

        logger.info(f"Loaded {self.count()} agents from config")

    def _parse_agent_config(self, agent_id: str, data: dict) -> AgentConfig:
        """解析单个智能体配置

        Args:
            agent_id: 智能体ID
            data: 配置字典

        Returns:
            智能体配置
        """
        return AgentConfig(
            id=agent_id,
            name=data.get("name", agent_id),
            avatar=data.get("avatar", "🤖"),
            role=data.get("role", ""),
            specialty=data.get("specialty", []),
            description=data.get("description", ""),
            skills=data.get("skills", []),
            level=data.get("level", 50),
            response_style=self._parse_response_style(data.get("response_style", "formal")),
            output_detail=self._parse_output_detail(data.get("output_detail", "normal")),
            tools=data.get("tools", []),
            collaboration_mode=self._parse_collaboration_mode(data.get("collaboration_mode", "collaborator")),
            llm_config_id=data.get("llm_config_id", "default"),
            system_prompt=data.get("system_prompt"),
            enabled=data.get("enabled", True),
        )

    def _parse_response_style(self, value: str) -> ResponseStyle:
        """解析响应风格"""
        try:
            return ResponseStyle(value.lower())
        except ValueError:
            return ResponseStyle.FORMAL

    def _parse_output_detail(self, value: str) -> OutputDetail:
        """解析输出详细程度"""
        try:
            return OutputDetail(value.lower())
        except ValueError:
            return OutputDetail.NORMAL

    def _parse_collaboration_mode(self, value: str) -> AgentCollaborationMode:
        """解析协作模式"""
        try:
            return AgentCollaborationMode(value.lower())
        except ValueError:
            return AgentCollaborationMode.COLLABORATOR


# 全局单例
agent_registry = AgentRegistry()

# 从配置文件加载
try:
    from pathlib import Path
    import os
    # Get project root directory
    project_root = Path(__file__).parent.parent.parent.parent
    config_path = project_root / "config" / "mcp.toml"
    if config_path.exists():
        agent_registry.load_from_config(str(config_path))
except Exception as e:
    logger.warning(f"Failed to load MCP config: {e}")
