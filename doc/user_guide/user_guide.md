# DeepResearch 用户操作手册

> **快速导航**: [文档索引](../index.rst) | [项目简介](../README_Zh.md) | [部署文档](../deployment/deployment.md) | [API文档](../api/api.md)

## 系统简介

DeepResearch 是一个基于渐进式搜索和交叉评估的轻量级深度研究框架，支持本地部署。系统通过模块化上下文组装和渐进式搜索优化，构建了"任务规划 → 工具调用 → 评估与迭代"的智能研究工作流。

> **系统架构详情**请参阅[架构设计文档](../architecture/architecture.md)。

## 核心功能

### 1. 深度研究

DeepResearch 能够进行深度研究，通过多轮搜索和评估，获取全面、准确的信息。

### 2. 智能规划

系统能够智能规划研究任务，确定需要执行的步骤，提高研究效率。

### 3. 工具集成

系统集成了搜索工具、评估工具等多种工具，支持多种研究场景。

### 4. 结果可视化

系统能够将研究结果生成为 HTML 报告，方便用户查看和分享。

## 使用步骤

### 1. 准备工作

1. 安装 DeepResearch（详见[部署文档](../deployment/deployment.md)）
2. 配置 LLM 和搜索工具的 API 密钥（详见[部署文档](../deployment/deployment.md)）

### 2. 运行系统

#### 2.1 命令行运行

```bash
python -m deepresearch.run "人工智能的发展趋势"
```

#### 2.2 作为模块导入

```python
from src.deepresearch.run import call_agent
from langchain_core.messages import HumanMessage

messages = [
    HumanMessage(content="人工智能的发展趋势")
]

async def main():
    await call_agent(messages=messages, max_depth=3, save_as_html=True)

import asyncio
asyncio.run(main())
```

> **更多 API 使用示例**请参阅[API文档](../api/api.md)。

### 3. 查看结果

系统运行完成后，会生成 HTML 报告，存储在 `./example/report` 目录中。用户可以打开 HTML 文件查看研究结果。

## 示例

### 示例 1：研究人工智能的发展趋势

**输入**：
```bash
python -m deepresearch.run "人工智能的发展趋势"
```

**输出**：
- HTML 报告，包含人工智能的发展历史、当前状态、未来趋势等信息。

### 示例 2：研究公司的业务板块

**输入**：
```bash
python -m deepresearch.run "请介绍阿里巴巴公司的电商零售业务板块，并分析其未来3-5年的发展前景，重点关注行业竞争视角。"
```

**输出**：
- HTML 报告，包含阿里巴巴公司的电商零售业务板块介绍、市场分析、竞争分析、未来展望等信息。

## 高级功能

### 1. 配置研究深度

通过 `max_depth` 参数配置研究深度，深度越大，研究越深入，但运行时间也会越长。

```python
await call_agent(messages=messages, max_depth=5, save_as_html=True)
```

### 2. 配置报告保存路径

通过 `save_path` 参数配置报告保存路径。

```python
await call_agent(messages=messages, max_depth=3, save_as_html=True, save_path="./my_report")
```

### 3. 禁用 HTML 报告

通过 `save_as_html` 参数禁用 HTML 报告生成。

```python
await call_agent(messages=messages, max_depth=3, save_as_html=False)
```

## 常见问题

### 1. 系统运行时间过长

**问题**：系统运行时间过长，需要等待很长时间才能得到结果。

**解决方案**：
- 减少研究深度，通过 `max_depth` 参数设置较小的值。
- 优化 LLM 的配置，减少生成的令牌数。
- 使用更高效的搜索引擎。

### 2. 研究结果不够准确

**问题**：研究结果不够准确，存在错误或遗漏。

**解决方案**：
- 增加研究深度，通过 `max_depth` 参数设置较大的值。
- 提供更具体的查询，明确研究的范围和重点。
- 检查 LLM 和搜索工具的配置，确保 API 密钥正确。

### 3. HTML 报告生成失败

**问题**：HTML 报告生成失败，无法查看研究结果。

**解决方案**：
- 检查 `save_path` 参数是否正确，确保路径存在且有写入权限。
- 检查系统的依赖库是否正确安装，特别是与 HTML 生成相关的库。

## 最佳实践

### 1. 明确研究目标

在使用系统时，应明确研究目标，提供具体的查询，避免过于宽泛的问题。

### 2. 合理配置研究深度

根据研究的复杂度和重要性，合理配置研究深度，平衡研究质量和运行时间。

### 3. 验证研究结果

系统生成的研究结果仅供参考，用户应根据自己的专业知识和判断，验证研究结果的准确性。

### 4. 定期更新配置

定期更新 LLM 和搜索工具的配置，确保系统能够使用最新的模型和功能。

## 故障排除

### 1. 系统无法启动

**问题**：系统无法启动，出现错误信息。

**解决方案**：
- 检查系统的依赖库是否正确安装。
- 检查 LLM 和搜索工具的配置是否正确。
- 查看系统的日志文件，了解错误的具体原因。

### 2. LLM 调用失败

**问题**：LLM 调用失败，出现错误信息。

**解决方案**：
- 检查 LLM 的 API 密钥是否正确。
- 检查 LLM 的 API 服务是否正常运行。
- 检查网络连接是否正常。

### 3. 搜索工具调用失败

**问题**：搜索工具调用失败，出现错误信息。

**解决方案**：
- 检查搜索工具的 API 密钥是否正确。
- 检查搜索工具的 API 服务是否正常运行。
- 检查网络连接是否正常。

## 联系支持

如果您在使用过程中遇到问题，可以通过以下方式联系支持：

- 电子邮件：support@iflytek.com
- 官方网站：https://www.iflytek.com
- GitHub 仓库：https://github.com/iflytek/DeepResearch

---

**导航**: [文档索引](../index.rst) | [项目简介](../README_Zh.md) | [部署文档](../deployment/deployment.md) | [API文档](../api/api.md) | [架构设计](../architecture/architecture.md)
