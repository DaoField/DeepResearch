# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
CLI历史模块单元测试
"""

import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path

from deepresearch.cli.history import HistoryEntry, HistoryManager, get_default_history_path
from deepresearch.cli.exceptions import FileOperationError


class TestHistoryEntry:
    """测试HistoryEntry类。"""

    def test_creation(self):
        """测试创建历史条目。"""
        entry = HistoryEntry(
            timestamp="2025-01-01T12:00:00",
            user_input="测试输入",
            response="测试响应",
            session_id="session123",
        )
        assert entry.timestamp == "2025-01-01T12:00:00"
        assert entry.user_input == "测试输入"
        assert entry.response == "测试响应"
        assert entry.session_id == "session123"

    def test_to_dict(self):
        """测试转换为字典。"""
        entry = HistoryEntry(
            timestamp="2025-01-01T12:00:00",
            user_input="测试输入",
            response="测试响应",
        )
        data = entry.to_dict()
        assert data["timestamp"] == "2025-01-01T12:00:00"
        assert data["user_input"] == "测试输入"
        assert data["response"] == "测试响应"
        assert data["session_id"] is None

    def test_from_dict(self):
        """测试从字典创建。"""
        data = {
            "timestamp": "2025-01-01T12:00:00",
            "user_input": "测试输入",
            "response": "测试响应",
            "session_id": "session123",
        }
        entry = HistoryEntry.from_dict(data)
        assert entry.timestamp == "2025-01-01T12:00:00"
        assert entry.user_input == "测试输入"
        assert entry.response == "测试响应"
        assert entry.session_id == "session123"

    def test_from_dict_partial(self):
        """测试从部分字典创建。"""
        data = {
            "timestamp": "2025-01-01T12:00:00",
            "user_input": "测试输入",
        }
        entry = HistoryEntry.from_dict(data)
        assert entry.timestamp == "2025-01-01T12:00:00"
        assert entry.user_input == "测试输入"
        assert entry.response == ""
        assert entry.session_id is None


class TestHistoryManager:
    """测试HistoryManager类。"""

    def test_initialization_without_file(self):
        """测试无文件初始化。"""
        manager = HistoryManager(history_file=None)
        assert manager.history_file is None
        assert manager.max_entries == 100
        assert len(manager._entries) == 0

    def test_initialization_with_file(self, tmp_path):
        """测试有文件初始化。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file, max_entries=50)
        assert manager.history_file == history_file
        assert manager.max_entries == 50

    def test_add_entry(self, tmp_path):
        """测试添加条目。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        manager.add_entry("用户问题", "系统回答")

        assert len(manager._entries) == 1
        assert manager._entries[0].user_input == "用户问题"
        assert manager._entries[0].response == "系统回答"
        assert manager._entries[0].session_id is not None

    def test_add_entry_creates_file(self, tmp_path):
        """测试添加条目创建文件。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        manager.add_entry("问题", "回答")

        assert history_file.exists()

    def test_max_entries_limit(self, tmp_path):
        """测试最大条目限制。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file, max_entries=3)

        for i in range(5):
            manager.add_entry(f"问题{i}", f"回答{i}")

        assert len(manager._entries) == 3
        # 应该保留最新的条目
        assert manager._entries[0].user_input == "问题2"
        assert manager._entries[2].user_input == "问题4"

    def test_get_recent(self, tmp_path):
        """测试获取最近条目。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        for i in range(10):
            manager.add_entry(f"问题{i}", f"回答{i}")

        recent = manager.get_recent(3)
        assert len(recent) == 3
        assert recent[0].user_input == "问题7"
        assert recent[2].user_input == "问题9"

    def test_get_recent_more_than_available(self, tmp_path):
        """测试获取超过可用数量的条目。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        manager.add_entry("问题1", "回答1")
        manager.add_entry("问题2", "回答2")

        recent = manager.get_recent(10)
        assert len(recent) == 2

    def test_get_recent_empty(self, tmp_path):
        """测试空历史记录。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        recent = manager.get_recent(5)
        assert len(recent) == 0

    def test_get_session_history(self, tmp_path):
        """测试获取会话历史。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        # 模拟不同会话
        manager._session_id = "session1"
        manager.add_entry("问题1", "回答1")

        manager._session_id = "session2"
        manager.add_entry("问题2", "回答2")

        session1_history = manager.get_session_history("session1")
        assert len(session1_history) == 1
        assert session1_history[0].user_input == "问题1"

    def test_search(self, tmp_path):
        """测试搜索功能。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        manager.add_entry("人工智能的发展", "回答1")
        manager.add_entry("机器学习算法", "回答2")
        manager.add_entry("人工智能应用", "回答3")

        results = manager.search("人工智能")
        assert len(results) == 2

    def test_search_case_insensitive(self, tmp_path):
        """测试大小写不敏感搜索。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        manager.add_entry("Artificial Intelligence", "回答")

        results = manager.search("artificial")
        assert len(results) == 1

    def test_search_in_response(self, tmp_path):
        """测试在响应中搜索。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        manager.add_entry("问题", "这是关于Python的回答")

        results = manager.search("Python")
        assert len(results) == 1

    def test_clear(self, tmp_path):
        """测试清空历史。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        manager.add_entry("问题", "回答")
        assert len(manager._entries) == 1
        assert history_file.exists()

        manager.clear()
        assert len(manager._entries) == 0
        assert not history_file.exists()

    def test_clear_without_file(self):
        """测试无文件时清空。"""
        manager = HistoryManager(history_file=None)
        manager.add_entry("问题", "回答")

        manager.clear()
        assert len(manager._entries) == 0

    def test_get_stats_empty(self):
        """测试空历史统计。"""
        manager = HistoryManager(history_file=None)
        stats = manager.get_stats()

        assert stats["total_entries"] == 0
        assert stats["sessions"] == 0
        assert stats["first_entry"] is None
        assert stats["last_entry"] is None

    def test_get_stats_with_entries(self, tmp_path):
        """测试有条目时的统计。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        manager.add_entry("问题1", "回答1")
        manager.add_entry("问题2", "回答2")

        stats = manager.get_stats()
        assert stats["total_entries"] == 2
        assert stats["sessions"] == 1
        assert stats["first_entry"] is not None
        assert stats["last_entry"] is not None

    def test_load_history(self, tmp_path):
        """测试加载历史记录。"""
        history_file = tmp_path / "history.json"

        # 预先创建历史文件
        data = [
            {
                "timestamp": "2025-01-01T12:00:00",
                "user_input": "历史问题",
                "response": "历史回答",
                "session_id": "old_session",
            }
        ]
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        manager = HistoryManager(history_file=history_file)
        assert len(manager._entries) == 1
        assert manager._entries[0].user_input == "历史问题"

    def test_load_invalid_json(self, tmp_path):
        """测试加载无效JSON。"""
        history_file = tmp_path / "history.json"
        history_file.write_text("invalid json")

        manager = HistoryManager(history_file=history_file)
        # 应该能正常初始化，但条目为空
        assert len(manager._entries) == 0

    def test_load_non_list_json(self, tmp_path):
        """测试加载非列表JSON。"""
        history_file = tmp_path / "history.json"
        history_file.write_text('{"key": "value"}')

        manager = HistoryManager(history_file=history_file)
        assert len(manager._entries) == 0


class TestGetDefaultHistoryPath:
    """测试get_default_history_path函数。"""

    def test_returns_path(self):
        """测试返回路径对象。"""
        path = get_default_history_path()
        assert isinstance(path, Path)
        assert path.name == "history.json"

    def test_creates_directory(self):
        """测试创建目录。"""
        path = get_default_history_path()
        # 目录应该存在
        assert path.parent.exists()


class TestHistoryManagerPersistence:
    """测试历史管理器持久化。"""

    def test_persistence_roundtrip(self, tmp_path):
        """测试持久化往返。"""
        history_file = tmp_path / "history.json"

        # 第一个管理器添加条目
        manager1 = HistoryManager(history_file=history_file)
        manager1.add_entry("问题1", "回答1")
        manager1.add_entry("问题2", "回答2")

        # 第二个管理器读取文件
        manager2 = HistoryManager(history_file=history_file)
        assert len(manager2._entries) == 2
        assert manager2._entries[0].user_input == "问题1"
        assert manager2._entries[1].user_input == "问题2"

    def test_unicode_persistence(self, tmp_path):
        """测试Unicode字符持久化。"""
        history_file = tmp_path / "history.json"
        manager = HistoryManager(history_file=history_file)

        manager.add_entry("中文问题 🎉", "中文回答 🚀")

        # 重新加载
        manager2 = HistoryManager(history_file=history_file)
        assert manager2._entries[0].user_input == "中文问题 🎉"
        assert manager2._entries[0].response == "中文回答 🚀"
