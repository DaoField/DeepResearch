# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

"""
配置基类模块单元测试
"""

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

from deepresearch.config import (
    BaseConfig,
    ConfigError,
    ConfigField,
    ConfigManager,
    ConfigSource,
    ConfigValidator,
    ChoiceValidator,
    RangeValidator,
    TypeValidator,
    ValidationError,
    add_sensitive_key,
    clear_config_cache,
    config_manager,
    get_config_dir,
    load_config,
    load_toml_config,
    redact_config,
    remove_sensitive_key,
)


class MockConfigValidators:
    """测试配置验证器。"""

    def test_range_validator_valid(self):
        """测试范围验证器 - 有效值。"""
        validator = RangeValidator(min_val=0, max_val=100)
        assert validator.validate(50, "test_field") == 50.0
        assert validator.validate(0, "test_field") == 0.0
        assert validator.validate(100, "test_field") == 100.0

    def test_range_validator_invalid_type(self):
        """测试范围验证器 - 无效类型。"""
        validator = RangeValidator(min_val=0, max_val=100)
        with pytest.raises(ValidationError, match="必须是数值类型"):
            validator.validate("not_a_number", "test_field")

    def test_range_validator_out_of_range(self):
        """测试范围验证器 - 超出范围。"""
        validator = RangeValidator(min_val=0, max_val=100)
        with pytest.raises(ValidationError, match="不能小于"):
            validator.validate(-1, "test_field")
        with pytest.raises(ValidationError, match="不能大于"):
            validator.validate(101, "test_field")

    def test_range_validator_only_min(self):
        """测试范围验证器 - 仅最小值。"""
        validator = RangeValidator(min_val=0)
        assert validator.validate(1000, "test_field") == 1000.0
        with pytest.raises(ValidationError):
            validator.validate(-1, "test_field")

    def test_range_validator_only_max(self):
        """测试范围验证器 - 仅最大值。"""
        validator = RangeValidator(max_val=100)
        assert validator.validate(-1000, "test_field") == -1000.0
        with pytest.raises(ValidationError):
            validator.validate(101, "test_field")

    def test_choice_validator_valid(self):
        """测试选项验证器 - 有效值。"""
        validator = ChoiceValidator({"a", "b", "c"})
        assert validator.validate("a", "test_field") == "a"
        assert validator.validate("B", "test_field") == "b"  # 大小写不敏感

    def test_choice_validator_invalid(self):
        """测试选项验证器 - 无效值。"""
        validator = ChoiceValidator({"a", "b", "c"})
        with pytest.raises(ValidationError, match="必须是以下值之一"):
            validator.validate("d", "test_field")

    def test_type_validator_valid(self):
        """测试类型验证器 - 有效值。"""
        validator = TypeValidator(int)
        assert validator.validate(42, "test_field") == 42
        assert validator.validate("42", "test_field") == 42

    def test_type_validator_invalid(self):
        """测试类型验证器 - 无效值。"""
        validator = TypeValidator(int)
        with pytest.raises(ValidationError, match="必须是 int 类型"):
            validator.validate("not_an_int", "test_field")


@dataclass
class MockConfig(BaseConfig):
    """测试配置类。"""
    name: str = "default"
    timeout: int = 30
    retries: int = 3
    enabled: bool = True


@dataclass
class ValidatedConfig(BaseConfig):
    """带验证的配置类。"""
    port: int = 8080
    host: str = "localhost"

    def __post_init__(self):
        # 手动验证
        if self.port < 1 or self.port > 65535:
            raise ValidationError(f"port 必须在 1-65535 之间，当前值: {self.port}")
        super().__post_init__()


class TestBaseConfig:
    """测试 BaseConfig 基类。"""

    def test_default_values(self):
        """测试默认值。"""
        config = MockConfig()
        assert config.name == "default"
        assert config.timeout == 30
        assert config.retries == 3
        assert config.enabled is True

    def test_from_dict(self):
        """测试从字典创建。"""
        config = MockConfig.from_dict({"name": "test", "timeout": 60})
        assert config.name == "test"
        assert config.timeout == 60
        assert config.retries == 3  # 使用默认值

    def test_from_dict_ignores_invalid_fields(self):
        """测试从字典创建时忽略无效字段。"""
        config = MockConfig.from_dict({"name": "test", "invalid_field": "value"})
        assert config.name == "test"
        assert not hasattr(config, "invalid_field")

    def test_to_dict(self):
        """测试转换为字典。"""
        config = MockConfig(name="test", timeout=60)
        config_dict = config.to_dict()
        assert config_dict == {"name": "test", "timeout": 60, "retries": 3, "enabled": True}

    def test_to_dict_with_redact(self):
        """测试脱敏转换。"""
        @dataclass
        class SensitiveConfig(BaseConfig):
            api_key: str = "secret123"
            normal_field: str = "value"

        config = SensitiveConfig()
        config_dict = config.to_dict(redact=True)
        assert config_dict["api_key"] == "***"
        assert config_dict["normal_field"] == "value"

    def test_merge(self):
        """测试配置合并。"""
        config1 = MockConfig(name="base", timeout=30)
        config2 = MockConfig(name="override", timeout=60)
        merged = config1.merge(config2)

        assert merged.name == "override"
        assert merged.timeout == 60
        assert merged.retries == 3

    def test_merge_preserves_original(self):
        """测试合并不修改原始配置。"""
        config1 = MockConfig(name="base")
        config2 = MockConfig(name="override")
        merged = config1.merge(config2)

        assert config1.name == "base"
        assert config2.name == "override"
        assert merged.name == "override"

    def test_get(self):
        """测试 get 方法。"""
        config = MockConfig(name="test")
        assert config.get("name") == "test"
        assert config.get("timeout") == 30
        assert config.get("nonexistent", "default") == "default"

    def test_set(self):
        """测试 set 方法。"""
        config = MockConfig()
        config.set("name", "new_name")
        assert config.name == "new_name"

    def test_set_private_field_ignored(self):
        """测试 set 方法忽略私有字段。"""
        config = MockConfig()
        config.set("_private", "value")  # 不应抛出异常

    def test_validation_error(self):
        """测试验证错误。"""
        with pytest.raises(ValidationError):
            ValidatedConfig(port=70000)


class TestConfigFromEnv:
    """测试从环境变量加载配置。"""

    def test_from_env_basic(self, monkeypatch):
        """测试基本环境变量加载。"""
        monkeypatch.setenv("DEEPRESEARCH_NAME", "env_name")
        monkeypatch.setenv("DEEPRESEARCH_TIMEOUT", "120")

        config = MockConfig.from_env()
        assert config.name == "env_name"
        assert config.timeout == 120

    def test_from_env_boolean(self, monkeypatch):
        """测试布尔值环境变量。"""
        monkeypatch.setenv("DEEPRESEARCH_ENABLED", "false")

        config = MockConfig.from_env()
        assert config.enabled is False

    def test_from_env_boolean_variations(self, monkeypatch):
        """测试布尔值环境变量变体。"""
        # 测试各种 true 值
        for val in ["true", "1", "yes"]:
            monkeypatch.setenv("DEEPRESEARCH_ENABLED", val)
            config = MockConfig.from_env()
            assert config.enabled is True, f"Failed for value: {val}"

        # 测试各种 false 值
        for val in ["false", "0", "no"]:
            monkeypatch.setenv("DEEPRESEARCH_ENABLED", val)
            config = MockConfig.from_env()
            assert config.enabled is False, f"Failed for value: {val}"

    def test_from_env_no_matching_vars(self, monkeypatch):
        """测试无匹配环境变量。"""
        # 清除可能的环境变量
        for key in list(os.environ.keys()):
            if key.startswith("DEEPRESEARCH_"):
                monkeypatch.delenv(key, raising=False)

        config = MockConfig.from_env()
        assert config.name == "default"
        assert config.timeout == 30


class TestConfigFromFile:
    """测试从文件加载配置。"""

    def test_from_file_toml(self, tmp_path):
        """测试从 TOML 文件加载。"""
        config_file = tmp_path / "test_config.toml"
        config_file.write_text("""
name = "file_name"
timeout = 90
retries = 5
enabled = false
""")

        config = MockConfig.from_file(config_file)
        assert config.name == "file_name"
        assert config.timeout == 90
        assert config.retries == 5
        assert config.enabled is False

    def test_from_file_not_found(self):
        """测试文件不存在。"""
        with pytest.raises(ConfigError):
            MockConfig.from_file("/nonexistent/path/config.toml")

    def test_from_file_invalid_toml(self, tmp_path):
        """测试无效 TOML 文件。"""
        config_file = tmp_path / "invalid.toml"
        config_file.write_text("invalid toml content {{{")

        with pytest.raises(ConfigError):
            MockConfig.from_file(config_file)


class TestConfigManager:
    """测试配置管理器。"""

    def setup_method(self):
        """每个测试方法前重置配置管理器。"""
        clear_config_cache()
        config_manager._configs.clear()
        config_manager._loaders.clear()
        config_manager._custom_config_dir = None

    def test_set_config_dir(self, tmp_path):
        """测试设置自定义配置目录。"""
        custom_dir = tmp_path / "custom_config"
        custom_dir.mkdir()

        config_manager.set_config_dir(custom_dir)
        assert config_manager.get_config_dir() == custom_dir

    def test_set_config_dir_string(self, tmp_path):
        """测试设置配置目录（字符串路径）。"""
        custom_dir = tmp_path / "custom_config"
        custom_dir.mkdir()

        config_manager.set_config_dir(str(custom_dir))
        assert config_manager.get_config_dir() == custom_dir

    def test_get_config_dir_env(self, monkeypatch, tmp_path):
        """测试从环境变量获取配置目录。"""
        custom_dir = tmp_path / "env_config"
        custom_dir.mkdir()

        monkeypatch.setenv("DEEPRESEARCH_CONFIG_DIR", str(custom_dir))
        # 重置自定义目录
        config_manager._custom_config_dir = None

        assert config_manager.get_config_dir() == custom_dir

    def test_register_and_load(self):
        """测试注册和加载配置。"""
        def loader():
            return MockConfig(name="loaded")

        config_manager.register_loader("test", loader)
        config = config_manager.load("test")

        assert config.name == "loaded"

    def test_load_caches_result(self):
        """测试加载结果缓存。"""
        call_count = 0

        def loader():
            nonlocal call_count
            call_count += 1
            return MockConfig(name=f"call_{call_count}")

        config_manager.register_loader("cached", loader)

        config1 = config_manager.load("cached")
        config2 = config_manager.load("cached")

        assert config1.name == "call_1"
        assert config2.name == "call_1"  # 缓存的值
        assert call_count == 1

    def test_reload_clears_cache(self):
        """测试重新加载清除缓存。"""
        call_count = 0

        def loader():
            nonlocal call_count
            call_count += 1
            return MockConfig(name=f"call_{call_count}")

        config_manager.register_loader("reloadable", loader)

        config1 = config_manager.load("reloadable")
        config_manager.reload("reloadable")
        config2 = config_manager.load("reloadable")

        assert config1.name == "call_1"
        assert config2.name == "call_2"
        assert call_count == 2

    def test_reload_all(self):
        """测试重新加载所有配置。"""
        config_manager._configs["test1"] = MockConfig(name="test1")
        config_manager._configs["test2"] = MockConfig(name="test2")

        config_manager.reload()

        assert len(config_manager._configs) == 0

    def test_load_unregistered_raises(self):
        """测试加载未注册配置抛出异常。"""
        with pytest.raises(ConfigError, match="未找到配置"):
            config_manager.load("unregistered")


class TestLoadConfigFunction:
    """测试 load_config 便捷函数。"""

    def setup_method(self):
        """每个测试方法前清理。"""
        clear_config_cache()

    def test_load_config_defaults(self):
        """测试加载默认配置。"""
        config = load_config(MockConfig, use_env=False, use_file=False)
        assert config.name == "default"
        assert config.timeout == 30

    def test_load_config_with_env(self, monkeypatch):
        """测试从环境变量加载。"""
        monkeypatch.setenv("DEEPRESEARCH_TIMEOUT", "200")

        config = load_config(MockConfig, use_env=True, use_file=False)
        assert config.timeout == 200

    def test_load_config_with_file(self, tmp_path, monkeypatch):
        """测试从文件加载。"""
        # 设置临时配置目录
        config_manager._custom_config_dir = tmp_path

        config_file = tmp_path / "test_config.toml"
        config_file.write_text("name = \"from_file\"\ntimeout = 150")

        config = load_config(MockConfig, filename="test_config.toml", use_env=False, use_file=True)
        assert config.name == "from_file"
        assert config.timeout == 150

    def test_load_config_priority_env_over_file(self, tmp_path, monkeypatch):
        """测试优先级：环境变量 > 配置文件。"""
        config_manager._custom_config_dir = tmp_path

        config_file = tmp_path / "test_config.toml"
        config_file.write_text("timeout = 100")

        monkeypatch.setenv("DEEPRESEARCH_TIMEOUT", "250")

        config = load_config(MockConfig, filename="test_config.toml", use_env=True, use_file=True)
        assert config.timeout == 250  # 环境变量优先级更高

    def test_load_config_custom_prefix(self, monkeypatch):
        """测试自定义环境变量前缀。"""
        monkeypatch.setenv("CUSTOM_PREFIX_TIMEOUT", "300")

        config = load_config(
            MockConfig,
            use_env=True,
            use_file=False,
            env_prefix="CUSTOM_PREFIX_"
        )
        assert config.timeout == 300


class TestBackwardCompatibility:
    """测试向后兼容性。"""

    def setup_method(self):
        """每个测试方法前重置配置管理器。"""
        clear_config_cache()
        config_manager._custom_config_dir = None

    def test_get_config_dir(self):
        """测试 get_config_dir 函数。"""
        config_dir = get_config_dir()
        assert isinstance(config_dir, Path)
        assert config_dir.exists()
        assert config_dir.name == "config"

    def test_load_toml_config(self):
        """测试 load_toml_config 函数。"""
        workflow = load_toml_config("workflow.toml")
        assert isinstance(workflow, dict)
        assert "search" in workflow

    def test_redact_config(self):
        """测试 redact_config 函数。"""
        config = {
            "api_key": "secret123",
            "password": "mypassword",
            "normal": "value"
        }
        redacted = redact_config(config)
        assert redacted["api_key"] == "***"
        assert redacted["password"] == "***"
        assert redacted["normal"] == "value"

    def test_redact_config_custom_keys(self):
        """测试自定义敏感键脱敏。"""
        config = {
            "custom_secret": "secret123",
            "normal": "value"
        }
        redacted = redact_config(config, sensitive_keys={"custom_secret"})
        assert redacted["custom_secret"] == "***"
        assert redacted["normal"] == "value"

    def test_clear_config_cache(self):
        """测试 clear_config_cache 函数。"""
        # 先加载一些配置
        load_toml_config("workflow.toml")

        # 清除缓存不应抛出异常
        clear_config_cache()

    def test_add_remove_sensitive_key(self):
        """测试添加和移除敏感键。"""
        add_sensitive_key("custom_key")

        config = {"custom_key": "secret"}
        redacted = redact_config(config)
        assert redacted["custom_key"] == "***"

        remove_sensitive_key("custom_key")

        # 移除后不应再脱敏
        redacted = redact_config(config)
        assert redacted["custom_key"] == "secret"


class TestConfigSource:
    """测试配置来源枚举。"""

    def test_config_source_values(self):
        """测试配置来源值。"""
        assert ConfigSource.DEFAULT.value == "default"
        assert ConfigSource.FILE.value == "file"
        assert ConfigSource.ENV.value == "env"
        assert ConfigSource.CODE.value == "code"


class TestConfigField:
    """测试 ConfigField 类。"""

    def test_config_field_defaults(self):
        """测试 ConfigField 默认值。"""
        field = ConfigField()
        assert field.default is None
        assert field.validators == []
        assert field.env_var is None
        assert field.sensitive is False
        assert field.description == ""

    def test_config_field_custom(self):
        """测试 ConfigField 自定义值。"""
        validator = RangeValidator(min_val=0, max_val=100)
        field = ConfigField(
            default=50,
            validators=[validator],
            env_var="CUSTOM_VAR",
            sensitive=True,
            description="Test field"
        )
        assert field.default == 50
        assert field.validators == [validator]
        assert field.env_var == "CUSTOM_VAR"
        assert field.sensitive is True
        assert field.description == "Test field"
