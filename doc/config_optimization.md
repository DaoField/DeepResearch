# 配置模块优化说明文档

## 概述

本文档详细说明了 `deepresearch.config.base` 模块的灵活性优化方案，包括设计思路、新增功能、使用方法以及向后兼容性保证。

## 优化目标

1. **消除硬编码**：配置目录、敏感字段等不再硬编码
2. **增强可扩展性**：引入配置基类和验证器机制
3. **支持多层级配置**：环境变量 > 配置文件 > 默认值
4. **提升类型安全**：使用 dataclass 和类型提示
5. **保持向后兼容**：现有代码无需修改即可继续工作

## 主要改进

### 1. 配置基类 (BaseConfig)

新增 `BaseConfig` 基类，提供统一的配置管理功能：

```python
from dataclasses import dataclass
from deepresearch.config import BaseConfig

@dataclass
class MyConfig(BaseConfig):
    name: str = "default"
    timeout: int = 30
    enabled: bool = True
```

#### 主要方法

- `from_dict(data, source)` - 从字典创建配置实例
- `from_env()` - 从环境变量加载配置
- `from_file(filepath)` - 从文件加载配置
- `merge(other, source)` - 合并另一个配置实例
- `to_dict(redact=False)` - 转换为字典，支持脱敏
- `get(key, default)` - 获取配置项值
- `set(key, value)` - 设置配置项值

### 2. 配置验证器

新增多种验证器，支持配置值验证：

```python
from deepresearch.config import (
    RangeValidator,
    ChoiceValidator,
    TypeValidator,
    ConfigField
)

@dataclass
class ValidatedConfig(BaseConfig):
    # 使用 ConfigField 定义带验证的字段
    port: int = ConfigField(
        default=8080,
        validators=[RangeValidator(min_val=1, max_val=65535)],
        description="服务端口号"
    ).default

    # 或在 __post_init__ 中手动验证
    def __post_init__(self):
        if self.port < 1 or self.port > 65535:
            raise ValidationError(f"port 必须在 1-65535 之间")
        super().__post_init__()
```

#### 内置验证器

- `RangeValidator(min_val, max_val)` - 数值范围验证
- `ChoiceValidator(choices)` - 选项值验证
- `TypeValidator(expected_type)` - 类型验证

### 3. 配置管理器 (ConfigManager)

新增 `ConfigManager` 类，提供统一的配置管理接口：

```python
from deepresearch.config import config_manager

# 设置自定义配置目录
config_manager.set_config_dir("/path/to/config")

# 注册配置加载器
config_manager.register_loader("my_config", lambda: MyConfig())

# 加载配置（带缓存）
config = config_manager.load("my_config")

# 重新加载配置
config_manager.reload("my_config")  # 重新加载指定配置
config_manager.reload()  # 重新加载所有配置
```

### 4. 动态配置目录

支持通过多种方式设置配置目录（按优先级排序）：

1. **代码设置**：`config_manager.set_config_dir("/path")`
2. **环境变量**：`DEEPRESEARCH_CONFIG_DIR=/path`
3. **默认路径**：项目根目录下的 `config` 文件夹

### 5. 多层级配置加载

新增 `load_config` 便捷函数，支持多层级配置覆盖：

```python
from deepresearch.config import load_config

# 配置优先级（高到低）：
# 1. 环境变量
# 2. 配置文件
# 3. 默认值

config = load_config(
    MyConfig,
    filename="my_config.toml",  # 配置文件名
    env_prefix="MYAPP_",        # 环境变量前缀
    use_env=True,               # 是否从环境变量加载
    use_file=True               # 是否从文件加载
)
```

### 6. 可扩展的敏感字段

支持动态添加/移除敏感字段：

```python
from deepresearch.config import add_sensitive_key, remove_sensitive_key

# 添加敏感字段
add_sensitive_key("my_secret_key")

# 移除敏感字段
remove_sensitive_key("my_secret_key")
```

## 向后兼容性

所有原有函数保持完全兼容：

```python
from deepresearch.config import (
    get_config_dir,      # 现在支持动态配置目录
    load_toml_config,    # 完全兼容
    redact_config,       # 现在支持自定义敏感字段
    clear_config_cache   # 完全兼容
)

# 原有代码无需修改即可继续工作
config_dir = get_config_dir()
workflow = load_toml_config("workflow.toml")
redacted = redact_config(config)
```

## 使用示例

### 示例 1：基本配置类

```python
from dataclasses import dataclass
from deepresearch.config import BaseConfig

@dataclass
class DatabaseConfig(BaseConfig):
    host: str = "localhost"
    port: int = 5432
    username: str = "admin"
    password: str = ""  # 敏感字段会自动脱敏
    database: str = "mydb"

# 使用默认值
default_config = DatabaseConfig()

# 从字典创建
config_from_dict = DatabaseConfig.from_dict({
    "host": "db.example.com",
    "port": 3306
})

# 转换为字典（脱敏）
config_dict = config_from_dict.to_dict(redact=True)
# 结果: {'host': 'db.example.com', 'port': 3306, 'username': 'admin', 'password': '***', 'database': 'mydb'}
```

### 示例 2：从环境变量加载

```python
import os
from dataclasses import dataclass
from deepresearch.config import BaseConfig

@dataclass
class AppConfig(BaseConfig):
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = 100

# 设置环境变量
os.environ["MYAPP_DEBUG"] = "true"
os.environ["MYAPP_LOG_LEVEL"] = "DEBUG"
os.environ["MYAPP_MAX_CONNECTIONS"] = "200"

# 从环境变量加载
config = AppConfig.from_env()
print(config.debug)           # True
print(config.log_level)       # DEBUG
print(config.max_connections) # 200
```

### 示例 3：配置验证

```python
from dataclasses import dataclass
from deepresearch.config import (
    BaseConfig,
    RangeValidator,
    ChoiceValidator,
    ValidationError
)

@dataclass
class ServerConfig(BaseConfig):
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4
    log_level: str = "INFO"

    def __post_init__(self):
        # 手动验证
        if not (1 <= self.port <= 65535):
            raise ValidationError(f"port 必须在 1-65535 之间: {self.port}")
        if self.workers < 1:
            raise ValidationError(f"workers 必须大于 0: {self.workers}")
        if self.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
            raise ValidationError(f"无效的 log_level: {self.log_level}")
        super().__post_init__()

# 有效配置
valid_config = ServerConfig(port=8080, workers=4)

# 无效配置会抛出 ValidationError
try:
    invalid_config = ServerConfig(port=70000)
except ValidationError as e:
    print(f"配置错误: {e}")
```

### 示例 4：多层级配置合并

```python
from dataclasses import dataclass
from deepresearch.config import BaseConfig, load_config, config_manager

@dataclass
class FeatureConfig(BaseConfig):
    feature_a: bool = False
    feature_b: bool = False
    feature_c: bool = False
    threshold: int = 50

# 方法 1: 使用 load_config 函数
config = load_config(
    FeatureConfig,
    filename="features.toml",
    env_prefix="FEATURE_"
)

# 方法 2: 手动合并
base_config = FeatureConfig(feature_a=True, threshold=30)
env_config = FeatureConfig.from_env()
final_config = base_config.merge(env_config)
```

### 示例 5：自定义配置目录

```python
from deepresearch.config import config_manager, load_toml_config

# 方法 1: 通过代码设置
config_manager.set_config_dir("/etc/myapp/config")

# 方法 2: 通过环境变量
# export DEEPRESEARCH_CONFIG_DIR=/etc/myapp/config

# 加载配置时会使用新的配置目录
config = load_toml_config("app.toml")
```

## API 参考

### 异常类

- `ConfigError` - 配置加载错误基类
- `ValidationError` - 配置验证错误

### 枚举

- `ConfigSource` - 配置来源枚举
  - `DEFAULT` - 默认值
  - `FILE` - 配置文件
  - `ENV` - 环境变量
  - `CODE` - 代码传入

### 配置基类

- `BaseConfig` - 配置基类
  - 类属性:
    - `_sensitive_keys: set[str]` - 敏感字段集合
    - `_env_prefix: str` - 环境变量前缀
    - `_config_dir_env: str` - 配置目录环境变量名

### 验证器

- `ConfigValidator` - 验证器抽象基类
- `RangeValidator(min_val, max_val)` - 范围验证器
- `ChoiceValidator(choices)` - 选项验证器
- `TypeValidator(expected_type)` - 类型验证器

### 配置管理器

- `ConfigManager` - 配置管理器类
  - `set_config_dir(path)` - 设置配置目录
  - `get_config_dir()` - 获取配置目录
  - `register_loader(name, loader)` - 注册加载器
  - `load(name)` - 加载配置
  - `reload(name=None)` - 重新加载配置
- `config_manager` - 全局配置管理器实例

### 便捷函数

- `load_config(config_class, filename, env_prefix, use_env, use_file)` - 加载配置
- `get_config_dir()` - 获取配置目录
- `load_toml_config(filename)` - 加载 TOML 配置
- `redact_config(config, sensitive_keys)` - 脱敏配置
- `clear_config_cache()` - 清除配置缓存
- `add_sensitive_key(key)` - 添加敏感字段
- `remove_sensitive_key(key)` - 移除敏感字段

## 迁移指南

### 从旧版本迁移

现有代码无需修改即可继续工作。如需使用新功能，可以逐步迁移：

1. **使用新的配置基类**（可选）:
   ```python
   # 旧方式
   from deepresearch.config import load_toml_config
   config = load_toml_config("myconfig.toml")

   # 新方式
   from deepresearch.config import BaseConfig
   from dataclasses import dataclass

   @dataclass
   class MyConfig(BaseConfig):
       setting1: str = "default"
       setting2: int = 42

   config = MyConfig.from_file("config/myconfig.toml")
   ```

2. **使用配置验证**（推荐）:
   ```python
   @dataclass
   class ValidatedConfig(BaseConfig):
       port: int = 8080

       def __post_init__(self):
           if not (1 <= self.port <= 65535):
               raise ValidationError("port 超出范围")
           super().__post_init__()
   ```

3. **使用多层级配置**（推荐）:
   ```python
   from deepresearch.config import load_config

   config = load_config(MyConfig, filename="myconfig.toml")
   ```

## 测试

所有功能都包含完整的单元测试，位于 `tests/unit/config/test_base.py`。

运行测试：

```bash
python -m pytest tests/unit/config/test_base.py -v
```

## 总结

本次优化在不破坏现有功能的前提下，显著提升了配置模块的灵活性和可扩展性：

1. ✅ **消除硬编码** - 配置目录和敏感字段可动态设置
2. ✅ **增强可扩展性** - 引入基类和验证器机制
3. ✅ **支持多层级配置** - 环境变量 > 配置文件 > 默认值
4. ✅ **提升类型安全** - 使用 dataclass 和类型提示
5. ✅ **保持向后兼容** - 现有代码无需修改
