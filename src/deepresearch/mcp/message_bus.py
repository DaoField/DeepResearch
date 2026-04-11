# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Optional
from uuid import uuid4

from .exceptions import MessageBusError
from .types import Message, MessageType, ProgressEvent

logger = logging.getLogger(__name__)


class MessageBus:
    """消息总线

    支持：
    - 会话内消息存储
    - 发布/订阅模式
    - 点对点消息
    - 进度事件订阅
    """

    def __init__(self):
        # 按会话存储消息
        self._messages: dict[str, list[Message]] = defaultdict(list)
        # 全局订阅（所有事件）
        self._global_subscribers: list[Callable[[ProgressEvent], None]] = []
        # 按会话订阅
        self._session_subscribers: dict[str, list[Callable[[ProgressEvent], None]]] = defaultdict(list)
        # 点对点订阅（接收者agent_id）
        self._agent_subscribers: dict[str, list[Callable[[Message], None]]] = defaultdict(list)

    def publish_message(self, message: Message) -> None:
        """发布消息到总线

        Args:
            message: 消息对象
        """
        # 存储消息
        self._messages[message.session_id].append(message)

        # 通知点对点订阅者
        if message.to_agent_id and message.to_agent_id in self._agent_subscribers:
            for callback in self._agent_subscribers[message.to_agent_id]:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in agent subscriber callback: {e}")

        # 通知会话订阅者 - 作为进度事件包装
        event = ProgressEvent(
            session_id=message.session_id,
            status=None,
            progress=0.0,
            new_message=message,
        )
        self._notify_subscribers(event)

    def publish_progress(self, event: ProgressEvent) -> None:
        """发布进度事件

        Args:
            event: 进度事件
        """
        self._notify_subscribers(event)

    def subscribe_progress(
        self,
        callback: Callable[[ProgressEvent], None],
        session_id: Optional[str] = None,
    ) -> str:
        """订阅进度事件

        Args:
            callback: 回调函数
            session_id: 可选，指定订阅特定会话，如果为 None 订阅所有会话

        Returns:
            订阅ID（用于取消订阅）
        """
        if session_id is None:
            self._global_subscribers.append(callback)
        else:
            self._session_subscribers[session_id].append(callback)
        return f"{uuid4()}"

    def unsubscribe_progress(
        self,
        callback: Callable[[ProgressEvent], None],
        session_id: Optional[str] = None,
    ) -> bool:
        """取消进度订阅

        Args:
            callback: 回调函数
            session_id: 会话ID

        Returns:
            是否成功取消
        """
        if session_id is None:
            if callback in self._global_subscribers:
                self._global_subscribers.remove(callback)
                return True
        else:
            if session_id in self._session_subscribers and callback in self._session_subscribers[session_id]:
                self._session_subscribers[session_id].remove(callback)
                return True
        return False

    def subscribe_agent(
        self,
        agent_id: str,
        callback: Callable[[Message], None],
    ) -> str:
        """订阅发给特定智能体的点对点消息

        Args:
            agent_id: 智能体ID
            callback: 回调函数

        Returns:
            订阅ID
        """
        self._agent_subscribers[agent_id].append(callback)
        return f"{uuid4()}"

    def unsubscribe_agent(
        self,
        agent_id: str,
        callback: Callable[[Message], None],
    ) -> bool:
        """取消智能体订阅

        Args:
            agent_id: 智能体ID
            callback: 回调函数

        Returns:
            是否成功取消
        """
        if agent_id in self._agent_subscribers and callback in self._agent_subscribers[agent_id]:
            self._agent_subscribers[agent_id].remove(callback)
            return True
        return False

    def get_messages(
        self,
        session_id: str,
        from_agent_id: Optional[str] = None,
        to_agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
    ) -> list[Message]:
        """获取会话消息

        Args:
            session_id: 会话ID
            from_agent_id: 可选，按发送者过滤
            to_agent_id: 可选，按接收者过滤
            message_type: 可选，按消息类型过滤

        Returns:
            消息列表
        """
        messages = self._messages.get(session_id, [])

        if from_agent_id is not None:
            messages = [m for m in messages if m.from_agent_id == from_agent_id]
        if to_agent_id is not None:
            messages = [m for m in messages if m.to_agent_id == to_agent_id]
        if message_type is not None:
            messages = [m for m in messages if m.message_type == message_type]

        return messages

    def clear_session(self, session_id: str) -> None:
        """清除会话消息

        Args:
            session_id: 会话ID
        """
        if session_id in self._messages:
            del self._messages[session_id]
        if session_id in self._session_subscribers:
            del self._session_subscribers[session_id]
        logger.debug(f"Cleared message bus for session: {session_id}")

    def get_session_message_count(self, session_id: str) -> int:
        """获取会话消息数量

        Args:
            session_id: 会话ID

        Returns:
            消息数量
        """
        return len(self._messages.get(session_id, []))

    def _notify_subscribers(self, event: ProgressEvent) -> None:
        """通知所有相关订阅者"""
        # 全局订阅者
        for callback in self._global_subscribers:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in global progress subscriber: {e}")

        # 会话订阅者
        if event.session_id in self._session_subscribers:
            for callback in self._session_subscribers[event.session_id]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in session progress subscriber: {e}")


# 全局单例
message_bus = MessageBus()
