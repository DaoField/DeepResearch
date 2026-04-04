````{figure} LOGO.svg
:align: center
:alt: Logo

一个基于渐进式搜索和交叉评估的轻量级深度研究框架。
```{image} https://img.shields.io/badge/license-apache2.0-blue.svg
:alt: License
:target: ../LICENSE
```
![repo size](https://img.shields.io/github/repo-size/DaoField/DeepResearch.svg)
[![GitHub Stars][stars-badge]][stars-link]
[![GitHub forks][fork-badge]][fork-link]

[stars-badge]: https://img.shields.io/github/stars/DaoField/DeepResearch?style=social
[stars-link]: https://github.com/DaoField/DeepResearch/stargazers
[fork-badge]: https://img.shields.io/github/forks/DaoField/DeepResearch
[fork-link]: https://github.com/DaoField/DeepResearch/network
````

# 项目简介

DeepResearch专注于解决复杂的信息分析问题，并支持个人开发者进行本地部署。通过模块化的上下文组装（涵盖知识库、工具描述和交互历史）和渐进式搜索优化，它构建了一个"任务规划→工具调用→评估与迭代"的智能研究工作流。该工作流有效缓解了大模型处理长上下文时注意力分散和信息丢失的问题。同时，它允许用户引入自定义研究工作流，确保输出内容具有主题聚焦性、论证全面性和逻辑层次感。

**主要特点：**

- 无需模型定制即可提供高质量结果。
- 支持小型和大型模型协同工作，提高研究效率并控制使用成本。
- 通过知识提取和交叉评估验证减少大模型幻觉。
- 支持轻量级部署和灵活配置。

**框架架构：**

```{image} framework.png
:align: center
:alt: framework
:width: 600px
:height: 450px
```

**示例报告：**

[深度研究产品全球与国内格局分析](https://deep-report-file.xf-yun.com/Deep%20Research%20Products%20Global%20and%20Domestic%20Landscape%20Analysis.html)

[全球AI Agent产品全景分析：核心能力与应用场景](https://deep-report-file.xf-yun.com/Global%20AI%20Agent%20Products%20Panoramic%20Analysis%20Core%20Capabilities%20and%20Application%20Scenarios.html)

## 快速开始

本节将介绍如何配置DeepResearch的本地运行环境，或者您也可以访问[讯飞星火](https://xinghuo.xfyun.cn/desk)并进入"分析研究"标签页进行在线体验。

### 1. 环境设置

- 推荐Python版本：**>=3.10,<4.0**（项目依赖要求）。
- 克隆仓库。

```bash
git clone git@github.com:DaoField/DeepResearch.git
```

- 确保已安装Poetry（推荐版本2.2.1）。

```bash
poetry --version
# 如果尚未安装Poetry，可以尝试通过以下方法安装
# 在Bash中安装Poetry
curl -sSL https://install.python-poetry.org | python3 -
# 在PowerShell中安装Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

- 设置运行环境

```bash
cd DeepResearch
poetry install
```

> 注：Poetry 环境激活在不同 shell 中可能有差异。您可以直接使用 `poetry run` 命令来执行 Python 脚本，例如：
> ```bash
> poetry run python -m deepresearch
> ```

### 2. 环境配置

根据DeepResearch的工作流程，您需要为每个模块填写LLM配置参数（对于`Planner`，建议使用推理能力强的LLM，如`DeepSeekR1`）。

编辑`config/llms.toml`和`config/search.toml`文件，提供您的实际API密钥和配置值：

**LLM配置（`config/llms.toml`）**：

- **`[basic]`**：基础配置，作为默认LLM配置
- **`[clarify]`**：需求澄清模块配置
- **`[planner]`**：任务规划模块配置（建议使用推理能力强的模型，如DeepSeekR1）
- **`[query_generation]`**：查询生成模块配置
- **`[evaluate]`**：评估模块配置
- **`[report]`**：报告生成模块配置

每个配置段需填写：
- **api_base/api_key/model**：兼容OpenAI的API，来自[讯飞云MaaS](https://maas.xfyun.cn/modelSquare)或其他平台。

**搜索工具配置（`config/search.toml`）**：

- **engine**：搜索引擎，支持`jina`或`tavily`
- **jina_api_key**或**tavily_api_key**：从[Jina](https://jina.ai/)或[Tavily](https://www.tavily.com/)获取密钥用于网页读取。

> **详细配置说明**请参阅[部署文档](deployment/deployment.md)。

### 3. 运行DeepResearch

享受这一刻。

使用 Poetry 运行：

```bash
poetry run python -m deepresearch.run "您想要研究的主题"
```

例如：

```bash
poetry run python -m deepresearch.run "人工智能的发展趋势"
```

如果已激活虚拟环境，也可以直接运行：

```bash
python -m deepresearch.run "您想要研究的主题"
```

> **详细使用说明**请参阅[用户操作手册](user_guide/user_guide.md)。

```{image} start.png
:align: center
:alt: framework
```

## 支持

- 社区讨论：[GitHub Discussions](https://github.com/DaoField/DeepResearch/discussions)
- 问题反馈：[Issues](https://github.com/DaoField/DeepResearch/issues)

## 许可证

本项目采用[Apache 2.0许可证](../LICENSE)。

