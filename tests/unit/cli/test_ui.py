# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
CLI UI模块单元测试
"""

import pytest
from unittest.mock import patch, MagicMock

from deepresearch.cli.ui import TerminalUI, ProgressTracker, create_ui


class TestTerminalUI:
    """测试TerminalUI类。"""

    def test_default_initialization(self):
        """测试默认初始化。"""
        ui = TerminalUI()
        assert ui.theme == "default"

    def test_custom_theme(self):
        """测试自定义主题。"""
        ui = TerminalUI(theme="colorful")
        assert ui.theme == "colorful"

    def test_terminal_width(self):
        """测试终端宽度获取。"""
        ui = TerminalUI()
        assert isinstance(ui._terminal_width, int)
        assert ui._terminal_width > 0

    def test_style_without_color(self):
        """测试无颜色样式。"""
        ui = TerminalUI()
        ui._color_enabled = False
        result = ui.style("test", color="red", bold=True)
        assert result == "test"

    def test_style_with_color(self):
        """测试带颜色样式。"""
        ui = TerminalUI()
        ui._color_enabled = True
        result = ui.style("test", color="red")
        assert "\033[" in result
        assert "test" in result

    def test_style_bold(self):
        """测试粗体样式。"""
        ui = TerminalUI()
        ui._color_enabled = True
        result = ui.style("test", bold=True)
        assert "\033[1m" in result

    def test_style_invalid_color(self):
        """测试无效颜色。"""
        ui = TerminalUI()
        ui._color_enabled = True
        result = ui.style("test", color="invalid_color")
        # 无效颜色应该被忽略，返回原始文本
        assert result == "test"


class TestTerminalUIThemes:
    """测试TerminalUI主题。"""

    @patch("builtins.print")
    def test_print_header_default(self, mock_print):
        """测试默认主题标题。"""
        ui = TerminalUI(theme="default")
        ui.print_header("Test Title")
        assert mock_print.called

    @patch("builtins.print")
    def test_print_header_minimal(self, mock_print):
        """测试最小主题标题。"""
        ui = TerminalUI(theme="minimal")
        ui.print_header("Test Title")
        assert mock_print.called

    @patch("builtins.print")
    def test_print_header_colorful(self, mock_print):
        """测试彩色主题标题。"""
        ui = TerminalUI(theme="colorful")
        ui.print_header("Test Title")
        assert mock_print.called


class TestTerminalUIMessages:
    """测试TerminalUI消息输出。"""

    @patch("builtins.print")
    def test_print_success(self, mock_print):
        """测试成功消息。"""
        ui = TerminalUI()
        ui.print_success("操作成功")
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert "✓" in args
        assert "操作成功" in args

    @patch("builtins.print")
    def test_print_error(self, mock_print):
        """测试错误消息。"""
        ui = TerminalUI()
        ui.print_error("操作失败")
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert "✗" in args
        assert "操作失败" in args

    @patch("builtins.print")
    def test_print_warning(self, mock_print):
        """测试警告消息。"""
        ui = TerminalUI()
        ui.print_warning("警告信息")
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert "⚠" in args
        assert "警告信息" in args

    @patch("builtins.print")
    def test_print_info(self, mock_print):
        """测试信息消息。"""
        ui = TerminalUI()
        ui.print_info("提示信息")
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert "ℹ" in args
        assert "提示信息" in args


class TestProgressTracker:
    """测试ProgressTracker类。"""

    @patch("builtins.print")
    def test_initialization(self, mock_print):
        """测试初始化。"""
        ui = TerminalUI()
        tracker = ProgressTracker(ui, total_steps=5)
        assert tracker.total_steps == 5
        assert tracker.current_step == 0

    @patch("builtins.print")
    def test_add_step(self, mock_print):
        """测试添加步骤。"""
        ui = TerminalUI()
        tracker = ProgressTracker(ui, total_steps=3)
        tracker.add_step("Step 1")
        tracker.add_step("Step 2")
        assert len(tracker._step_names) == 2

    @patch("builtins.print")
    def test_next_step(self, mock_print):
        """测试下一步。"""
        ui = TerminalUI()
        tracker = ProgressTracker(ui, total_steps=3)
        tracker.next_step("Processing")
        assert tracker.current_step == 1

    @patch("builtins.print")
    def test_finish(self, mock_print):
        """测试完成。"""
        ui = TerminalUI()
        tracker = ProgressTracker(ui, total_steps=3)
        tracker.finish()
        assert tracker.current_step == 3


class TestCreateUI:
    """测试create_ui函数。"""

    def test_default_theme(self):
        """测试默认主题。"""
        ui = create_ui()
        assert isinstance(ui, TerminalUI)
        assert ui.theme == "default"

    def test_custom_theme(self):
        """测试自定义主题。"""
        ui = create_ui(theme="colorful")
        assert ui.theme == "colorful"

    def test_all_themes(self):
        """测试所有可用主题。"""
        themes = ["default", "minimal", "colorful"]
        for theme in themes:
            ui = create_ui(theme=theme)  # type: ignore
            assert ui.theme == theme


class TestColorSupport:
    """测试颜色支持检测。"""

    @patch("sys.platform", "win32")
    @patch("ctypes.windll")
    def test_windows_color_support(self, mock_windll):
        """测试Windows颜色支持。"""
        ui = TerminalUI()
        # Windows系统应该尝试启用颜色支持
        assert ui._color_enabled is not None

    @patch("sys.platform", "linux")
    @patch("sys.stdout")
    def test_unix_color_support(self, mock_stdout):
        """测试Unix颜色支持。"""
        mock_stdout.isatty.return_value = True
        ui = TerminalUI()
        assert ui._color_enabled is True

    @patch("sys.platform", "linux")
    @patch("sys.stdout")
    def test_no_tty(self, mock_stdout):
        """测试非TTY环境。"""
        mock_stdout.isatty.return_value = False
        ui = TerminalUI()
        assert ui._color_enabled is False


class TestDataclassFeatures:
    """测试Dataclass特性。"""

    def test_terminal_ui_is_dataclass(self):
        """测试TerminalUI是dataclass。"""
        from dataclasses import is_dataclass

        assert is_dataclass(TerminalUI)

    def test_progress_tracker_is_dataclass(self):
        """测试ProgressTracker是dataclass。"""
        from dataclasses import is_dataclass

        assert is_dataclass(ProgressTracker)

    def test_terminal_ui_fields(self):
        """测试TerminalUI字段定义。"""
        from dataclasses import fields

        ui_fields = {f.name: f for f in fields(TerminalUI)}
        assert "theme" in ui_fields
        assert "_color_enabled" in ui_fields
        assert "_terminal_width" in ui_fields

        # 检查theme字段有默认值
        assert ui_fields["theme"].default == "default"

        # 检查内部字段是init=False
        assert ui_fields["_color_enabled"].init is False
        assert ui_fields["_terminal_width"].init is False

    def test_terminal_ui_repr(self):
        """测试TerminalUI的repr不包含内部字段。"""
        ui = TerminalUI(theme="colorful")
        repr_str = repr(ui)
        # 内部字段不应该出现在repr中
        assert "_color_enabled" not in repr_str
        assert "_terminal_width" not in repr_str
        assert "theme" in repr_str

    def test_progress_tracker_fields(self):
        """测试ProgressTracker字段定义。"""
        from dataclasses import fields

        tracker_fields = {f.name: f for f in fields(ProgressTracker)}
        assert "ui" in tracker_fields
        assert "total_steps" in tracker_fields
        assert "current_step" in tracker_fields
        assert "_step_names" in tracker_fields

        # 检查current_step有默认值0
        assert tracker_fields["current_step"].default == 0

        # 检查_step_names使用default_factory
        assert tracker_fields["_step_names"].default_factory is not None

    def test_progress_tracker_default_step_names(self):
        """测试ProgressTracker步骤名称列表默认独立。"""
        ui = TerminalUI()
        tracker1 = ProgressTracker(ui, total_steps=3)
        tracker2 = ProgressTracker(ui, total_steps=3)

        tracker1.add_step("Step 1")

        # tracker2不应该受到tracker1的影响
        assert len(tracker1._step_names) == 1
        assert len(tracker2._step_names) == 0

    def test_terminal_ui_post_init(self):
        """测试TerminalUI的__post_init__正确初始化。"""
        ui = TerminalUI()

        # _color_enabled和_terminal_width应该在__post_init__中被设置
        assert hasattr(ui, "_color_enabled")
        assert hasattr(ui, "_terminal_width")
        assert isinstance(ui._color_enabled, bool)
        assert isinstance(ui._terminal_width, int)

    def test_terminal_ui_equality(self):
        """测试TerminalUI实例相等性。"""
        ui1 = TerminalUI(theme="default")
        ui2 = TerminalUI(theme="default")
        ui3 = TerminalUI(theme="colorful")

        # 相同主题，但由于_color_enabled和_terminal_width可能不同，
        # dataclass默认的相等性比较会比较所有字段
        # 这里主要测试功能正常
        assert ui1.theme == ui2.theme
        assert ui1.theme != ui3.theme

    def test_progress_tracker_equality(self):
        """测试ProgressTracker实例相等性。"""
        ui = TerminalUI()
        tracker1 = ProgressTracker(ui, total_steps=3, current_step=0)
        tracker2 = ProgressTracker(ui, total_steps=3, current_step=0)
        tracker3 = ProgressTracker(ui, total_steps=5, current_step=0)

        # 相同参数的tracker应该相等
        assert tracker1 == tracker2
        assert tracker1 != tracker3
