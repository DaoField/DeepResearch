# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
DeepResearch CLI 主模块

提供命令行交互界面，支持交互式对话和单次查询模式。
"""

import argparse
import asyncio
import os
import signal
import sys
from pathlib import Path
from typing import List, Union

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command

from deepresearch.agent.agent import build_agent
from deepresearch.cli.config import CLIConfig, get_cli_config
from deepresearch.cli.exceptions import (
    AgentExecutionError,
    CLIError,
    ConfigurationError,
    UserInterruptError,
    ValidationError,
)
from deepresearch.config import config_manager
from deepresearch.config.llms_config import reload_llm_configs
from deepresearch.cli.history import HistoryManager, get_default_history_path
from deepresearch.cli.ui import TerminalUI, create_ui
from deepresearch.logging_config import configure_logging, get_logger

logger = get_logger(__name__)

# 全局变量用于信号处理
_shutdown_requested = False


def validate_config_dir(path: str) -> Path:
    """验证配置目录的有效性。

    Args:
        path: 配置目录路径

    Returns:
        解析后的绝对路径

    Raises:
        ConfigurationError: 路径无效时抛出
    """
    config_path = Path(path).expanduser().resolve()

    # 验证路径是否存在
    if not config_path.exists():
        raise ConfigurationError(f"配置路径不存在: {path}")

    # 验证路径是否为目录
    if not config_path.is_dir():
        raise ConfigurationError(f"配置路径不是目录: {path}")

    # 验证路径是否可读
    if not os.access(config_path, os.R_OK):
        raise ConfigurationError(f"无法读取配置路径: {path}")

    return config_path


def _signal_handler(signum: int, frame) -> None:
    """处理系统信号。"""
    global _shutdown_requested
    _shutdown_requested = True
    logger.info(f"接收到信号 {signum}，准备退出...")


# 注册信号处理器
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def validate_messages(
    messages: List[Union[HumanMessage, AIMessage]],
) -> List[Union[HumanMessage, AIMessage]]:
    """验证消息列表的有效性。

    Args:
        messages: 消息列表

    Returns:
        验证后的消息列表

    Raises:
        ValidationError: 验证失败时抛出
    """
    if not messages:
        raise ValidationError("输入不能为空")

    valid_messages = [m for m in messages if isinstance(m, (HumanMessage, AIMessage))]
    if not valid_messages:
        raise ValidationError("消息必须包含有效的 HumanMessage 或 AIMessage 对象")

    return valid_messages


async def call_agent(
    messages: List[Union[HumanMessage, AIMessage]],
    config: CLIConfig | None = None,
    ui: TerminalUI | None = None,
) -> List[Union[HumanMessage, AIMessage]]:
    """调用Agent处理消息。

    Args:
        messages: 消息列表
        config: CLI配置
        ui: 终端UI实例

    Returns:
        更新后的消息列表

    Raises:
        AgentExecutionError: Agent执行失败时抛出
        UserInterruptError: 用户中断时抛出
    """
    global _shutdown_requested

    if config is None:
        config = get_cli_config()

    if ui is None:
        ui = create_ui(theme=config.theme)

    # 验证输入
    valid_messages = validate_messages(messages)

    # 构建状态
    state = {"messages": valid_messages}
    agent_config = {
        "configurable": {
            "depth": config.max_depth,
            "save_as_html": config.save_as_html,
            "save_path": str(config.get_save_path()),
        }
    }

    # 构建Agent
    try:
        graph = build_agent()
    except Exception as e:
        logger.exception("构建Agent失败")
        raise AgentExecutionError(f"构建Agent失败: {e}", original_error=e)

    output = ""
    step_count = 0

    try:
        if ui and config.stream_output:
            ui.print_info("Agent正在处理，请稍候...")

        for message in graph.stream(
            input=state, config=agent_config, stream_mode="values"
        ):
            # 检查是否收到退出信号
            if _shutdown_requested:
                raise UserInterruptError("用户中断操作")

            step_count += 1

            # 处理Command类型
            if isinstance(message, Command):
                message = message.update

            # 提取输出
            if isinstance(message, dict) and "messages" in message:
                if "output" in message and isinstance(message["output"], dict):
                    if "message" in message["output"]:
                        output = message["output"]["message"]

            logger.debug(f"Agent处理步骤 {step_count} 完成")

    except UserInterruptError:
        raise
    except Exception as e:
        logger.exception("Agent执行过程中发生错误")
        raise AgentExecutionError(f"Agent执行失败: {e}", original_error=e)

    if not output:
        output = "Agent未返回有效输出"
        logger.warning(output)

    valid_messages.append(AIMessage(content=output))
    return valid_messages


async def interactive_agent(config: CLIConfig | None = None) -> int:
    """交互式对话模式。

    Args:
        config: CLI配置

    Returns:
        退出码
    """
    if config is None:
        config = get_cli_config()

    # 配置日志
    configure_logging(
        level=config.log_level,
        log_file=config.log_file,
    )

    # 创建UI
    ui = create_ui(theme=config.theme)

    # 初始化历史管理器
    history_file = config.get_history_path() or get_default_history_path()
    history = HistoryManager(history_file=history_file, max_entries=config.max_history)

    # 打印欢迎信息
    ui.print_header("欢迎使用 iFlytek DeepResearch!")
    ui.print_info("输入 'help' 查看帮助，'quit' 退出程序，'clear' 清空对话")
    ui.print()

    messages: List[Union[HumanMessage, AIMessage]] = []

    while True:
        try:
            # 获取用户输入
            try:
                user_input = input(ui.style("\n你: ", color="green", bold=True))
            except EOFError:
                ui.print()
                break

            user_input = user_input.strip()

            if not user_input:
                continue

            # 处理特殊命令
            if user_input.lower() == "quit":
                ui.print_success("感谢使用，再见！")
                break

            if user_input.lower() == "clear":
                messages = []
                ui.print_info("对话已清空")
                continue

            if user_input.lower() == "help":
                _print_help(ui)
                continue

            if user_input.lower() == "history":
                _print_history(ui, history)
                continue

            if user_input.lower().startswith("search "):
                keyword = user_input[7:].strip()
                _search_history(ui, history, keyword)
                continue

            # 处理用户消息
            messages.append(HumanMessage(content=user_input))

            # 调用Agent
            with ui.spinner("Agent正在思考"):
                try:
                    messages = await call_agent(
                        messages=messages,
                        config=config,
                        ui=ui,
                    )
                except UserInterruptError:
                    ui.print_warning("操作已中断")
                    continue
                except AgentExecutionError as e:
                    ui.print_error(f"Agent执行失败: {e}")
                    logger.error(f"Agent执行错误: {e}", exc_info=True)
                    # 移除失败的消息
                    if messages and isinstance(messages[-1], HumanMessage):
                        messages.pop()
                    continue

            # 显示响应
            if messages and isinstance(messages[-1], AIMessage):
                response = messages[-1].content
                ui.print(ui.style("\nAssistant: ", color="blue", bold=True))
                ui.print(response)

                # 保存到历史记录
                history.add_entry(user_input, response)

        except KeyboardInterrupt:
            ui.print()
            ui.print_warning("程序被中断")
            break
        except Exception as e:
            ui.print_error(f"发生错误: {e}")
            logger.exception("交互式对话中发生未预期的错误")

    return 0


def _print_help(ui: TerminalUI) -> None:
    """打印帮助信息。"""
    ui.print_header("帮助信息")
    help_text = """
可用命令:
  help              - 显示此帮助信息
  quit              - 退出程序
  clear             - 清空当前对话
  history           - 显示最近的历史记录
  search <关键词>   - 搜索历史记录

快捷键:
  Ctrl+C            - 中断当前操作
  Ctrl+D            - 退出程序

提示:
  - 输入问题后按回车发送
  - Agent会分析您的问题并生成研究报告
  - 可以使用中文或英文提问
    """
    ui.print(help_text)


def _print_history(ui: TerminalUI, history: HistoryManager) -> None:
    """打印历史记录。"""
    entries = history.get_recent(10)
    if not entries:
        ui.print_info("暂无历史记录")
        return

    ui.print_header("最近的历史记录")
    for i, entry in enumerate(entries, 1):
        ui.print(f"{i}. [{entry.timestamp[:19]}] {entry.user_input[:50]}...")


def _search_history(ui: TerminalUI, history: HistoryManager, keyword: str) -> None:
    """搜索历史记录。"""
    if not keyword:
        ui.print_warning("请输入搜索关键词")
        return

    entries = history.search(keyword)
    if not entries:
        ui.print_info(f"未找到包含 '{keyword}' 的历史记录")
        return

    ui.print_header(f"搜索结果: '{keyword}'")
    for i, entry in enumerate(entries[:10], 1):
        ui.print(f"{i}. [{entry.timestamp[:19]}] {entry.user_input[:50]}...")


async def single_query(
    query: str,
    config: CLIConfig | None = None,
) -> str:
    """单次查询模式。

    Args:
        query: 查询内容
        config: CLI配置

    Returns:
        查询结果
    """
    if config is None:
        config = get_cli_config()

    ui = create_ui(theme=config.theme)

    messages = [HumanMessage(content=query)]

    with ui.spinner("处理中"):
        messages = await call_agent(messages=messages, config=config, ui=ui)

    if messages and isinstance(messages[-1], AIMessage):
        return messages[-1].content

    return ""


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="deepresearch",
        description="iFlytek DeepResearch - 智能深度研究助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                           # 启动交互式模式
  %(prog)s -q "人工智能的发展趋势"    # 单次查询模式
  %(prog)s --depth 5                 # 设置搜索深度为5
  %(prog)s --no-html                 # 不保存HTML报告
  %(prog)s --config-dir /path/to/config    # 使用自定义配置目录

环境变量:
  DEEPRESEARCH_MAX_DEPTH      - 默认搜索深度 (默认: 3)
  DEEPRESEARCH_SAVE_AS_HTML   - 是否保存HTML (默认: true)
  DEEPRESEARCH_SAVE_PATH      - 报告保存路径 (默认: ./example/report)
  DEEPRESEARCH_LOG_LEVEL      - 日志级别 (默认: INFO)
  DEEPRESEARCH_LOG_FILE       - 日志文件路径
  DEEPRESEARCH_THEME          - 界面主题 (default/minimal/colorful)
  DEEPRESEARCH_CONFIG_DIR     - 配置文件夹路径
        """,
    )

    parser.add_argument(
        "-q", "--query",
        type=str,
        help="单次查询模式，直接输入问题并获取答案",
    )

    parser.add_argument(
        "-d", "--depth",
        type=int,
        default=None,
        metavar="N",
        help="搜索深度 (1-10, 默认: 3)",
    )

    parser.add_argument(
        "--no-html",
        action="store_true",
        help="不保存HTML格式的报告",
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        metavar="PATH",
        help="报告输出路径",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="日志级别",
    )

    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        metavar="PATH",
        help="日志文件路径",
    )

    parser.add_argument(
        "--theme",
        type=str,
        choices=["default", "minimal", "colorful"],
        default=None,
        help="界面主题样式",
    )

    parser.add_argument(
        "-c", "--config-dir",
        type=str,
        default=None,
        metavar="PATH",
        help="指定配置文件夹路径",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.1.1",
    )

    return parser


def main(args: List[str] | None = None) -> int:
    """CLI入口函数。

    Args:
        args: 命令行参数列表

    Returns:
        退出码
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # 验证并处理配置目录参数
    config_dir = None
    if parsed_args.config_dir:
        try:
            config_dir = validate_config_dir(parsed_args.config_dir)
            # 设置配置管理器的自定义配置目录
            config_manager.set_config_dir(config_dir)
            # 清除 LLM 配置缓存，确保重新加载配置
            reload_llm_configs()
            logger.debug(f"使用自定义配置目录: {config_dir}")
        except ConfigurationError:
            raise

    # 构建配置
    try:
        config = get_cli_config(
            max_depth=parsed_args.depth,
            save_as_html=not parsed_args.no_html if parsed_args.no_html else None,
            save_path=parsed_args.output,
            log_level=parsed_args.log_level,
            config_dir=str(config_dir) if config_dir else None,
        )

        # 覆盖主题设置
        if parsed_args.theme:
            config = CLIConfig(
                **{
                    **{k: getattr(config, k) for k in CLIConfig.__dataclass_fields__},
                    "theme": parsed_args.theme,
                }
            )

        # 覆盖日志文件设置
        if parsed_args.log_file:
            config = CLIConfig(
                **{
                    **{k: getattr(config, k) for k in CLIConfig.__dataclass_fields__},
                    "log_file": parsed_args.log_file,
                }
            )

    except ConfigurationError as e:
        print(f"配置错误: {e}", file=sys.stderr)
        return e.exit_code
    except Exception as e:
        print(f"初始化失败: {e}", file=sys.stderr)
        return 1

    # 配置日志
    configure_logging(
        level=config.log_level,
        log_file=config.log_file,
    )

    logger.info("DeepResearch CLI 启动")

    try:
        if parsed_args.query:
            # 单次查询模式
            result = asyncio.run(single_query(parsed_args.query, config))
            print(result)
            return 0
        else:
            # 交互式模式
            return asyncio.run(interactive_agent(config))

    except KeyboardInterrupt:
        logger.info("用户中断程序")
        print("\n程序已中断", file=sys.stderr)
        return 130
    except CLIError as e:
        logger.error(f"CLI错误: {e}")
        print(f"错误: {e}", file=sys.stderr)
        return e.exit_code
    except Exception as e:
        logger.exception("发生未预期的错误")
        print(f"错误: {e}", file=sys.stderr)
        return 1
