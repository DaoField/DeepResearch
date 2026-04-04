# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
CLI模块集成测试

测试CLI各组件之间的集成。
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from deepresearch.cli.config import CLIConfig, get_cli_config
from deepresearch.cli.history import HistoryManager, HistoryEntry
from deepresearch.cli.ui import TerminalUI, create_ui
from deepresearch.cli.exceptions import ValidationError, ConfigurationError
from deepresearch.cli.main import validate_messages, create_parser
from langchain_core.messages import HumanMessage, AIMessage


class TestConfigAndHistoryIntegration:
    """测试配置和历史模块集成。"""

    def test_config_with_history_path(self, tmp_path):
        """测试带历史路径的配置。"""
        history_file = tmp_path / "history.json"
        config = CLIConfig(
            history_file=str(history_file),
            max_history=50,
        )

        # 使用配置创建历史管理器
        history = HistoryManager(
            history_file=config.get_history_path(),
            max_entries=config.max_history,
        )

        history.add_entry("测试", "响应")
        assert len(history._entries) == 1

    def test_history_persists_with_config(self, tmp_path):
        """测试历史记录随配置持久化。"""
        history_file = tmp_path / "history.json"
        config = CLIConfig(history_file=str(history_file))

        # 第一个历史管理器
        history1 = HistoryManager(history_file=config.get_history_path())
        history1.add_entry("问题1", "回答1")

        # 第二个历史管理器应该能读取到
        history2 = HistoryManager(history_file=config.get_history_path())
        assert len(history2._entries) == 1
        assert history2._entries[0].user_input == "问题1"


class TestUIAndConfigIntegration:
    """测试UI和配置模块集成。"""

    def test_ui_uses_config_theme(self):
        """测试UI使用配置的主题。"""
        config = CLIConfig(theme="colorful")
        ui = create_ui(theme=config.theme)
        assert ui.theme == "colorful"

    def test_ui_with_different_themes(self):
        """测试UI与不同主题的集成。"""
        themes = ["default", "minimal", "colorful"]
        for theme in themes:
            config = CLIConfig(theme=theme)  # type: ignore
            ui = create_ui(theme=config.theme)
            assert ui.theme == theme

    @patch("builtins.print")
    def test_ui_outputs_with_config(self, mock_print):
        """测试UI根据配置输出。"""
        config = CLIConfig(theme="default")
        ui = create_ui(theme=config.theme)

        ui.print_success("成功消息")
        assert mock_print.called


class TestMainAndConfigIntegration:
    """测试主模块和配置模块集成。"""

    def test_parser_with_config_defaults(self):
        """测试解析器使用配置默认值。"""
        parser = create_parser()
        args = parser.parse_args([])

        # 解析后的参数应该能与配置合并
        config = get_cli_config(
            max_depth=args.depth,
            save_as_html=not args.no_html if args.no_html else None,
        )

        assert isinstance(config, CLIConfig)

    def test_config_override_from_args(self):
        """测试从参数覆盖配置。"""
        # 默认配置
        default_config = CLIConfig()
        assert default_config.max_depth == 3

        # 从参数创建的配置
        parser = create_parser()
        args = parser.parse_args(["--depth", "7"])

        config = get_cli_config(max_depth=args.depth)
        assert config.max_depth == 7


class TestExceptionHandlingIntegration:
    """测试异常处理集成。"""

    def test_validation_error_in_message_flow(self):
        """测试消息流中的验证错误。"""
        # 空消息列表应该抛出ValidationError
        with pytest.raises(ValidationError):
            validate_messages([])

        # 无效的消息类型应该抛出ValidationError
        with pytest.raises(ValidationError):
            validate_messages(["not a message"])

    def test_error_recovery(self, tmp_path):
        """测试错误恢复。"""
        history_file = tmp_path / "history.json"

        # 创建损坏的历史文件
        history_file.write_text("invalid json")

        # 应该能正常初始化，不抛出异常
        history = HistoryManager(history_file=history_file)
        assert len(history._entries) == 0

        # 应该能正常使用
        history.add_entry("问题", "回答")
        assert len(history._entries) == 1


class TestEndToEndWorkflow:
    """测试端到端工作流。"""

    def test_complete_session_workflow(self, tmp_path):
        """测试完整的会话工作流。"""
        history_file = tmp_path / "history.json"

        # 1. 创建配置
        config = CLIConfig(
            history_file=str(history_file),
            theme="default",
            max_history=100,
        )

        # 2. 创建UI
        ui = create_ui(theme=config.theme)

        # 3. 创建历史管理器
        history = HistoryManager(
            history_file=config.get_history_path(),
            max_entries=config.max_history,
        )

        # 4. 模拟对话
        messages = [
            HumanMessage(content="你好"),
            AIMessage(content="你好！有什么可以帮助你的？"),
        ]

        # 5. 验证消息
        valid_messages = validate_messages(messages)
        assert len(valid_messages) == 2

        # 6. 保存到历史
        history.add_entry("你好", "你好！有什么可以帮助你的？")
        assert len(history._entries) == 1

        # 7. 验证历史统计
        stats = history.get_stats()
        assert stats["total_entries"] == 1
        assert stats["sessions"] == 1

    def test_multiple_sessions(self, tmp_path):
        """测试多个会话。"""
        history_file = tmp_path / "history.json"

        # 会话1
        history1 = HistoryManager(history_file=history_file)
        history1._session_id = "session1"
        history1.add_entry("问题1", "回答1")

        # 会话2
        history2 = HistoryManager(history_file=history_file)
        history2._session_id = "session2"
        history2.add_entry("问题2", "回答2")

        # 验证会话隔离
        session1_entries = history2.get_session_history("session1")
        session2_entries = history2.get_session_history("session2")

        assert len(session1_entries) == 1
        assert len(session2_entries) == 1
        assert session1_entries[0].user_input == "问题1"
        assert session2_entries[0].user_input == "问题2"


class TestCrossPlatformCompatibility:
    """测试跨平台兼容性。"""

    def test_path_handling(self, tmp_path):
        """测试路径处理。"""
        # 不同格式的路径
        paths = [
            str(tmp_path / "history.json"),
            str(tmp_path / "subdir" / "history.json"),
        ]

        for path in paths:
            config = CLIConfig(history_file=path)
            history_path = config.get_history_path()
            assert history_path is not None
            assert history_path.suffix == ".json"

    def test_unicode_support(self, tmp_path):
        """测试Unicode支持。"""
        history_file = tmp_path / "history.json"
        history = HistoryManager(history_file=history_file)

        # 添加Unicode内容
        history.add_entry("中文问题 🎉", "中文回答 🚀")
        history.add_entry("日本語の質問", "日本語の回答")
        history.add_entry("Emoji: 🎊🎈🎁", "Response: 🎉🎊")

        # 重新加载
        history2 = HistoryManager(history_file=history_file)
        assert len(history2._entries) == 3
        assert "🎉" in history2._entries[0].user_input
        assert "日本語" in history2._entries[1].user_input


class TestPerformanceAndLimits:
    """测试性能和限制。"""

    def test_large_history_handling(self, tmp_path):
        """测试大量历史记录处理。"""
        history_file = tmp_path / "history.json"
        history = HistoryManager(history_file=history_file, max_entries=100)

        # 添加大量条目
        for i in range(150):
            history.add_entry(f"问题{i}", f"回答{i}")

        # 应该限制为max_entries
        assert len(history._entries) == 100

        # 应该保留最新的
        assert history._entries[-1].user_input == "问题149"

    def test_history_search_performance(self, tmp_path):
        """测试历史搜索性能。"""
        history_file = tmp_path / "history.json"
        history = HistoryManager(history_file=history_file)

        # 添加条目
        for i in range(100):
            history.add_entry(f"问题{i} 关键词", f"回答{i}")

        # 搜索应该快速完成
        import time
        start = time.time()
        results = history.search("关键词")
        elapsed = time.time() - start

        assert len(results) == 100
        assert elapsed < 1.0  # 应该在1秒内完成


class TestConfigurationPriority:
    """测试配置优先级。"""

    def test_env_overrides_default(self, monkeypatch):
        """测试环境变量覆盖默认值。"""
        monkeypatch.setenv("DEEPRESEARCH_MAX_DEPTH", "8")
        monkeypatch.setenv("DEEPRESEARCH_THEME", "colorful")

        config = CLIConfig.from_env()
        assert config.max_depth == 8
        assert config.theme == "colorful"

    def test_args_override_env(self, monkeypatch):
        """测试参数覆盖环境变量。"""
        monkeypatch.setenv("DEEPRESEARCH_MAX_DEPTH", "8")

        # 环境变量设置8，但参数覆盖为5
        config = get_cli_config(max_depth=5)
        assert config.max_depth == 5

    def test_explicit_overrides_all(self):
        """测试显式值覆盖所有。"""
        config = CLIConfig(max_depth=10, theme="minimal")
        assert config.max_depth == 10
        assert config.theme == "minimal"
