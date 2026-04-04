# DeepResearch 部署文档

> **快速导航**: [文档索引](../index.rst) | [用户手册](../user_guide/user_guide.md) | [API文档](../api/api.md)

## 环境要求

### 1. 硬件要求

- **CPU**：至少 4 核
- **内存**：至少 8GB
- **磁盘**：至少 20GB 可用空间

### 2. 软件要求

- **Python**：3.10 或更高版本
- **pip**：20.0 或更高版本
- **Git**：2.0 或更高版本

## 安装步骤

### 1. 克隆代码库

```bash
git clone https://github.com/iflytek/DeepResearch.git
cd DeepResearch
```

### 2. 安装依赖

#### 使用 pip 安装

```bash
pip install -e .
```

#### 使用 poetry 安装

```bash
poetry install
```

### 3. 配置系统

#### 3.1 配置 LLM

编辑 `config/llms.toml` 文件，配置 LLM 的 API 密钥和其他参数：

```toml
[basic]
api_base="https://maas-coding-api.cn-huabei-1.xf-yun.com/v2"
model="astron-code-latest"
api_key="your_api_key"

[clarify]
api_base="https://maas-coding-api.cn-huabei-1.xf-yun.com/v2"
model="astron-code-latest"
api_key="your_api_key"

[planner]
api_base="https://maas-coding-api.cn-huabei-1.xf-yun.com/v2"
model="astron-code-latest"
api_key="your_api_key"

[query_generation]
api_base="https://maas-coding-api.cn-huabei-1.xf-yun.com/v2"
model="astron-code-latest"
api_key="your_api_key"

[evaluate]
api_base="https://maas-coding-api.cn-huabei-1.xf-yun.com/v2"
model="astron-code-latest"
api_key="your_api_key"

[report]
api_base="https://maas-coding-api.cn-huabei-1.xf-yun.com/v2"
model="astron-code-latest"
api_key="your_api_key"
```

#### 3.2 配置搜索工具

编辑 `config/search.toml` 文件，配置搜索工具的 API 密钥：

```toml
[search]
# search engine (supports "jina" or "tavily" now)
engine = "tavily"
timeout = 30
jina_api_key = "your_jina_api_key"
tavily_api_key = "your_tavily_api_key"
```

## 运行系统

### 1. 命令行运行

```bash
python -m deepresearch "人工智能的发展趋势"
```

### 2. 作为模块导入

```python
from deepresearch import call_agent
from langchain_core.messages import HumanMessage

messages = [
    HumanMessage(content="人工智能的发展趋势")
]

async def main():
    await call_agent(messages=messages, max_depth=3, save_as_html=True)

import asyncio
asyncio.run(main())
```

> **详细使用说明**请参阅[用户操作手册](../user_guide/user_guide.md)。
> **更多 API 示例**请参阅[API文档](../api/api.md)。

## 测试系统

### 1. 运行单元测试

```bash
python -m pytest tests/unit/ -v
```

### 2. 运行集成测试

```bash
python -m pytest tests/integration/ -v
```

### 3. 运行端到端测试

```bash
python -m pytest tests/e2e/ -v
```

## 配置说明

### 1. LLM 配置

- `api_base`：LLM 的 API 基础 URL
- `model`：LLM 的模型名称
- `api_key`：LLM 的 API 密钥

### 2. 搜索工具配置

- `engine`：搜索引擎，支持 "jina" 或 "tavily"
- `timeout`：搜索超时时间，单位为秒
- `jina_api_key`：Jina 搜索引擎的 API 密钥
- `tavily_api_key`：Tavily 搜索引擎的 API 密钥

## 常见问题

### 1. 安装依赖失败

**问题**：安装依赖时出现错误。

**解决方案**：确保 Python 版本为 3.10 或更高版本，并且 pip 版本为 20.0 或更高版本。

### 2. LLM 调用失败

**问题**：LLM 调用时出现错误。

**解决方案**：检查 LLM 的 API 密钥是否正确，并且 API 密钥是否具有足够的权限。

### 3. 搜索工具调用失败

**问题**：搜索工具调用时出现错误。

**解决方案**：检查搜索工具的 API 密钥是否正确，并且 API 密钥是否具有足够的权限。

### 4. 系统运行缓慢

**问题**：系统运行速度缓慢。

**解决方案**：
- 增加系统的内存和 CPU 资源
- 优化 LLM 的配置，减少生成的令牌数
- 使用更高效的搜索引擎

## 故障排除

### 1. 查看日志

系统的日志文件存储在 `logs` 目录中，可以查看日志文件来了解系统的运行情况。

### 2. 检查配置

确保系统的配置文件正确配置，包括 LLM 配置和搜索工具配置。

### 3. 检查依赖

确保系统的依赖库正确安装，并且版本兼容。

## 升级系统

### 1. 拉取最新代码

```bash
git pull
```

### 2. 更新依赖

#### 使用 pip 更新

```bash
pip install -e .
```

#### 使用 poetry 更新

```bash
poetry install
```

### 3. 更新配置

根据需要更新系统的配置文件。

## 卸载系统

### 1. 移除代码库

```bash
rm -rf DeepResearch
```

### 2. 移除依赖

```bash
pip uninstall -e DeepResearch
```

---

**导航**: [文档索引](../index.rst) | [用户手册](../user_guide/user_guide.md) | [API文档](../api/api.md) | [架构设计](../architecture/architecture.md)
