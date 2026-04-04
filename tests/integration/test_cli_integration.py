# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from deepresearch.cli.config import CLIConfig, get_cli_config
from deepresearch.cli.exceptions import ConfigurationError, ValidationError
from deepresearch.cli.history import HistoryEntry, HistoryManager, get_default_history_path
from deepresearch.cli.ui import TerminalUI, create_ui
from deepresearch.cli.utils import create_parser, validate_messages


class TestConfigAndHistoryIntegration:
    def test_config_with_history_path(self, tmp_path: Path):
        history_file = tmp_path / "history.json"
        config = CLIConfig(
            history_file=str(history_file),
            max_history=50,
        )

        history = HistoryManager(
            history_file=config.get_history_path(),
            max_entries=config.max_history,
        )

        history.add_entry("测试", "响应")
        assert len(history._entries) == 1

    def test_history_persists_with_config(self, tmp_path: Path):
        history_file = tmp_path / "history.json"
        config = CLIConfig(history_file=str(history_file))

        history1 = HistoryManager(history_file=config.get_history_path())
        history1.add_entry("问题1", "回答1")

        history2 = HistoryManager(history_file=config.get_history_path())
        assert len(history2._entries) == 1
        assert history2._entries[0].user_input == "问题1"


class TestUIAndConfigIntegration:
    def test_ui_uses_config_theme(self):
        config = CLIConfig(theme="colorful")
        ui = create_ui(theme=config.theme)
        assert ui.theme == "colorful"

    def test_ui_with_different_themes(self):
        themes = ["default", "minimal", "colorful"]
        for theme in themes:
            config = CLIConfig(theme=theme)  # type: ignore
            ui = create_ui(theme=config.theme)
            assert ui.theme == theme


class TestMainAndConfigIntegration:
    def test_parser_with_config_defaults(self):
        parser = create_parser()
        args = parser.parse_args([])

        config = get_cli_config(
            max_depth=args.depth,
            save_as_html=not args.no_html if args.no_html else None,
        )

        assert isinstance(config, CLIConfig)

    def test_config_override_from_args(self):
        default_config = CLIConfig()
        assert default_config.max_depth == 3

        parser = create_parser()
        args = parser.parse_args(["--depth", "7"])

        config = get_cli_config(max_depth=args.depth)
        assert config.max_depth == 7


class TestExceptionHandlingIntegration:
    def test_validation_error_in_message_flow(self):
        with pytest.raises(ValidationError):
            validate_messages([])

        with pytest.raises(ValidationError):
            validate_messages(["not a message"])

    def test_error_recovery(self, tmp_path: Path):
        history_file = tmp_path / "history.json"

        history_file.write_text("invalid json")

        history = HistoryManager(history_file=history_file)
        assert len(history._entries) == 0

        history.add_entry("问题", "回答")
        assert len(history._entries) == 1


class TestEndToEndWorkflow:
    def test_complete_session_workflow(self, tmp_path: Path):
        history_file = tmp_path / "history.json"

        config = CLIConfig(
            history_file=str(history_file),
            theme="default",
            max_history=100,
        )

        ui = create_ui(theme=config.theme)

        history = HistoryManager(
            history_file=config.get_history_path(),
            max_entries=config.max_history,
        )

        messages = [
            HumanMessage(content="你好"),
            AIMessage(content="你好！有什么可以帮助你的？"),
        ]

        valid_messages = validate_messages(messages)
        assert len(valid_messages) == 2

        history.add_entry("你好", "你好！有什么可以帮助你的？")
        assert len(history._entries) == 1

        stats = history.get_stats()
        assert stats["total_entries"] == 1
        assert stats["sessions"] == 1

    def test_multiple_sessions(self, tmp_path: Path):
        history_file = tmp_path / "history.json"

        history1 = HistoryManager(history_file=history_file)
        history1._session_id = "session1"
        history1.add_entry("问题1", "回答1")

        history2 = HistoryManager(history_file=history_file)
        history2._session_id = "session2"
        history2.add_entry("问题2", "回答2")

        session1_entries = history2.get_session_history("session1")
        session2_entries = history2.get_session_history("session2")

        assert len(session1_entries) == 1
        assert len(session2_entries) == 1
        assert session1_entries[0].user_input == "问题1"
        assert session2_entries[0].user_input == "问题2"


class TestCrossPlatformCompatibility:
    def test_path_handling(self, tmp_path: Path):
        paths = [
            str(tmp_path / "history.json"),
            str(tmp_path / "subdir" / "history.json"),
        ]

        for path in paths:
            config = CLIConfig(history_file=path)
            history_path = config.get_history_path()
            assert history_path is not None
            assert history_path.suffix == ".json"

    def test_unicode_support(self, tmp_path: Path):
        history_file = tmp_path / "history.json"
        history = HistoryManager(history_file=history_file)

        history.add_entry("中文问题 🎉", "中文回答 🚀")
        history.add_entry("日本語の質問", "日本語の回答")
        history.add_entry("Emoji: 🎊🎈🎁", "Response: 🎉🎊")

        history2 = HistoryManager(history_file=history_file)
        assert len(history2._entries) == 3
        assert "🎉" in history2._entries[0].user_input
        assert "日本語" in history2._entries[1].user_input


class TestPerformanceAndLimits:
    def test_large_history_handling(self, tmp_path: Path):
        history_file = tmp_path / "history.json"
        history = HistoryManager(history_file=history_file, max_entries=100)

        for i in range(150):
            history.add_entry(f"问题{i}", f"回答{i}")

        assert len(history._entries) == 100

        assert history._entries[-1].user_input == "问题149"

    def test_history_search_performance(self, tmp_path: Path):
        history_file = tmp_path / "history.json"
        history = HistoryManager(history_file=history_file)

        for i in range(100):
            history.add_entry(f"问题{i} 关键词", f"回答{i}")

        start = time.time()
        results = history.search("关键词")
        elapsed = time.time() - start

        assert len(results) == 100
        assert elapsed < 1.0


class TestConfigurationPriority:
    def test_env_overrides_default(self, monkeypatch):
        monkeypatch.setenv("DEEPRESEARCH_MAX_DEPTH", "8")
        monkeypatch.setenv("DEEPRESEARCH_THEME", "colorful")

        config = CLIConfig.from_env()
        assert config.max_depth == 8
        assert config.theme == "colorful"

    def test_args_override_env(self, monkeypatch):
        monkeypatch.setenv("DEEPRESEARCH_MAX_DEPTH", "8")

        config = get_cli_config(max_depth=5)
        assert config.max_depth == 5

    def test_explicit_overrides_all(self):
        config = CLIConfig(max_depth=10, theme="minimal")
        assert config.max_depth == 10
        assert config.theme == "minimal"
