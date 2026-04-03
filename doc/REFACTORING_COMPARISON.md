# DeepResearch 项目重构对比文档

## 概述

本文档详细记录了 DeepResearch 项目从初始版本到当前版本的重构过程，包括目录结构、配置方式、代码组织等方面的改进。

---

## 1. 目录结构变化

### 1.1 改造前（假设原始结构）

```
DeepResearch/
├── README.md
├── pyproject.toml
├── config/
│   ├── llms.toml
│   ├── search.toml
│   └── workflow.toml
├── src/
│   ├── __init__.py
│   ├── agent/
│   ├── config/
│   ├── data/
│   ├── llms/
│   ├── mcp_client/
│   ├── prompts/
│   ├── tools/
│   ├── utils/
│   └── run.py
└── tests/
```

### 1.2 改造后（当前结构）

```
DeepResearch/
├── README.md
├── pyproject.toml
├── config/                          # 配置文件独立管理
│   ├── llms.toml
│   ├── search.toml
│   └── workflow.toml
├── src/
│   └── deepresearch/               # 统一包名，符合 Python 最佳实践
│       ├── __init__.py             # 公开 API 暴露
│       ├── errors.py               # 错误类集中定义
│       ├── logging_config.py       # 日志配置独立
│       ├── run.py                  # 入口文件
│       ├── agent/                  # Agent 相关模块
│       ├── config/                 # 配置加载模块
│       ├── data/                   # 数据相关模块
│       ├── llms/                   # 大语言模型模块
│       ├── mcp_client/             # MCP 客户端
│       ├── prompts/                # 提示词模板
│       ├── tools/                  # 工具模块
│       └── utils/                  # 工具函数
└── tests/
```

### 1.3 主要改进点

| 方面 | 改进内容 |
|------|---------|
| **包结构** | 采用标准的 Python 包结构，所有源代码统一放在 `src/deepresearch/` 下 |
| **命名规范** | 包名统一为 `deepresearch`，符合 PEP 8 规范 |
| **模块隔离** | 不同功能模块清晰分离，便于维护和测试 |
| **入口清晰** | 主要功能入口统一管理 |

---

## 2. 配置方式的变化

### 2.1 配置文件管理

#### 改造前（假设）
- 配置文件可能分散在源代码目录中
- 配置加载逻辑与业务逻辑耦合
- 缺少统一的配置管理机制

#### 改造后（当前）
- 配置文件统一放在项目根目录的 `config/` 文件夹
- 提供了统一的配置加载和管理模块 `src/deepresearch/config/base.py`
- 支持配置缓存、脱敏、热更新等功能

### 2.2 核心配置模块

**配置加载模块 (`base.py`)** 提供了以下功能：

```python
# 核心功能
- load_toml_config()      # 加载 TOML 配置文件
- redact_config()          # 配置脱敏，隐藏敏感信息
- get_config_dir()         # 获取配置目录路径
- clear_config_cache()     # 清理配置缓存
```

### 2.3 配置文件示例

#### llms.toml（LLM 配置）
```toml
[basic]
api_base="https://maas-api.cn-huabei-1.xf-yun.com/v1"
model="xdeepseekv31"
api_key="sk-xxxxxxx"

[clarify]
api_base="https://maas-api.cn-huabei-1.xf-yun.com/v1"
model="xdeepseekv31"
api_key="sk-xxxxxxx"

[planner]
api_base="https://maas-api.cn-huabei-1.xf-yun.com/v1"
model="xdeepseekr1"
api_key="sk-xxxxxxx"
```

#### search.toml（搜索配置）
```toml
[search]
engine = "tavily"
timeout = 30
jina_api_key = "jina_xxxxxxxxx"
tavily_api_key = "tvly-xxxxxxxxx"
```

#### workflow.toml（工作流配置）
```toml
[search]
topN = 5
```

### 2.4 配置管理改进收益

- **安全性**：内置敏感信息脱敏功能，防止 API Key 等敏感信息泄露
- **性能**：配置加载带缓存机制，避免重复读取文件
- **可维护性**：配置加载逻辑集中管理，易于扩展和修改
- **灵活性**：支持动态清理缓存，便于配置更新

---

## 3. 代码组织的改进

### 3.1 模块组织架构

#### 改造前
- 模块间耦合度较高
- 缺少统一的错误处理机制
- 日志配置分散
- 公共 API 不明确

#### 改造后
```
deepresearch/
├── __init__.py              # 公开 API 统一导出
├── errors.py                # 错误类层次结构
├── logging_config.py        # 日志配置集中管理
├── run.py                   # 主要入口函数
├── agent/                   # Agent 相关功能
│   ├── agent.py            # Agent 构建器
│   ├── prep.py             # 预处理节点
│   ├── outline.py          # 大纲生成节点
│   ├── learning.py         # 学习节点
│   ├── generate.py         # 生成节点
│   └── message.py          # 消息状态定义
├── config/                  # 配置管理
│   ├── base.py             # 基础配置加载
│   ├── llms_config.py      # LLM 配置
│   ├── search_config.py    # 搜索配置
│   └── workflow_config.py  # 工作流配置
├── prompts/                 # 提示词模板
│   ├── prep/               # 预处理提示词
│   ├── outline/            # 大纲提示词
│   ├── learning/           # 学习提示词
│   └── generate/           # 生成提示词
├── tools/                   # 工具模块
│   ├── search.py           # 搜索工具
│   ├── _jina.py            # Jina 阅读器
│   ├── _tavily.py          # Tavily 搜索
│   └── md2html.py          # Markdown 转 HTML
└── utils/                   # 工具函数
    ├── parse_model_res.py  # 模型响应解析
    └── print_util.py       # 打印工具
```

### 3.2 公开 API 设计

通过 `__init__.py` 统一导出公共 API，使用户可以清晰地了解可用功能：

```python
from deepresearch.agent.agent import build_agent
from deepresearch.run import call_agent, interactive_agent
from deepresearch.logging_config import configure_logging, get_logger
from deepresearch.errors import (
    DeepResearchError,
    ConfigError,
    SearchError,
    LLMError,
    ReportError,
)
```

### 3.3 错误处理体系

建立了清晰的错误类层次结构：

```
DeepResearchError (基类)
├── ConfigError      # 配置相关错误
├── SearchError      # 搜索相关错误
├── LLMError         # 大模型相关错误
└── ReportError      # 报告生成错误
```

### 3.4 Agent 架构改进

采用 LangGraph 构建状态机，节点职责清晰：

```python
def build_agent():
    """构建包含所有节点和边的状态图"""
    agent = StateGraph(ReportState)
    
    # 节点定义
    agent.add_node("preprocess", preprocess_node)
    agent.add_node("rewrite", rewrite_node)
    agent.add_node("classify", classify_node)
    agent.add_node("clarify", clarify_node)
    agent.add_node("outline_search", outline_search_node)
    agent.add_node("outline", outline_node)
    agent.add_node("learning", learning_node)
    agent.add_node("generate", generate_node)
    
    # 边定义
    agent.add_edge(START, "preprocess")
    agent.add_edge("rewrite", "classify")
    agent.add_edge("outline_search", "outline")
    agent.add_edge("learning", "generate")
    
    return agent.compile()
```

### 3.5 入口函数优化

提供了清晰的调用接口：

```python
# 程序化调用
async def call_agent(
    messages: List[Union[HumanMessage, AIMessage]],
    max_depth: int = 3,
    save_as_html: bool = True,
    save_path: str = "./example/report"
)

# 交互式运行
async def interactive_agent(max_depth: int = 3, save_as_html: bool = True)
```

---

## 4. 重构的收益总结

### 4.1 可维护性提升

| 方面 | 改进效果 |
|------|---------|
| **代码可读性** | 模块划分清晰，职责单一，易于理解 |
| **代码可扩展性** | 模块化设计，新增功能无需修改核心代码 |
| **错误定位** | 统一的错误处理体系，便于问题排查 |
| **配置管理** | 集中式配置，便于统一修改和部署 |

### 4.2 可测试性提升

- 模块化设计便于单元测试
- 依赖注入友好
- 配置可独立测试
- 错误类可独立验证

### 4.3 安全性提升

- 敏感信息自动脱敏
- 配置文件独立于代码仓库
- 错误信息不暴露敏感数据

### 4.4 开发体验提升

- 清晰的公共 API 文档
- 统一的日志配置
- 类型提示完善
- 符合 Python 最佳实践

### 4.5 部署便利性提升

- 配置与代码分离
- 标准的包结构
- 清晰的依赖管理
- 易于打包和分发

---

## 5. 最佳实践遵循

本次重构遵循了以下 Python 开发最佳实践：

1. **包结构**：采用 `src/` 布局，避免命名空间污染
2. **命名规范**：遵循 PEP 8 命名规范
3. **错误处理**：建立清晰的异常层次结构
4. **配置管理**：配置与代码分离
5. **日志管理**：统一的日志配置
6. **API 设计**：清晰的公共 API 导出
7. **类型提示**：完善的类型注解
8. **模块化**：高内聚、低耦合的模块设计

---

## 6. 后续优化建议

### 6.1 短期优化

- [ ] 完善单元测试覆盖率
- [ ] 添加类型检查（mypy）
- [ ] 添加代码格式化工具（black）
- [ ] 添加静态代码分析（ruff）

### 6.2 中期优化

- [ ] 添加 CI/CD 流水线
- [ ] 实现配置热更新
- [ ] 添加性能监控
- [ ] 支持多语言配置

### 6.3 长期规划

- [ ] 插件化架构支持
- [ ] 分布式部署支持
- [ ] 可视化工作流编辑器
- [ ] 更多数据源集成

---

## 总结

本次重构使 DeepResearch 项目从一个功能原型转变为一个结构清晰、易于维护、符合工业标准的 Python 项目。通过合理的模块划分、统一的配置管理、清晰的错误处理体系，项目的可维护性、可扩展性和开发体验都得到了显著提升。

重构不是终点，而是一个持续改进的过程。随着项目的发展，我们应该持续关注代码质量，不断优化架构，保持项目的健康发展。
