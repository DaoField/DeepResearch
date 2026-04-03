# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this repository.

> **项目来源**: [iflytek/DeepResearch](https://github.com/iflytek/DeepResearch)
> **许可证**: Apache 2.0 License
> **版权**: © 2026 iFLYTEK CO.,LTD.

---

## 目录

1. [项目概述](#1-项目概述)
2. [开发命令](#2-开发命令)
3. [整体架构设计](#3-整体架构设计)
4. [核心模块详解](#4-核心模块详解)
5. [关键类与函数说明](#5-关键类与函数说明)
6. [配置指南](#6-配置指南)
7. [扩展开发指南](#7-扩展开发指南)

---

## 1. 项目概述

### 1.1 项目简介

DeepResearch 是一个基于**渐进式搜索和交叉评估**的轻量级深度研究框架，专注于解决复杂信息分析问题，并支持个人开发者本地部署。

### 1.2 核心特性

| 特性 | 描述 |
|------|------|
| 无需模型定制 | 可直接利用现有大模型完成深度研究任务 |
| 大小模型协同 | 支持小型和大型语言模型协同，提高研究效率并控制使用成本 |
| 幻觉抑制 | 通过知识提取和交叉评估验证，减少大模型幻觉 |
| 轻量级部署 | 支持本地快速部署，配置灵活 |
| 模块化设计 | 每个组件均可独立替换或扩展 |

### 1.3 技术栈

| 组件 | 技术 |
|------|------|
| 核心框架 | LangGraph (状态机工作流) |
| LLM集成 | LangChain + DeepSeek |
| 搜索工具 | Jina AI / Tavily |
| 配置文件 | TOML |
| 依赖管理 | Poetry |
| Python版本 | >=3.10, <4.0 |

---

## 2. 开发命令

This project uses Poetry for dependency management:

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry env activate

# Run the application
poetry run python -m src.run

# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/unit/agent/test_agent.py

# Run specific test function
poetry run pytest tests/unit/agent/test_agent.py::test_function_name

# Run tests with coverage
poetry run pytest --cov=src
```

---

## 3. 整体架构设计

### 3.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DeepResearch 系统架构                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐     ┌──────────────────────────────────────────────┐   │
│  │   用户输入   │────▶│              LangGraph 工作流                 │   │
│  └─────────────┘     │  ┌────────────────────────────────────────┐  │   │
│                       │  │           预处理阶段 (Prep)            │  │   │
│                       │  │  preprocess → rewrite → classify       │  │   │
│                       │  │           → clarify → generic          │  │   │
│                       │  └────────────────────────────────────────┘  │   │
│                       │                    │                        │   │
│                       │                    ▼                        │   │
│                       │  ┌────────────────────────────────────────┐  │   │
│                       │  │          规划阶段 (Planning)          │  │   │
│                       │  │     outline_search → outline          │  │   │
│                       │  └────────────────────────────────────────┘  │   │
│                       │                    │                        │   │
│                       │                    ▼                        │   │
│                       │  ┌────────────────────────────────────────┐  │   │
│                       │  │         深度研究阶段 (Learning)         │  │   │
│                       │  │         DeepSearch 多轮迭代             │  │   │
│                       │  │    搜索→提取→评估→迭代 (最多3层)        │  │   │
│                       │  └────────────────────────────────────────┘  │   │
│                       │                    │                        │   │
│                       │                    ▼                        │   │
│                       │  ┌────────────────────────────────────────┐  │   │
│                       │  │          报告生成 (Generate)            │  │   │
│                       │  │      Markdown + HTML 输出              │  │   │
│                       │  └────────────────────────────────────────┘  │   │
│                       └──────────────────────────────────────────────┘   │
│                                       │                                   │
│                                       ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                         外部服务层                                  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │ │
│  │  │ Jina/Tavily │  │   DeepSeek  │  │  ArXiv/PubMed (MCP)      │   │ │
│  │  │  搜索API     │  │    LLM API  │  │  学术论文搜索            │   │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 工作流程状态图

```
                    ┌──────────┐
                    │   START   │
                    └────┬─────┘
                         │
                         ▼
               ┌─────────────────────┐
               │    preprocess       │ 预处理: 解析用户消息
               └──────────┬──────────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
    ┌──────────┐  ┌───────────┐  ┌──────────┐
    │ 1条消息   │  │  3条消息   │  │ 其他消息  │
    └────┬─────┘  └─────┬─────┘  └────┬─────┘
         │              │             │
         ▼              ▼             ▼
  ┌──────────┐  ┌───────────┐  ┌──────────┐
  │ classify │  │  rewrite   │  │  generic │
  └────┬─────┘  └─────┬─────┘  └────┬─────┘
       │              │             │
       └──────────────┼─────────────┘
                      │
                      ▼
              ┌───────────────┐
              │   clarify     │ 澄清: 确定研究范围
              └───────┬───────┘
                      │
                      ▼
            ┌─────────────────┐
            │  outline_search  │ 搜索: 为大纲获取背景知识
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │    outline       │ 生成: 产出报告大纲结构
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │    learning     │ 学习: 深度搜索每个章节
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │    generate     │ 生成: 撰写完整报告
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  save_local     │ 保存: Markdown/HTML
            └────────┬────────┘
                     │
                     ▼
               ┌──────────┐
               │   END    │
               └──────────┘
```

### 3.3 多轮迭代搜索流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    DeepSearch 多轮迭代流程                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  第一轮搜索  │───▶│  知识提取   │───▶│   评估验证  │        │
│  │  Round 1    │    │ Extract     │    │ Evaluate    │        │
│  └─────────────┘    └─────────────┘    └──────┬──────┘        │
│                                                │                │
│                              ┌──────────────────┼──────────────┐ │
│                              ▼                                 │ │
│                      ┌─────────────┐                          │ │
│                      │  深度足够?  │                          │ │
│                      └──────┬──────┘                          │ │
│                             │                                 │ │
│              ┌──────────────┴──────────────┐                   │ │
│              ▼                             ▼                   │ │
│     ┌─────────────────┐            ┌──────────────┐            │ │
│     │  生成新查询     │            │    结束      │            │ │
│     │  New Queries   │            │    END       │            │ │
│     └────────┬────────┘            └──────────────┘            │ │
│              │                                              │ │
│              ▼                                              │ │
│     ┌─────────────────┐                                     │ │
│     │  第二轮搜索      │                                     │ │
│     │  Round 2        │                                     │ │
│     └────────┬────────┘                                     │ │
│              │                                              │ │
│              └──────────────────────────────────────────────┘ │
│                                                                 │
│                    (最多迭代 N 轮，N 由 depth 参数控制)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 核心模块详解

### 4.1 Agent 模块 (`src/deepresearch/agent/`)

Agent 模块是整个系统的核心，负责构建和管理基于 LangGraph 的状态机工作流。

| 文件 | 职责 | 关键类/函数 |
|------|------|-------------|
| `agent.py` | 构建 LangGraph 工作流 | `build_agent()` |
| `message.py` | 定义状态数据结构 | `ReportState`, `Chapter`, `Reference` |
| `prep.py` | 用户输入预处理 | `preprocess_node`, `rewrite_node`, `classify_node` |
| `outline.py` | 大纲生成 | `outline_node`, `outline_search_node` |
| `learning.py` | 章节深度学习 | `learning_node` |
| `deepsearch.py` | 多轮搜索迭代 | `DeepSearch` |
| `generate.py` | 报告生成 | `generate_node`, `ContentProcessor` |

### 4.2 LLM 模块 (`src/deepresearch/llms/`)

提供统一的 LLM 调用接口，支持多种模型和流式输出。

```python
# 核心接口
def llm(
    llm_type: str,      # LLM类型: basic, clarify, planner, query_generation, evaluate, report
    messages: List,     # 消息列表
    stream: bool = True # 是否流式输出
) -> Union[str, Iterator]
```

### 4.3 Tools 模块 (`src/deepresearch/tools/`)

搜索工具的抽象和实现层。

```
┌─────────────────┐
│  SearchClient   │  ← 工厂类，根据配置选择具体实现
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌────────┐
│ Jina  │ │ Tavily │
└───┬───┘ └───┬────┘
    │         │
    ▼         ▼
┌─────────────────┐
│  SearchResult   │  ← 统一返回格式
└─────────────────┘
```

### 4.4 Config 模块 (`src/deepresearch/config/`)

集中管理所有配置，支持 TOML 格式。

| 文件 | 作用 |
|------|------|
| `llms_config.py` | LLM 配置加载，提供 6 种 LLM 类型配置 |
| `search_config.py` | 搜索引擎配置 (Jina/Tavily API密钥) |
| `workflow_config.py` | 工作流参数配置 (搜索深度、结果数量等) |

### 4.5 Prompts 模块 (`src/deepresearch/prompts/`)

提示模板管理，支持变量注入。

```
prompts/
├── template.py          # 模板引擎
├── generate/           # 报告生成提示
│   ├── generate.py     # 章节内容生成
│   └── chart.py        # 图表生成
├── learning/          # 深度学习提示
│   ├── extract_knowledge.py  # 知识提取
│   ├── evaluate_*.py        # 各类评估
│   └── search_query.py      # 搜索查询生成
├── outline/           # 大纲生成提示
│   ├── outline.py    # 大纲结构
│   └── outline_sq.py # 搜索查询
└── prep/             # 预处理提示
    ├── classify.py   # 领域分类
    ├── clarify.py    # 澄清问题
    └── rewrite.py   # 需求重写
```

### 4.6 Data 模块 (`src/deepresearch/data/`)

定义分析类型的分类体系。

```python
class AnalysisTag(Enum):
    INDUSTRY = "Industry Research"      # 行业研究
    COMPANY = "Company Research"        # 公司研究
    COMPREHENSIVE = "Comprehensive Analysis"  # 综合分析
```

### 4.7 MCP Client 模块 (`src/deepresearch/mcp_client/`)

MCP (Model Context Protocol) 客户端，用于学术搜索。

| 文件 | 功能 |
|------|------|
| `arxiv.py` | arXiv 论文搜索 |
| `pubmed.py` | PubMed 医学文献搜索 |
| `paper_mcp_server.py` | MCP 服务器实现 |

---

## 5. 关键类与函数说明

### 5.1 状态管理

#### `ReportState` (message.py)

```python
class ReportState(MessagesState):
    outline: Chapter           # 报告大纲
    messages: List            # 对话历史
    topic: str                 # 报告主题
    domain: str                # 研究领域
    logic: str                 # 分析逻辑
    details: str               # 详细说明
    output: dict               # 输出信息
    knowledge: list            # 知识库
    final_report: str          # 最终报告
    search_id: int             # 搜索ID计数器
```

#### `Chapter` (message.py)

```python
class Chapter:
    id: int                    # 章节ID
    level: int                 # 层级 (1-6)
    title: str                 # 章节标题
    thinking: str              # 思考过程
    summary: str               # 章节摘要
    sub_chapter: List[Chapter] # 子章节
    parent_chapter: Chapter    # 父章节
    references: List[Reference] # 引用列表
    learning_knowledge: List    # 学习到的知识
```

### 5.2 核心节点函数

#### `preprocess_node` (prep.py)

```python
def preprocess_node(state: ReportState) -> dict:
    """
    处理用户输入消息，根据消息数量决定后续流程

    逻辑:
    - 0条消息: 结束
    - 1条消息: 进入分类
    - 3条消息: 进入重写
    - 其他: 进入通用回复
    """
```

#### `outline_node` (outline.py)

```python
def outline_node(state: ReportState) -> Command:
    """
    生成报告大纲的核心函数

    流程:
    1. 调用 planner LLM 生成大纲
    2. 流式输出思考过程
    3. 解析 Markdown 为章节结构
    4. 返回 Command(goto="learning")
    """
```

#### `learning_node` (learning.py)

```python
def learning_node(state: ReportState, config: RunnableConfig) -> dict:
    """
    对大纲每个章节进行深度研究

    流程:
    1. 遍历所有子章节
    2. 为每个章节创建 DeepSearch 实例
    3. 执行多轮搜索迭代
    4. 收集和整合搜索结果
    """
```

#### `generate_node` (generate.py)

```python
def generate_node(state: ReportState, config: RunnableConfig) -> dict:
    """
    根据大纲和知识库生成完整报告

    功能:
    - 流式输出生成过程
    - 自动插入引用标记
    - 支持表格和图表
    - 生成 Markdown 和 HTML
    """
```

### 5.3 深度搜索类

#### `DeepSearch` (deepsearch.py)

```python
class DeepSearch:
    def __init__(
        self,
        report_topic: str,           # 报告主题
        chapter_title: str,           # 章节标题
        sub_chapter_titles: List,     # 子章节标题
        chapter_summary: str,         # 章节摘要
        max_depth: int = 3,           # 最大搜索深度
        top_n: int = 5                # 每轮返回结果数
    ):
        ...

    def deep_search(self) -> DeepSearchResult:
        """
        执行深度搜索的主入口

        返回: DeepSearchResult
        """
```

### 5.4 搜索工具类

#### `SearchClient` (search.py)

```python
class SearchClient:
    """搜索客户端工厂类"""
    
    def __init__(self):
        # 根据配置选择引擎 (jina/tavily)
        if search_config.engine == "jina":
            self._client = JinaSearchClient()
        elif search_config.engine == "tavily":
            self._client = TavilySearchClient()
    
    def search(self, query: str, top_n: int) -> List[SearchResult]:
        """执行搜索并返回结果"""
```

#### `SearchResult` (_search.py)

```python
@dataclass(kw_only=True)
class SearchResult:
    url: str      # 来源URL
    title: str    # 结果标题
    summary: str  # 摘要
    content: str  # 完整内容
    date: str     # 发布日期
    id: int       # 唯一标识
```

---

## 6. 配置指南

### 6.1 环境要求

| 要求 | 版本 |
|------|------|
| Python | ≥3.10, <4.0 (推荐 3.10.0) |
| Poetry | ≥2.2.1 |
| 操作系统 | Windows/Linux/macOS |

### 6.2 LLM 配置 (llms.toml)

```toml
# 文件路径: config/llms.toml

[basic]
api_base="https://maas-api.cn-huabei-1.xf-yun.com/v1"
model="xdeepseekv31"
api_key="sk-xxxxxx"

[clarify]
api_base="https://maas-api.cn-huabei-1.xf-yun.com/v1"
model="xdeepseekv31"
api_key="sk-xxxxxx"

[planner]
# 规划模块推荐使用推理能力强的模型
api_base="https://maas-api.cn-huabei-1.xf-yun.com/v1"
model="xdeepseekr1"
api_key="sk-xxxxxx"

[query_generation]
api_base="https://maas-api.cn-huabei-1.xf-yun.com/v1"
model="xdeepseekv31"
api_key="sk-xxxxxx"

[evaluate]
api_base="https://maas-api.cn-huabei-1.xf-yun.com/v1"
model="xdeepseekv31"
api_key="sk-xxxxxx"

[report]
api_base="https://maas-api.cn-huabei-1.xf-yun.com/v1"
model="xdeepseekv31"
api_key="sk-xxxxxx"
```

**LLM 类型说明**:

| 类型 | 用途 | 推荐模型 |
|------|------|----------|
| `basic` | 基础对话 | DeepSeek V3 |
| `clarify` | 问题澄清 | DeepSeek V3 |
| `planner` | 任务规划/大纲生成 | DeepSeek R1 (推理能力强) |
| `query_generation` | 搜索查询生成 | DeepSeek V3 |
| `evaluate` | 内容评估验证 | DeepSeek V3 |
| `report` | 报告生成 | DeepSeek V3 |

### 6.3 搜索配置 (search.toml)

```toml
# 文件路径: config/search.toml

[search]
engine = "jina"              # 搜索引擎: jina 或 tavily
jina_api_key = "your-jina-key"   # 从 https://jina.ai/ 获取
# tavily_api_key = "your-tavily-key"  # 从 https://tavily.com/ 获取
timeout = 30                 # 超时时间(秒)
```

### 6.4 工作流配置 (workflow.toml)

```toml
# 文件路径: config/workflow.toml

[search]
topN = 5        # 每轮搜索返回的结果数量

[report]
save_as_html = true   # 是否保存为HTML格式
```

---

## 7. 扩展开发指南

### 7.1 添加新的搜索工具

```python
# 1. 在 src/deepresearch/tools/ 下创建新文件 _custom_search.py
from typing import List
from src.deepresearch.tools._search import SearchClient, SearchResult

class CustomSearchClient(SearchClient):
    def __init__(self, api_key: str):
        self._api_key = api_key
        # 初始化自定义搜索API
    
    def search(self, query: str, top_n: int) -> List[SearchResult]:
        # 实现搜索逻辑
        results = []
        # ... 调用自定义API并转换结果
        return results

# 2. 修改 src/deepresearch/tools/search.py 添加新引擎支持
if search_config.engine == "custom":
    self._client = CustomSearchClient(api_key=search_config.custom_api_key)

# 3. 修改 config/search.toml
[search]
engine = "custom"
custom_api_key = "your-key"
```

### 7.2 添加新的提示模板

```python
# 1. 在 src/deepresearch/prompts/your_module/ 下创建模板文件 your_template.py

SYSTEM_PROMPT = """你是一个专业的分析助手..."""

PROMPT = """
根据以下主题撰写内容:
主题: {topic}
要求: {requirements}

请以Markdown格式输出。
"""

# 2. 在 src/deepresearch/prompts/template.py 添加目录扫描
PROMPTS_DIRS = [
    # ... 现有目录
    os.path.join(os.path.dirname(__file__), "your_module"),
]

# 3. 使用模板
from src.deepresearch.prompts.template import apply_prompt_template

messages = apply_prompt_template(
    prompt_name="your_module/your_template",
    state={
        "topic": "示例主题",
        "requirements": "详细要求"
    }
)
```

### 7.3 自定义工作流节点

```python
# 在 src/deepresearch/agent/ 下创建新节点文件 custom_node.py
from typing import Dict, Any
from src.deepresearch.agent.message import ReportState
from langgraph.types import Command

def custom_node(state: ReportState) -> Command:
    """
    自定义节点函数
    
    Args:
        state: 当前工作流状态
        
    Returns:
        Command: 控制流向和状态更新
    """
    # 获取状态数据
    topic = state.get("topic")
    
    # 执行业务逻辑
    result = do_something(topic)
    
    # 返回状态更新和下一步
    return Command(
        goto="next_node",  # 下一个节点
        update={
            "custom_field": result,
            # 其他状态更新...
        }
    )

# 在 src/deepresearch/agent/agent.py 中注册节点
def build_agent():
    workflow = StateGraph(ReportState)
    # ... 添加其他节点
    workflow.add_node("custom", custom_node)
    # ... 连接节点
```

---

## 附录: 工作流节点说明

| 节点名称 | 输入 | 输出 | 说明 |
|----------|------|------|------|
| `preprocess` | 用户消息 | 消息列表 | 消息格式解析 |
| `rewrite` | 交互历史 | 重写后主题 | 多轮澄清 |
| `classify` | 用户问题 | 领域分类 | 确定分析类型 |
| `clarify` | 分类结果 | 确认意图 | 最终确认 |
| `generic` | 任意消息 | 通用回复 | 非研究类问题 |
| `outline_search` | 主题 | 背景知识 | 为大纲搜索 |
| `outline` | 背景知识 | 大纲结构 | 生成章节 |
| `learning` | 大纲 | 章节知识 | 深度研究 |
| `generate` | 章节+知识 | 完整报告 | 流式生成 |
| `save_local` | 报告 | 保存文件 | Markdown/HTML |
