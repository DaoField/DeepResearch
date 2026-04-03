# DeepResearch API 文档

> **快速导航**: [文档索引](../index.rst) | [项目简介](../README_Zh.md) | [用户手册](../user_guide/user_guide.md) | [部署文档](../deployment/deployment.md) | [架构设计](../architecture/architecture.md)

## 概述

DeepResearch 是一个基于渐进式搜索和交叉评估的轻量级深度研究框架，支持本地部署。本文档提供了系统的核心 API 接口说明，包括 LLM 调用、prompt 模板应用、agent 构建等功能。

> **系统架构详情**请参阅[架构设计文档](../architecture/architecture.md)。
> **使用示例**请参阅[用户操作手册](../user_guide/user_guide.md)。

## 核心模块 API

### 1. LLM 模块

#### `llm(llm_type: str, messages: List[Union[HumanMessage, AIMessage, SystemMessage]], stream: bool = False) -> Union[Generator[str, None, None], str]`

**功能**：生成 LLM 响应，支持流式和非流式模式。

**参数**：
- `llm_type`：LLM 类型，可选值为 "basic"、"clarify"、"planner"、"query_generation"、"evaluate"、"report"
- `messages`：消息列表，表示对话历史
- `stream`：是否启用流式响应，默认为 False

**返回值**：
- 当 `stream=True` 时，返回一个生成器，产生 (reasoning_content, content) 元组
- 当 `stream=False` 时，返回完整的响应字符串

**示例**：
```python
from src.deepresearch.llms.llm import llm
from langchain_core.messages import HumanMessage, SystemMessage

# 非流式响应
messages = [
    SystemMessage(content="You are a helpful assistant"),
    HumanMessage(content="What is AI?")
]
response = llm("basic", messages, stream=False)
print(response)

# 流式响应
for reasoning_content, content in llm("basic", messages, stream=True):
    print(reasoning_content, end="", flush=True)
    print(content, end="", flush=True)
```

#### `_get_llm_instance(llm_type: str, streaming: bool = False, max_tokens: int = 8192) -> ChatDeepSeek`

**功能**：获取 LLM 实例，支持缓存。

**参数**：
- `llm_type`：LLM 类型
- `streaming`：是否启用流式响应
- `max_tokens`：最大生成令牌数，默认为 8192

**返回值**：
- 配置好的 ChatDeepSeek 实例

### 2. Prompt 模板模块

#### `apply_prompt_template(prompt_name: str, state: Dict[str, Any]) -> List`

**功能**：应用 prompt 模板，返回格式化的消息列表。

**参数**：
- `prompt_name`：模板名称
- `state`：包含变量的字典，用于注入模板

**返回值**：
- 消息列表，包含 SystemMessage 和 HumanMessage

**示例**：
```python
from src.deepresearch.prompts.template import apply_prompt_template
from langchain_core.messages import HumanMessage

state = {
    "topic": "人工智能",
    "messages": [HumanMessage(content="人工智能的发展趋势")]
}
messages = apply_prompt_template("classify", state)
print(messages)
```

#### `load_prompt_templates() -> Dict[str, str]`

**功能**：加载所有 prompt 模板。

**返回值**：
- 模板字典，键为模板名称，值为模板内容

#### `load_prompt_templates_lazy() -> Dict[str, str]`

**功能**：懒加载所有 prompt 模板。

**返回值**：
- 模板字典，键为模板名称，值为模板内容

### 3. Agent 模块

#### `build_agent() -> Graph`

**功能**：构建 agent 图。

**返回值**：
- 配置好的 Graph 实例

**示例**：
```python
from src.deepresearch.agent.agent import build_agent
from langchain_core.messages import HumanMessage

# 构建 agent
graph = build_agent()

# 运行 agent
state = {
    "messages": [HumanMessage(content="人工智能的发展趋势")]
}
config = {
    "configurable": {
        "depth": 3,
        "save_as_html": True,
        "save_path": "./example/report"
    }
}

for message in graph.stream(input=state, config=config, stream_mode="values"):
    if isinstance(message, dict):
        if "output" in message and isinstance(message["output"], dict):
            if "message" in message["output"] and message["output"]["message"]:
                print(message["output"]["message"])
```

## 工具模块 API

### 1. 搜索工具

#### `search_tool(query: str) -> Dict`

**功能**：使用搜索引擎搜索信息。

**参数**：
- `query`：搜索查询

**返回值**：
- 搜索结果字典

### 2. 评估工具

#### `evaluate_tool(content: str, criteria: str) -> Dict`

**功能**：评估内容质量。

**参数**：
- `content`：要评估的内容
- `criteria`：评估标准

**返回值**：
- 评估结果字典

## 配置模块 API

### 1. 配置加载

#### `load_toml_config(config_file: str) -> Dict`

**功能**：加载 TOML 配置文件。

**参数**：
- `config_file`：配置文件名称

**返回值**：
- 配置字典

#### `load_llm_configs() -> Dict[str, BaseLLMConfig]`

**功能**：加载 LLM 配置。

**返回值**：
- LLM 配置字典，键为配置名称，值为 BaseLLMConfig 实例

---

**导航**: [文档索引](../index.rst) | [项目简介](../README_Zh.md) | [用户手册](../user_guide/user_guide.md) | [部署文档](../deployment/deployment.md) | [架构设计](../architecture/architecture.md)
