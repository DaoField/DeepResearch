# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

> **详细文档请参阅 [AGENTS.md](./AGENTS.md)**

## 项目概述

DeepResearch 是一个基于多个 LLM 协作的深度研究框架，集成搜索工具对主题进行深度研究，最终输出可视化研究报告。它是一个基于渐进式搜索和交叉评估的轻量级深度研究框架，专注于解决复杂的信息分析问题，并支持个人开发者进行本地部署。通过模块化的上下文组装（涵盖知识库、工具描述和交互历史）和渐进式搜索优化，它构建了一个"任务规划→工具调用→评估与迭代"的智能研究工作流。该工作流有效缓解了大模型处理长上下文时注意力分散和信息丢失的问题。同时，它允许用户引入自定义研究工作流，确保输出内容具有主题聚焦性、论证全面性和逻辑层次感。

## 项目信息
- **版本**: 1.1.1
- **作者**: CzChu <czchu2@iflytek.com>
- **Python 要求**: >=3.10, <4.0

## 快速启动

```bash
# 安装依赖
pip install -e .

# 运行应用
python -m deepresearch.run

# 运行测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/unit/agent/test_agent.py

# 运行测试并生成覆盖率报告
python -m pytest --cov=src
```

## 架构概要

| 组件 | 位置 | 说明 |
|------|------|------|
| 状态图 | `src/deepresearch/agent/agent.py` | LangGraph 工作流编排器 |
| 报告状态 | `src/deepresearch/agent/message.py` | `ReportState`、`Chapter`、`Reference` |
| LLM 接口 | `src/deepresearch/llms/llm.py` | 统一 LLM 调用接口（带缓存） |
| 提示模板 | `src/deepresearch/prompts/` | 动态模板加载 |
| 搜索工具 | `src/deepresearch/tools/search.py` | Jina/Tavily 搜索客户端 |
| 配置管理 | `config/` | TOML 配置文件 |

## 工作流节点

```
preprocess → rewrite → classify → clarify → outline_search → outline → learning → generate → save_local
```

## 配置文件

需在 `config/` 目录配置：
- `llms.toml` - LLM API 设置（6 种类型：basic、clarify、planner、query_generation、evaluate、report）
- `search.toml` - 搜索引擎设置（Jina/Tavily API 密钥）
- `workflow.toml` - 工作流参数

## 关键设计决策

- **LangGraph** 用于工作流编排，提供显式状态转换
- **统一 LLM 接口** 通过 `llm(llm_type, messages, stream)` 调用
- **模块化搜索引擎** 可通过配置切换

---

详细架构图、代码示例和扩展指南请参阅 [AGENTS.md](./AGENTS.md)。
