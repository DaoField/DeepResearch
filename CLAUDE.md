# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

> **详细文档请参阅 [AGENTS.md](./AGENTS.md)**

## 项目概述

DeepResearch 是一个基于渐进式搜索和交叉评估的轻量级深度研究框架，通过组装模块化上下文并迭代执行"任务规划 → 工具调用 → 评估与迭代"工作流来解决复杂信息分析问题。基于 LangGraph 构建，支持多 LLM 协同。

## 快速启动

```bash
# 安装依赖
poetry install

# 运行应用
poetry run python -m src.run

# 运行测试
poetry run pytest
```

## 架构概要

| 组件 | 位置 | 说明 |
|------|------|------|
| 状态图 | `src/agent/agent.py` | LangGraph 工作流编排器 |
| 报告状态 | `src/agent/message.py` | `ReportState`、`Chapter`、`Reference` |
| LLM 接口 | `src/llms/llm.py` | 统一 LLM 调用接口（带缓存） |
| 提示模板 | `src/prompts/` | 动态模板加载 |
| 搜索工具 | `src/tools/search.py` | Jina/Tavily 搜索客户端 |
| 配置管理 | `src/config/` | TOML 配置文件 |

## 工作流节点

```
preprocess → rewrite → classify → clarify → outline_search → outline → learning → generate → save_local
```

## 配置文件

需在 `src/config/` 目录配置：
- `llms.toml` - LLM API 设置（6 种类型：basic、clarify、planner、query_generation、evaluate、report）
- `search.toml` - 搜索引擎设置（Jina/Tavily API 密钥）
- `workflow.toml` - 工作流参数

## 关键设计决策

- **LangGraph** 用于工作流编排，提供显式状态转换
- **统一 LLM 接口** 通过 `llm(llm_type, messages, stream)` 调用
- **模块化搜索引擎** 可通过配置切换

---

详细架构图、代码示例和扩展指南请参阅 [AGENTS.md](./AGENTS.md)。
