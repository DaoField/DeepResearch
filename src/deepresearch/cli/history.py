# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
命令历史管理模块

提供对话历史记录功能，支持保存、加载和查询历史记录。
"""

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from deepresearch.cli.exceptions import FileOperationError
from deepresearch.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class HistoryEntry:
    """历史记录条目。

    Attributes:
        timestamp: 时间戳，ISO格式字符串
        user_input: 用户输入内容
        response: 系统响应内容
        session_id: 会话ID，可选
    """

    timestamp: str
    user_input: str
    response: str
    session_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HistoryEntry:
        """从字典创建实例。"""
        return cls(
            timestamp=data.get("timestamp", ""),
            user_input=data.get("user_input", ""),
            response=data.get("response", ""),
            session_id=data.get("session_id"),
        )


@dataclass
class HistoryManager:
    """历史记录管理器。

    管理对话历史记录的加载、保存、查询和清理。

    Attributes:
        history_file: 历史记录文件路径，可选
        max_entries: 最大历史记录条目数，默认100
        _entries: 历史记录条目列表，内部使用
        _session_id: 当前会话ID，内部使用
        _loaded: 是否已加载历史记录，内部使用

    Example:
        >>> manager = HistoryManager(history_file=Path("history.json"))
        >>> manager.add_entry("你好", "你好！有什么可以帮助你的？")
        >>> recent = manager.get_recent(5)
    """

    history_file: Path | None = None
    max_entries: int = 100
    _entries: list[HistoryEntry] = field(default_factory=list, repr=False)
    _session_id: str = field(init=False, repr=False)
    _loaded: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        """初始化后处理：生成会话ID并加载历史记录。"""
        object.__setattr__(
            self, "_session_id", datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        if self.history_file:
            self._load_history()

    def _load_history(self) -> None:
        """从文件加载历史记录。"""
        if not self.history_file or not self.history_file.exists():
            return

        try:
            with open(self.history_file, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._entries = [
                        HistoryEntry.from_dict(entry)
                        for entry in data[-self.max_entries :]
                    ]
                    object.__setattr__(self, "_loaded", True)
                    logger.debug(f"已加载 {len(self._entries)} 条历史记录")
        except json.JSONDecodeError as e:
            logger.warning(f"历史文件格式错误: {e}")
        except Exception as e:
            logger.warning(f"加载历史记录失败: {e}")

    def _save_history(self) -> None:
        """保存历史记录到文件。"""
        if not self.history_file:
            return

        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(
                    [entry.to_dict() for entry in self._entries],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            logger.debug(f"已保存 {len(self._entries)} 条历史记录")
        except Exception as e:
            raise FileOperationError(
                f"保存历史记录失败: {e}",
                path=str(self.history_file),
            )

    def add_entry(self, user_input: str, response: str) -> None:
        """添加新的历史记录条目。

        Args:
            user_input: 用户输入
            response: 系统响应
        """
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            response=response,
            session_id=self._session_id,
        )
        self._entries.append(entry)

        # 限制历史记录数量
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

        # 异步保存
        try:
            self._save_history()
        except FileOperationError:
            logger.warning("保存历史记录失败，但不影响正常使用")

    def get_recent(self, count: int = 10) -> list[HistoryEntry]:
        """获取最近的历史记录。

        Args:
            count: 获取数量

        Returns:
            历史记录列表
        """
        return self._entries[-count:] if self._entries else []

    def get_session_history(self, session_id: str | None = None) -> list[HistoryEntry]:
        """获取指定会话的历史记录。

        Args:
            session_id: 会话ID，None表示当前会话

        Returns:
            历史记录列表
        """
        sid = session_id or self._session_id
        return [entry for entry in self._entries if entry.session_id == sid]

    def search(self, keyword: str) -> list[HistoryEntry]:
        """搜索历史记录。

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的历史记录列表
        """
        keyword_lower = keyword.lower()
        return [
            entry
            for entry in self._entries
            if keyword_lower in entry.user_input.lower()
            or keyword_lower in entry.response.lower()
        ]

    def clear(self) -> None:
        """清空历史记录。"""
        self._entries.clear()
        if self.history_file and self.history_file.exists():
            try:
                self.history_file.unlink()
                logger.info("历史记录已清空")
            except Exception as e:
                raise FileOperationError(
                    f"删除历史文件失败: {e}",
                    path=str(self.history_file),
                )

    def get_stats(self) -> dict[str, Any]:
        """获取历史记录统计信息。

        Returns:
            统计信息字典
        """
        if not self._entries:
            return {
                "total_entries": 0,
                "sessions": 0,
                "first_entry": None,
                "last_entry": None,
            }

        sessions = set(entry.session_id for entry in self._entries if entry.session_id)
        return {
            "total_entries": len(self._entries),
            "sessions": len(sessions),
            "first_entry": self._entries[0].timestamp if self._entries else None,
            "last_entry": self._entries[-1].timestamp if self._entries else None,
        }


def get_default_history_path() -> Path:
    """获取默认历史文件路径。

    Returns:
        历史文件路径
    """
    # 优先使用用户目录
    if os.name == "nt":  # Windows
        base_dir = Path(os.environ.get("APPDATA", Path.home()))
    else:  # Unix-like
        base_dir = Path(
            os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        )

    history_dir = base_dir / "deepresearch"
    history_dir.mkdir(parents=True, exist_ok=True)
    return history_dir / "history.json"
