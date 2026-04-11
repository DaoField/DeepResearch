# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

import os
import tomllib
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field, fields, replace
from enum import Enum
from functools import lru_cache
from pathlib import Path
from threading import Thread
from typing import Any, ClassVar, Optional, TypeVar

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object


class ConfigError(Exception):
    """配置加载错误。"""

    pass


class ValidationError(ConfigError):
    """配置验证错误。"""

    pass


class ConfigSource(Enum):
    """配置来源枚举。"""

    DEFAULT = "default"
    FILE = "file"
    ENV = "env"
    CODE = "code"


ConfigT = TypeVar("ConfigT", bound="BaseConfig")
T = TypeVar("T")


# Metadata 键名常量
META_VALIDATORS = "validators"
META_ENV_VAR = "env_var"
META_SENSITIVE = "sensitive"
META_DESCRIPTION = "description"


@dataclass
class ConfigValue:
    """配置值包装类，记录配置来源和元数据（向后兼容）。"""

    value: T
    source: ConfigSource = ConfigSource.DEFAULT
    metadata: dict[str, Any] = field(default_factory=dict)


def _clone_toml_value(value: Any) -> Any:
    """深拷贝 TOML 配置值。"""
    if isinstance(value, dict):
        return {k: _clone_toml_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clone_toml_value(v) for v in value]
    return value


class ConfigValidator(ABC):
    """配置验证器抽象基类。"""

    @abstractmethod
    def validate(self, value: Any, field_name: str) -> Any:
        """验证并可能转换值。

        Args:
            value: 待验证的值
            field_name: 字段名称

        Returns:
            验证后的值

        Raises:
            ValidationError: 验证失败时抛出
        """
        pass


@dataclass
class ConfigField:
    """配置字段定义（向后兼容，建议使用 config_field 函数）。"""

    default: Any = None
    validators: list[ConfigValidator] = field(default_factory=list)
    env_var: str | None = None
    sensitive: bool = False
    description: str = ""


@dataclass(frozen=True)
class RangeValidator(ConfigValidator):
    """范围验证器。"""

    min_val: int | float | None = None
    max_val: int | float | None = None

    def validate(self, value: Any, field_name: str) -> Any:
        try:
            num_val = float(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"字段 '{field_name}' 必须是数值类型") from exc

        if self.min_val is not None and num_val < self.min_val:
            raise ValidationError(f"字段 '{field_name}' 不能小于 {self.min_val}")
        if self.max_val is not None and num_val > self.max_val:
            raise ValidationError(f"字段 '{field_name}' 不能大于 {self.max_val}")

        return num_val


@dataclass(frozen=True)
class ChoiceValidator(ConfigValidator):
    """选项验证器。"""

    choices: frozenset[str] = field(default_factory=frozenset)

    def __init__(self, choices: set[str] | frozenset[str] | list[str]):
        object.__setattr__(self, "choices", frozenset(c.lower() for c in choices))

    def validate(self, value: Any, field_name: str) -> Any:
        str_val = str(value).lower()
        if str_val not in self.choices:
            raise ValidationError(
                f"字段 '{field_name}' 必须是以下值之一: {set(self.choices)}"
            )
        return str_val


@dataclass(frozen=True)
class TypeValidator(ConfigValidator):
    """类型验证器。"""

    expected_type: type = field(default=object)

    def validate(self, value: Any, field_name: str) -> Any:
        if not isinstance(value, self.expected_type):
            try:
                return self.expected_type(value)
            except (TypeError, ValueError) as exc:
                raise ValidationError(
                    f"字段 '{field_name}' 必须是 {self.expected_type.__name__} 类型"
                ) from exc
        return value


def config_field(
    default: Any = None,
    default_factory: Callable[[], Any] | None = None,
    validators: list[ConfigValidator] | None = None,
    env_var: str | None = None,
    sensitive: bool = False,
    description: str = "",
) -> Any:
    """创建配置字段，支持验证器和元数据。

    Args:
        default: 默认值
        default_factory: 默认工厂函数
        validators: 验证器列表
        env_var: 环境变量名
        sensitive: 是否为敏感字段
        description: 字段描述

    Returns:
        dataclass field
    """
    metadata = {
        META_VALIDATORS: validators or [],
        META_ENV_VAR: env_var,
        META_SENSITIVE: sensitive,
        META_DESCRIPTION: description,
    }

    if default_factory is not None:
        return field(default_factory=default_factory, metadata=metadata)
    return field(default=default, metadata=metadata)


# 模块级别的敏感键集合，支持动态修改
_DEFAULT_SENSITIVE_KEYS: set[str] = {"api_key", "password", "secret", "token"}


@dataclass
class BaseConfig:
    """配置基类，提供统一的配置管理功能。"""

    _env_prefix: ClassVar[str] = "DEEPRESEARCH_"
    _config_dir_env: ClassVar[str] = "DEEPRESEARCH_CONFIG_DIR"

    @property
    def _sensitive_keys(self) -> set[str]:
        """获取敏感键集合。"""
        return _DEFAULT_SENSITIVE_KEYS

    def __post_init__(self) -> None:
        """初始化后验证所有字段。"""
        self._validate_all_fields()

    def _validate_all_fields(self) -> None:
        """验证所有字段。"""
        for f in fields(self):
            if f.name.startswith("_"):
                continue

            value = getattr(self, f.name)
            validators = f.metadata.get(META_VALIDATORS, [])

            for validator in validators:
                try:
                    value = validator.validate(value, f.name)
                except ValidationError:
                    raise

            # 使用 object.__setattr__ 避免触发 __setattr__ 限制
            object.__setattr__(self, f.name, value)

    @classmethod
    def from_dict(
        cls: type[ConfigT],
        data: dict[str, Any],
        source: ConfigSource = ConfigSource.CODE,
    ) -> ConfigT:
        """从字典创建配置实例。

        Args:
            data: 配置数据字典
            source: 配置来源

        Returns:
            配置实例
        """
        field_names = {f.name for f in fields(cls)}
        valid_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**valid_data)

    @classmethod
    def from_env(cls: type[ConfigT]) -> ConfigT:
        """从环境变量加载配置。

        Returns:
            配置实例
        """
        env_data: dict[str, Any] = {}

        for f in fields(cls):
            if f.name.startswith("_"):
                continue

            env_var_name = f.metadata.get(META_ENV_VAR)
            if env_var_name is None:
                env_var_name = f"{cls._env_prefix}{f.name.upper()}"

            env_value = os.getenv(env_var_name)
            if env_value is None:
                continue

            # 尝试解析布尔值
            lower_val = env_value.lower()
            if lower_val in ("true", "1", "yes"):
                env_data[f.name] = True
            elif lower_val in ("false", "0", "no"):
                env_data[f.name] = False
            else:
                # 尝试解析为整数
                try:
                    env_data[f.name] = int(env_value)
                except ValueError:
                    env_data[f.name] = env_value

        return cls.from_dict(env_data, ConfigSource.ENV)

    @classmethod
    def from_file(cls: type[ConfigT], filepath: Path | str) -> ConfigT:
        """从文件加载配置。

        Args:
            filepath: 配置文件路径

        Returns:
            配置实例
        """
        path = Path(filepath).expanduser().resolve()
        data = _load_toml_table_from_path(str(path))
        return cls.from_dict(data, ConfigSource.FILE)

    def merge(
        self: ConfigT, other: ConfigT, source: ConfigSource = ConfigSource.CODE
    ) -> ConfigT:
        """合并另一个配置实例的值（other 优先级更高）。

        Args:
            other: 另一个配置实例
            source: 合并来源

        Returns:
            新的合并后的配置实例
        """
        changes: dict[str, Any] = {}

        for f in fields(self):
            if f.name.startswith("_"):
                continue

            other_value = getattr(other, f.name, None)
            self_value = getattr(self, f.name, None)

            # 使用 other 的非默认值
            if other_value is not None and other_value != f.default:
                changes[f.name] = other_value
            else:
                changes[f.name] = self_value

        return replace(self, **changes)

    def to_dict(self, redact: bool = False) -> dict[str, Any]:
        """转换为字典。

        Args:
            redact: 是否脱敏敏感字段

        Returns:
            配置字典
        """
        result: dict[str, Any] = {}

        for f in fields(self):
            if f.name.startswith("_"):
                continue

            value = getattr(self, f.name)

            # 检查是否为敏感字段
            is_sensitive = False
            if redact:
                if f.metadata.get(META_SENSITIVE, False):
                    is_sensitive = True
                elif any(sk in f.name.lower() for sk in self._sensitive_keys):
                    is_sensitive = True

            result[f.name] = "***" if is_sensitive else value

        return result

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项值。

        Args:
            key: 配置项名称
            default: 默认值

        Returns:
            配置项值
        """
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """设置配置项值（仅对非 frozen 实例有效）。

        Args:
            key: 配置项名称
            value: 配置项值
        """
        if hasattr(self, key) and not key.startswith("_"):
            setattr(self, key, value)


@dataclass
class ConfigManager:
    """配置管理器，提供统一的配置加载和管理接口。"""

    _configs: dict[str, BaseConfig] = field(default_factory=dict, repr=False)
    _loaders: dict[str, Callable[[], BaseConfig]] = field(
        default_factory=dict, repr=False
    )
    _custom_config_dir: Path | None = field(default=None, repr=False)
    _observer: Optional[Observer] = field(default=None, repr=False)
    _watching: bool = field(default=False, repr=False)
    _reload_callbacks: list[Callable[[], None]] = field(
        default_factory=list, repr=False
    )

    def set_config_dir(self, config_dir: Path | str) -> None:
        """设置自定义配置目录。

        Args:
            config_dir: 配置目录路径
        """
        self._custom_config_dir = Path(config_dir).expanduser().resolve()
        clear_config_cache()

    def get_config_dir(self) -> Path:
        """获取项目配置目录路径。

        Returns:
            配置目录路径
        """
        # 优先使用自定义配置目录
        if self._custom_config_dir is not None:
            return self._custom_config_dir

        # 其次使用环境变量
        env_dir = os.getenv(BaseConfig._config_dir_env)
        if env_dir:
            return Path(env_dir).expanduser().resolve()

        # 然后检测项目根目录/.config 用户配置目录
        root_user_config = Path(__file__).parents[3] / ".config"
        if root_user_config.exists() and root_user_config.is_dir():
            return root_user_config.resolve()

        # 最后使用默认项目相对路径
        return Path(__file__).parents[3] / "config"

    def register_loader(self, name: str, loader: Callable[[], BaseConfig]) -> None:
        """注册配置加载器。

        Args:
            name: 配置名称
            loader: 加载器函数
        """
        self._loaders[name] = loader

    def load(self, name: str) -> BaseConfig:
        """加载指定配置。

        Args:
            name: 配置名称

        Returns:
            配置实例

        Raises:
            ConfigError: 配置未注册时抛出
        """
        if name not in self._configs:
            if name not in self._loaders:
                raise ConfigError(f"未找到配置 '{name}' 的加载器")
            self._configs[name] = self._loaders[name]()
        return self._configs[name]

    def register_reload_callback(self, callback: Callable[[], None]) -> None:
        """注册配置重新加载回调。

        Args:
            callback: 配置重新加载时要调用的回调函数
        """
        if callback not in self._reload_callbacks:
            self._reload_callbacks.append(callback)

    def unregister_reload_callback(self, callback: Callable[[], None]) -> None:
        """取消注册配置重新加载回调。

        Args:
            callback: 要取消注册的回调函数
        """
        if callback in self._reload_callbacks:
            self._reload_callbacks.remove(callback)

    def reload(self, name: str | None = None) -> None:
        """重新加载配置。

        Args:
            name: 配置名称，为 None 时重新加载所有配置
        """
        clear_config_cache()

        if name is None:
            self._configs.clear()
        elif name in self._configs:
            del self._configs[name]

        for callback in self._reload_callbacks:
            try:
                callback()
            except Exception:
                pass

    def get(self, name: str) -> BaseConfig:
        """获取配置（同 load）。"""
        return self.load(name)

    def start_watching(self) -> None:
        """启动配置文件变更监听。

        如果 watchdog 库不可用，则静默跳过。
        """
        if not WATCHDOG_AVAILABLE:
            return

        if self._watching:
            return

        config_dir = self.get_config_dir()
        if not config_dir.exists():
            return

        class ConfigChangeHandler(FileSystemEventHandler):
            """处理配置文件变更事件。"""

            def __init__(self, manager: ConfigManager):
                self.manager = manager
                self._debounce_timer: Optional[Thread] = None

            def _on_change(self) -> None:
                """延迟处理变更，避免频繁触发。"""
                self.manager.reload()

            def on_any_event(self, event):
                """处理任何文件系统事件。"""
                if event.is_directory:
                    return

                if not event.src_path.endswith(".toml"):
                    return

                if self._debounce_timer and self._debounce_timer.is_alive():
                    self._debounce_timer.join(timeout=1.0)

                self._debounce_timer = Thread(target=self._on_change, daemon=True)
                self._debounce_timer.start()

        self._observer = Observer()
        handler = ConfigChangeHandler(self)
        self._observer.schedule(handler, str(config_dir), recursive=False)
        self._observer.start()
        self._watching = True

    def stop_watching(self) -> None:
        """停止配置文件变更监听。"""
        if self._observer and self._watching:
            self._observer.stop()
            self._observer.join()
            self._watching = False

    def is_watching(self) -> bool:
        """检查是否正在监听配置变更。

        Returns:
            是否正在监听
        """
        return self._watching

    def __del__(self):
        """析构时停止观察者。"""
        self.stop_watching()


# 全局配置管理器实例
config_manager = ConfigManager()


@lru_cache(maxsize=16)
def _load_toml_table_from_path(resolved_path: str) -> dict[str, Any]:
    """从文件路径加载 TOML 配置（带缓存）。"""
    try:
        with Path(resolved_path).open("rb") as file_handle:
            data = tomllib.load(file_handle)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"配置文件解析失败：{resolved_path}") from exc
    except OSError as exc:
        raise ConfigError(f"无法读取配置文件：{resolved_path}") from exc
    if not isinstance(data, dict):
        raise ConfigError("配置文件必须解析为 TOML table")
    return data


__all__ = [
    "ConfigError",
    "ValidationError",
    "ConfigSource",
    "ConfigValue",
    "ConfigValidator",
    "ConfigField",
    "RangeValidator",
    "ChoiceValidator",
    "TypeValidator",
    "config_field",
    "BaseConfig",
    "ConfigManager",
    "config_manager",
    "get_config_dir",
    "load_toml_config",
    "redact_config",
    "clear_config_cache",
    "add_sensitive_key",
    "remove_sensitive_key",
    "load_config",
    "start_watching",
    "stop_watching",
    "WATCHDOG_AVAILABLE",
]

WATCHDOG_AVAILABLE = WATCHDOG_AVAILABLE


def get_config_dir() -> Path:
    """获取项目配置目录路径（向后兼容）。"""
    return config_manager.get_config_dir()


def start_watching() -> None:
    """启动配置文件变更监听（便捷函数）。"""
    config_manager.start_watching()


def stop_watching() -> None:
    """停止配置文件变更监听（便捷函数）。"""
    config_manager.stop_watching()


def load_toml_config(config_filename: str) -> dict[str, Any]:
    """加载 TOML 配置文件（返回深拷贝，向后兼容）。"""
    config_path = get_config_dir() / config_filename
    path = config_path.expanduser().resolve()
    data = _load_toml_table_from_path(str(path))
    return _clone_toml_value(data)


def redact_config(
    config: dict[str, Any], sensitive_keys: set[str] | None = None
) -> dict[str, Any]:
    """脱敏配置，隐藏敏感字段。

    Args:
        config: 配置字典
        sensitive_keys: 自定义敏感字段集合，为 None 时使用默认集合

    Returns:
        脱敏后的配置字典
    """
    cloned: dict[str, Any] = _clone_toml_value(config)
    keys_to_redact = sensitive_keys or _DEFAULT_SENSITIVE_KEYS

    def _redact_dict(d: dict[str, Any]) -> None:
        for k, v in d.items():
            if isinstance(v, dict):
                _redact_dict(v)
            elif any(sk in k.lower() for sk in keys_to_redact):
                d[k] = "***"

    _redact_dict(cloned)
    return cloned


def clear_config_cache() -> None:
    """清理配置读取缓存（用于测试或动态更新配置文件的场景）。"""
    _load_toml_table_from_path.cache_clear()


def add_sensitive_key(key: str) -> None:
    """添加敏感字段。

    Args:
        key: 敏感字段名称
    """
    _DEFAULT_SENSITIVE_KEYS.add(key.lower())


def remove_sensitive_key(key: str) -> None:
    """移除敏感字段。

    Args:
        key: 敏感字段名称
    """
    _DEFAULT_SENSITIVE_KEYS.discard(key.lower())


def load_config(
    config_class: type[ConfigT],
    filename: str | None = None,
    env_prefix: str | None = None,
    use_env: bool = True,
    use_file: bool = True,
) -> ConfigT:
    """加载配置的便捷函数，支持多层级配置覆盖。

    配置优先级（高到低）：
    1. 代码传入的参数
    2. 环境变量
    3. 配置文件
    4. 默认值

    Args:
        config_class: 配置类
        filename: 配置文件名，为 None 时不从文件加载
        env_prefix: 环境变量前缀，为 None 时使用类默认值
        use_env: 是否从环境变量加载
        use_file: 是否从文件加载

    Returns:
        配置实例
    """
    original_prefix = config_class._env_prefix

    try:
        if env_prefix:
            config_class._env_prefix = env_prefix

        # 从默认值开始
        config = config_class()

        # 从文件加载
        if use_file and filename:
            try:
                file_config = config_class.from_file(get_config_dir() / filename)
                config = config.merge(file_config, ConfigSource.FILE)
            except ConfigError | FileNotFoundError:
                pass  # 文件不存在时使用默认值

        # 从环境变量加载
        if use_env:
            try:
                env_config = config_class.from_env()
                config = config.merge(env_config, ConfigSource.ENV)
            except ValidationError:
                raise

        return config

    finally:
        config_class._env_prefix = original_prefix
