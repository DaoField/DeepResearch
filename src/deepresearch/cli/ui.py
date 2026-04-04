# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
CLI 用户界面模块

提供终端输出格式化、进度显示、颜色主题等功能。
"""

import shutil
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator, Literal

from deepresearch.logging_config import get_logger

logger = get_logger(__name__)

# ANSI 颜色代码
COLOR_CODES = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
}

BG_COLOR_CODES = {
    "black": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
}

STYLE_CODES = {
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "blink": "\033[5m",
    "reverse": "\033[7m",
    "hidden": "\033[8m",
    "strikethrough": "\033[9m",
}

RESET_CODE = "\033[0m"


@dataclass
class TerminalUI:
    """终端用户界面类。

    提供终端输出格式化、颜色样式、进度显示等功能。
    支持多种主题样式（default、minimal、colorful）。

    Attributes:
        theme: 主题样式，可选值为 "default"、"minimal"、"colorful"
        _color_enabled: 是否启用颜色输出，根据终端支持情况自动检测
        _terminal_width: 终端宽度，自动获取或默认为80
    """

    theme: Literal["default", "minimal", "colorful"] = "default"
    _color_enabled: bool = field(init=False, repr=False)
    _terminal_width: int = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """初始化后处理：检测终端颜色支持和获取终端宽度。"""
        object.__setattr__(self, "_color_enabled", self._check_color_support())
        object.__setattr__(self, "_terminal_width", self._get_terminal_width())

    def _check_color_support(self) -> bool:
        """检查终端是否支持颜色输出。

        Returns:
            如果终端支持颜色输出返回True，否则返回False
        """
        # Windows系统检查
        if sys.platform == "win32":
            try:
                import ctypes

                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except Exception:
                return False
        # Unix-like系统检查
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def _get_terminal_width(self) -> int:
        """获取终端宽度。

        Returns:
            终端列数，如果获取失败则返回默认值80
        """
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80

    def style(
        self,
        text: str,
        color: str | None = None,
        bg_color: str | None = None,
        bold: bool = False,
        dim: bool = False,
        italic: bool = False,
        underline: bool = False,
    ) -> str:
        """为文本添加样式。

        Args:
            text: 原始文本
            color: 文字颜色，可选值见COLOR_CODES
            bg_color: 背景颜色，可选值见BG_COLOR_CODES
            bold: 是否加粗
            dim: 是否暗淡
            italic: 是否斜体
            underline: 是否下划线

        Returns:
            带样式的文本，如果终端不支持颜色则返回原文本
        """
        if not self._color_enabled:
            return text

        codes = []

        if color and color.lower() in COLOR_CODES:
            codes.append(COLOR_CODES[color.lower()])
        if bg_color and bg_color.lower() in BG_COLOR_CODES:
            codes.append(BG_COLOR_CODES[bg_color.lower()])
        if bold:
            codes.append(STYLE_CODES["bold"])
        if dim:
            codes.append(STYLE_CODES["dim"])
        if italic:
            codes.append(STYLE_CODES["italic"])
        if underline:
            codes.append(STYLE_CODES["underline"])

        if codes:
            return f"{''.join(codes)}{text}{RESET_CODE}"
        return text

    def print(
        self,
        text: str = "",
        color: str | None = None,
        bold: bool = False,
        end: str = "\n",
    ) -> None:
        """打印带样式的文本。

        Args:
            text: 要打印的文本
            color: 文字颜色
            bold: 是否加粗
            end: 行尾字符，默认为换行符
        """
        styled_text = self.style(text, color=color, bold=bold)
        print(styled_text, end=end)

    def print_header(self, text: str) -> None:
        """打印标题。

        根据当前主题使用不同的样式打印标题。

        Args:
            text: 标题文本
        """
        if self.theme == "minimal":
            self.print(f"\n{text}", bold=True)
            self.print("=" * len(text))
        elif self.theme == "colorful":
            width = min(self._terminal_width, 60)
            self.print("\n" + "=" * width, color="cyan")
            self.print(text.center(width), color="bright_cyan", bold=True)
            self.print("=" * width, color="cyan")
        else:
            self.print(f"\n{'='*40}", color="blue")
            self.print(text, color="bright_blue", bold=True)
            self.print("=" * 40, color="blue")

    def print_success(self, text: str) -> None:
        """打印成功消息。

        Args:
            text: 成功消息文本
        """
        self.print(f"✓ {text}", color="green")

    def print_error(self, text: str) -> None:
        """打印错误消息。

        Args:
            text: 错误消息文本
        """
        self.print(f"✗ {text}", color="red", bold=True)

    def print_warning(self, text: str) -> None:
        """打印警告消息。

        Args:
            text: 警告消息文本
        """
        self.print(f"⚠ {text}", color="yellow")

    def print_info(self, text: str) -> None:
        """打印信息消息。

        Args:
            text: 信息消息文本
        """
        self.print(f"ℹ {text}", color="blue")

    def print_progress(self, message: str, step: int, total: int) -> None:
        """打印进度信息。

        Args:
            message: 进度消息
            step: 当前步骤（从1开始）
            total: 总步骤数
        """
        percentage = (step / total) * 100 if total > 0 else 0
        bar_length = 30
        filled = int(bar_length * step / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)

        if self.theme == "colorful":
            self.print(f"\r[{bar}] {percentage:.1f}% {message}", color="cyan", end="")
        else:
            self.print(f"\r[{bar}] {step}/{total} {message}", end="")

        if step >= total:
            self.print()  # 换行

    def clear_line(self) -> None:
        """清除当前行。"""
        print("\r" + " " * self._terminal_width + "\r", end="")

    @contextmanager
    def spinner(self, message: str = "Processing") -> Iterator[None]:
        """显示旋转进度指示器。

        使用上下文管理器方式显示旋转动画，适用于需要等待的操作。

        Args:
            message: 显示的消息

        Example:
            >>> with ui.spinner("Loading"):
            ...     time.sleep(2)

        Yields:
            None
        """
        import itertools
        import threading
        import time

        spinner_chars = itertools.cycle(
            ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        )
        stop_event = threading.Event()

        def spin() -> None:
            while not stop_event.is_set():
                char = next(spinner_chars)
                self.print(f"\r{char} {message}...", color="cyan", end="")
                time.sleep(0.1)
            self.clear_line()

        thread = threading.Thread(target=spin)
        thread.start()

        try:
            yield
        finally:
            stop_event.set()
            thread.join()


@dataclass
class ProgressTracker:
    """进度跟踪器。

    用于跟踪多步骤任务的进度，与TerminalUI配合使用显示进度信息。

    Attributes:
        ui: 终端UI实例，用于显示进度
        total_steps: 总步骤数
        current_step: 当前步骤（从0开始，会自动递增）
        _step_names: 步骤名称列表，用于自动显示步骤名称

    Example:
        >>> ui = TerminalUI()
        >>> tracker = ProgressTracker(ui, total_steps=3)
        >>> tracker.add_step("初始化")
        >>> tracker.add_step("处理")
        >>> tracker.add_step("完成")
        >>> tracker.next_step()  # 显示 "初始化"
        >>> tracker.next_step()  # 显示 "处理"
        >>> tracker.finish()     # 显示 "完成"
    """

    ui: TerminalUI
    total_steps: int
    current_step: int = 0
    _step_names: list[str] = field(default_factory=list, repr=False)

    def add_step(self, name: str) -> None:
        """添加步骤名称。

        Args:
            name: 步骤名称，将在调用next_step时自动显示
        """
        self._step_names.append(name)

    def next_step(self, message: str | None = None) -> None:
        """进入下一步。

        递增当前步骤并显示进度信息。如果提供了message参数则显示该消息，
        否则尝试从_step_names列表中获取对应的步骤名称。

        Args:
            message: 自定义进度消息，为None时使用步骤名称
        """
        self.current_step += 1
        step_name = message or (
            self._step_names[self.current_step - 1]
            if self.current_step <= len(self._step_names)
            else f"Step {self.current_step}"
        )
        self.ui.print_progress(step_name, self.current_step, self.total_steps)

    def finish(self) -> None:
        """完成所有步骤。

        将当前步骤设置为总步骤数并显示完成状态。
        """
        self.current_step = self.total_steps
        self.ui.print_progress("完成", self.total_steps, self.total_steps)


def create_ui(theme: Literal["default", "minimal", "colorful"] = "default") -> TerminalUI:
    """创建终端UI实例。

    工厂函数，用于创建配置好的TerminalUI实例。

    Args:
        theme: 主题样式，可选值为 "default"、"minimal"、"colorful"

    Returns:
        配置好的TerminalUI实例

    Example:
        >>> ui = create_ui("colorful")
        >>> ui.print_success("操作成功")
    """
    return TerminalUI(theme=theme)
