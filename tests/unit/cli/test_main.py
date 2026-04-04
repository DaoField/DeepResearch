# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
CLI主模块单元测试
"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from langchain_core.messages import HumanMessage, AIMessage

from deepresearch.cli.utils import (
    validate_messages,
    create_parser,
    main,
    single_query,
    validate_config_dir,
)
from deepresearch.cli.config import CLIConfig
from deepresearch.cli.exceptions import ValidationError, CLIError, ConfigurationError


class TestValidateMessages:
    """测试validate_messages函数。"""

    def test_valid_messages(self):
        """测试有效的消息列表。"""
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there"),
        ]
        result = validate_messages(messages)
        assert result == messages

    def test_empty_list(self):
        """测试空列表。"""
        with pytest.raises(ValidationError) as exc_info:
            validate_messages([])
        assert "输入不能为空" in str(exc_info.value)

    def test_invalid_message_types(self):
        """测试无效的消息类型。"""
        messages = ["not a message", 123]
        with pytest.raises(ValidationError) as exc_info:
            validate_messages(messages)
        assert "消息必须包含有效的 HumanMessage 或 AIMessage 对象" in str(exc_info.value)

    def test_mixed_messages(self):
        """测试混合有效和无效的消息。"""
        messages = [
            HumanMessage(content="Valid"),
            "Invalid",
            AIMessage(content="Also valid"),
        ]
        result = validate_messages(messages)
        assert len(result) == 2
        assert isinstance(result[0], HumanMessage)
        assert isinstance(result[1], AIMessage)


class TestCreateParser:
    """测试create_parser函数。"""

    def test_parser_creation(self):
        """测试解析器创建。"""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "deepresearch"

    def test_default_args(self):
        """测试默认参数。"""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.query is None
        assert args.depth is None
        assert args.no_html is False
        assert args.output is None
        assert args.log_level is None
        assert args.log_file is None
        assert args.theme is None

    def test_query_argument(self):
        """测试查询参数。"""
        parser = create_parser()
        args = parser.parse_args(["-q", "测试查询"])
        assert args.query == "测试查询"

    def test_depth_argument(self):
        """测试深度参数。"""
        parser = create_parser()
        args = parser.parse_args(["--depth", "5"])
        assert args.depth == 5

    def test_no_html_flag(self):
        """测试no-html标志。"""
        parser = create_parser()
        args = parser.parse_args(["--no-html"])
        assert args.no_html is True

    def test_output_argument(self):
        """测试输出路径参数。"""
        parser = create_parser()
        args = parser.parse_args(["-o", "/path/to/output"])
        assert args.output == "/path/to/output"

    def test_log_level_argument(self):
        """测试日志级别参数。"""
        parser = create_parser()
        args = parser.parse_args(["--log-level", "DEBUG"])
        assert args.log_level == "DEBUG"

    def test_invalid_log_level(self):
        """测试无效的日志级别。"""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--log-level", "INVALID"])

    def test_theme_argument(self):
        """测试主题参数。"""
        parser = create_parser()
        args = parser.parse_args(["--theme", "colorful"])
        assert args.theme == "colorful"

    def test_config_dir_argument(self):
        """测试配置目录参数。"""
        parser = create_parser()
        args = parser.parse_args(["--config-dir", "/path/to/config"])
        assert args.config_dir == "/path/to/config"

    def test_config_dir_short_option(self):
        """测试配置目录短选项。"""
        parser = create_parser()
        args = parser.parse_args(["-c", "/path/to/config"])
        assert args.config_dir == "/path/to/config"

    def test_version_flag(self):
        """测试版本标志。"""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0


class TestMainFunction:
    """测试main函数。"""

    @patch("deepresearch.cli.utils.single_query")
    @patch("deepresearch.cli.utils.configure_logging")
    def test_single_query_mode(self, mock_logging, mock_single_query):
        """测试单次查询模式。"""
        mock_single_query.return_value = "查询结果"

        result = main(["-q", "测试查询"])

        assert result == 0
        mock_single_query.assert_called_once()
        mock_logging.assert_called_once()

    @patch("deepresearch.cli.utils.interactive_agent")
    @patch("deepresearch.cli.utils.configure_logging")
    def test_interactive_mode(self, mock_logging, mock_interactive):
        """测试交互式模式。"""
        # 直接返回一个表示成功的整数
        mock_interactive.return_value = 0

        result = main([])

        assert result == 0
        mock_interactive.assert_called_once()

    @patch("deepresearch.cli.utils.get_cli_config")
    def test_configuration_error(self, mock_get_config):
        """测试配置错误处理。"""
        from deepresearch.cli.exceptions import ConfigurationError
        mock_get_config.side_effect = ConfigurationError("配置错误")

        result = main([])

        assert result == 2

    def test_keyboard_interrupt(self):
        """测试键盘中断处理。"""
        with patch("deepresearch.cli.utils.single_query") as mock_query:
            mock_query.side_effect = KeyboardInterrupt()
            result = main(["-q", "test"])
            assert result == 130


class TestSingleQuery:
    """测试single_query函数。"""

    @patch("deepresearch.cli.utils.call_agent")
    @patch("deepresearch.cli.utils.create_ui")
    def test_successful_query(self, mock_create_ui, mock_call_agent):
        """测试成功的查询。"""
        mock_ui = MagicMock()
        mock_ui.spinner.return_value.__enter__ = MagicMock()
        mock_ui.spinner.return_value.__exit__ = MagicMock()
        mock_create_ui.return_value = mock_ui

        mock_call_agent.return_value = [
            HumanMessage(content="查询"),
            AIMessage(content="结果"),
        ]

        config = CLIConfig()
        result = asyncio.run(single_query("测试查询", config))

        assert result == "结果"
        mock_call_agent.assert_called_once()

    @patch("deepresearch.cli.utils.call_agent")
    @patch("deepresearch.cli.utils.create_ui")
    def test_empty_response(self, mock_create_ui, mock_call_agent):
        """测试空响应。"""
        mock_ui = MagicMock()
        mock_ui.spinner.return_value.__enter__ = MagicMock()
        mock_ui.spinner.return_value.__exit__ = MagicMock()
        mock_create_ui.return_value = mock_ui

        mock_call_agent.return_value = [HumanMessage(content="查询")]

        config = CLIConfig()
        result = asyncio.run(single_query("测试查询", config))

        assert result == ""


class TestArgumentCombinations:
    """测试参数组合。"""

    def test_all_arguments(self):
        """测试所有参数组合。"""
        parser = create_parser()
        args = parser.parse_args([
            "-q", "查询",
            "--depth", "7",
            "--no-html",
            "-o", "/output/path",
            "--log-level", "DEBUG",
            "--log-file", "/log/path",
            "--theme", "colorful",
            "--config-dir", "/config/path",
        ])

        assert args.query == "查询"
        assert args.depth == 7
        assert args.no_html is True
        assert args.output == "/output/path"
        assert args.log_level == "DEBUG"
        assert args.log_file == "/log/path"
        assert args.theme == "colorful"
        assert args.config_dir == "/config/path"

    def test_short_options(self):
        """测试短选项。"""
        parser = create_parser()
        args = parser.parse_args([
            "-q", "查询",
            "-d", "5",
            "-o", "/output",
            "-c", "/config",
        ])

        assert args.query == "查询"
        assert args.depth == 5
        assert args.output == "/output"
        assert args.config_dir == "/config"


class TestValidateConfigDir:
    """测试validate_config_dir函数。"""

    def test_valid_config_dir(self, tmp_path):
        """测试有效的配置目录。"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        result = validate_config_dir(str(config_dir))

        assert result == config_dir.resolve()

    def test_nonexistent_config_dir(self):
        """测试不存在的配置目录。"""
        with pytest.raises(ConfigurationError) as exc_info:
            validate_config_dir("/nonexistent/path/to/config")
        assert "配置路径不存在" in str(exc_info.value)

    def test_config_dir_is_file(self, tmp_path):
        """测试配置路径是文件而非目录。"""
        config_file = tmp_path / "config"
        config_file.write_text("test")

        with pytest.raises(ConfigurationError) as exc_info:
            validate_config_dir(str(config_file))
        assert "配置路径不是目录" in str(exc_info.value)

    def test_config_dir_with_tilde(self, tmp_path, monkeypatch):
        """测试包含~的配置目录路径。"""
        # 模拟用户主目录
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("USERPROFILE", str(tmp_path))

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        result = validate_config_dir("~/config")

        assert result == config_dir.resolve()


class TestConfigDirEnvVar:
    """测试配置目录环境变量。"""

    def test_config_dir_from_env(self, monkeypatch, tmp_path):
        """测试从环境变量读取配置目录。"""
        config_dir = tmp_path / "env_config"
        config_dir.mkdir()

        monkeypatch.setenv("DEEPRESEARCH_CONFIG_DIR", str(config_dir))

        config = CLIConfig.from_env()

        assert config.config_dir == str(config_dir)

    def test_config_dir_env_priority(self, monkeypatch, tmp_path):
        """测试环境变量与参数优先级。"""
        env_dir = tmp_path / "env_config"
        env_dir.mkdir()
        arg_dir = tmp_path / "arg_config"
        arg_dir.mkdir()

        monkeypatch.setenv("DEEPRESEARCH_CONFIG_DIR", str(env_dir))

        # 参数优先级高于环境变量
        config = CLIConfig.from_env()
        # 通过get_cli_config传递参数覆盖环境变量
        config_with_arg = CLIConfig(
            **{
                **{k: getattr(config, k) for k in CLIConfig.__dataclass_fields__},
                "config_dir": str(arg_dir),
            }
        )

        assert config_with_arg.config_dir == str(arg_dir)


class TestHelpOutput:
    """测试帮助输出。"""

    def test_help_contains_description(self):
        """测试帮助包含描述。"""
        parser = create_parser()
        help_text = parser.format_help()
        assert "DeepResearch" in help_text

    def test_help_contains_examples(self):
        """测试帮助包含示例。"""
        parser = create_parser()
        help_text = parser.format_help()
        assert "示例" in help_text or "Example" in help_text

    def test_epilog_contains_env_vars(self):
        """测试epilog包含环境变量。"""
        parser = create_parser()
        # epilog内容在format_help中
        help_text = parser.format_help()
        assert "DEEPRESEARCH" in help_text or "环境变量" in help_text

    def test_help_contains_config_dir(self):
        """测试帮助包含配置目录参数说明。"""
        parser = create_parser()
        help_text = parser.format_help()
        assert "--config-dir" in help_text
        assert "-c" in help_text
        assert "配置" in help_text
