# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License


class MCPError(Exception):
    """MCP 基础异常"""
    pass


class AgentNotFoundError(MCPError):
    """智能体未找到"""
    def __init__(self, agent_id: str):
        super().__init__(f"Agent not found: {agent_id}")
        self.agent_id = agent_id


class AgentAlreadyRegisteredError(MCPError):
    """智能体已注册"""
    def __init__(self, agent_id: str):
        super().__init__(f"Agent already registered: {agent_id}")
        self.agent_id = agent_id


class CollaborationSessionNotFoundError(MCPError):
    """协作会话未找到"""
    def __init__(self, session_id: str):
        super().__init__(f"Collaboration session not found: {session_id}")
        self.session_id = session_id


class CollaborationAlreadyRunningError(MCPError):
    """协作已在运行"""
    def __init__(self, session_id: str):
        super().__init__(f"Collaboration already running: {session_id}")
        self.session_id = session_id


class CollaborationCannotCancelError(MCPError):
    """协作无法取消"""
    def __init__(self, session_id: str, status: str):
        super().__init__(f"Collaboration cannot be cancelled, current status: {status}")
        self.session_id = session_id
        self.status = status


class InvalidConfigurationError(MCPError):
    """配置无效"""
    def __init__(self, message: str):
        super().__init__(f"Invalid MCP configuration: {message}")


class MessageBusError(MCPError):
    """消息总线错误"""
    pass


class OrchestrationError(MCPError):
    """编排错误"""
    pass
