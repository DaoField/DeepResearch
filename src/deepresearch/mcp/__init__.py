# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from .agent_registry import AgentRegistry, agent_registry
from .collaboration_orchestrator import CollaborationOrchestrator
from .exceptions import (
    AgentAlreadyRegisteredError,
    AgentNotFoundError,
    CollaborationAlreadyRunningError,
    CollaborationCannotCancelError,
    CollaborationSessionNotFoundError,
    InvalidConfigurationError,
    MessageBusError,
    MCPError,
    OrchestrationError,
)
from .message_bus import MessageBus, message_bus
from .result_aggregator import ResultAggregator, result_aggregator
from .types import (
    AgentConfig,
    AgentCollaborationMode,
    AgentResult,
    CollaborationMode,
    CollaborationResult,
    CollaborationSession,
    CollaborationStatus,
    Message,
    MessageType,
    OutputDetail,
    ProgressEvent,
    ResponseStyle,
    Task,
    TaskPriority,
    TaskStatus,
)

# Global singleton instances
collaboration_orchestrator = CollaborationOrchestrator(
    registry=agent_registry,
    bus=message_bus,
    aggregator=result_aggregator,
)

__all__ = [
    # Types
    "AgentConfig",
    "AgentCollaborationMode",
    "AgentResult",
    "CollaborationMode",
    "CollaborationResult",
    "CollaborationSession",
    "CollaborationStatus",
    "Message",
    "MessageType",
    "OutputDetail",
    "ProgressEvent",
    "ResponseStyle",
    "Task",
    "TaskPriority",
    "TaskStatus",
    # Exceptions
    "MCPError",
    "AgentNotFoundError",
    "AgentAlreadyRegisteredError",
    "CollaborationSessionNotFoundError",
    "CollaborationAlreadyRunningError",
    "CollaborationCannotCancelError",
    "InvalidConfigurationError",
    "MessageBusError",
    "OrchestrationError",
    # Classes
    "AgentRegistry",
    "agent_registry",
    "MessageBus",
    "message_bus",
    "ResultAggregator",
    "result_aggregator",
    "CollaborationOrchestrator",
    "collaboration_orchestrator",
]
