# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from deepresearch.mcp.message_bus import MessageBus
from deepresearch.mcp.types import Message, MessageType, ProgressEvent


class TestMessageBus:
    """测试消息总线"""

    def test_publish_message(self):
        """测试发布消息"""
        bus = MessageBus()
        msg = Message.create(
            from_agent_id="agent1",
            from_agent_name="Agent 1",
            content="Hello",
            session_id="session-1",
        )
        bus.publish_message(msg)
        messages = bus.get_messages("session-1")
        assert len(messages) == 1
        assert messages[0].content == "Hello"

    def test_get_messages_filtered(self):
        """测试按条件过滤获取消息"""
        bus = MessageBus()
        msg1 = Message.create(
            from_agent_id="agent1",
            from_agent_name="Agent 1",
            to_agent_id="agent2",
            content="Hello agent2",
            session_id="session-1",
        )
        msg2 = Message.create(
            from_agent_id="agent2",
            from_agent_name="Agent 2",
            to_agent_id="agent1",
            content="Reply agent1",
            session_id="session-1",
        )
        bus.publish_message(msg1)
        bus.publish_message(msg2)

        from_agent1 = bus.get_messages("session-1", from_agent_id="agent1")
        assert len(from_agent1) == 1
        assert from_agent1[0].from_agent_id == "agent1"

        to_agent2 = bus.get_messages("session-1", to_agent_id="agent2")
        assert len(to_agent2) == 1
        assert to_agent2[0].to_agent_id == "agent2"

    def test_subscribe_agent(self):
        """测试订阅点对点消息"""
        bus = MessageBus()
        received = []

        def callback(msg):
            received.append(msg)

        bus.subscribe_agent("agent1", callback)

        msg = Message.create(
            from_agent_id="agent2",
            from_agent_name="Agent 2",
            to_agent_id="agent1",
            content="Hello agent1",
            session_id="session-1",
        )
        bus.publish_message(msg)

        assert len(received) == 1
        assert received[0].content == "Hello agent1"

    def test_publish_progress(self):
        """测试发布进度事件"""
        bus = MessageBus()
        received = []

        def callback(event):
            received.append(event)

        sub_id = bus.subscribe_progress(callback, session_id="session-1")

        event = ProgressEvent(
            session_id="session-1",
            status=None,
            progress=0.5,
            message="Halfway",
        )
        bus.publish_progress(event)

        assert len(received) == 1
        assert received[0].progress == 0.5

    def test_clear_session(self):
        """测试清除会话"""
        bus = MessageBus()
        msg = Message.create(
            from_agent_id="agent1",
            from_agent_name="Agent 1",
            content="Hello",
            session_id="session-1",
        )
        bus.publish_message(msg)
        assert bus.get_session_message_count("session-1") == 1

        bus.clear_session("session-1")
        assert bus.get_session_message_count("session-1") == 0

    def test_get_session_message_count(self):
        """测试获取会话消息数量"""
        bus = MessageBus()
        assert bus.get_session_message_count("session-1") == 0

        msg = Message.create(
            from_agent_id="agent1",
            from_agent_name="Agent 1",
            content="Hello",
            session_id="session-1",
        )
        bus.publish_message(msg)
        assert bus.get_session_message_count("session-1") == 1
