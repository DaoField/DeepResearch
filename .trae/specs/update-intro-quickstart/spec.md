# DeepResearch 文档更新规格说明

## 一、更新背景与目的

### 问题陈述

`doc/intro.md` 第 52-105 行的"快速开始"章节内容已过时，与项目当前状态（v1.1.1）存在多处不一致，主要体现在：

1. **仓库地址过时**：文档引用 `DaoField/DeepResearch`，实际仓库为 `iflytek/DeepResearch`
2. **Poetry 版本建议不准确**：文档建议 2.1.1，实际推荐版本为 2.2.1
3. **运行命令不一致**：文档使用 `poetry run python -m src.run`，实际应为 `python -m deepresearch.run`
4. **模块导入路径说明**：用户手册中 `from src.deepresearch.run` 存在路径歧义

### 更新目标

系统性修订"快速开始"章节，确保文档与项目最新状态（v1.1.1）保持一致，提供准确的技术指引。

## 二、变更内容详述

### 2.1 环境设置章节

| 变更项 | 当前内容 | 更新后内容 | 变更类型 |
|------|---------|-----------|---------|
| 仓库克隆地址 | `git@github.com:DaoField/DeepResearch.git` | `git@github.com:iflytek/DeepResearch.git` | 修正 |
| Poetry 推荐版本 | 2.1.1 | 2.2.1 | 修正 |
| Python 版本说明 | 3.10.0（可能导致问题） | >=3.10,<4.0（更准确的范围） | 优化 |
| 运行环境设置命令 | `poetry install` + `poetry env activate` | 保留 Poetry 安装流程 | 保持 |

### 2.2 环境配置章节

| 变更项 | 当前内容 | 更新后内容 | 变更类型 |
|------|---------|-----------|---------|
| LLM 配置模块说明 | 通用描述 | 补充新增的 `[basic]` 配置段说明 | 增强 |
| 运行命令 | `poetry run python -m src.run` | `python -m deepresearch.run` | 修正 |
| 模块导入示例路径 | `from src.deepresearch.run` | 移除或修正为正确路径 | 修正 |

### 2.3 运行 DeepResearch 章节

| 变更项 | 当前内容 | 更新后内容 | 变更类型 |
|------|---------|-----------|---------|
| 运行命令 | `poetry run python -m src.run` | `python -m deepresearch.run` | 修正 |
| 参考文档链接 | 指向 `user_guide/user_guide.md` | 保持，路径正确 | 验证 |

### 2.4 补充更新（非第 52-105 行范围）

- 版本号更新至 v1.1.1
- 项目简介中补充性能优化相关特性说明

## 三、影响范围

### 受影响文件

| 文件路径 | 变更类型 | 说明 |
|---------|---------|------|
| `doc/intro.md` | 主要更新 | 第 52-105 行快速开始章节全面修订 |
| `doc/user_guide/user_guide.md` | 关联修正 | 模块导入路径修正 |
| `doc/deployment/deployment.md` | 关联修正 | 运行命令与导入路径一致性检查 |

### 配置一致性验证

- `config/llms.toml`：验证配置段（basic, clarify, planner, query_generation, evaluate, report）
- `config/search.toml`：验证搜索工具配置
- `pyproject.toml`：验证版本号和依赖

## 四、更新要求

### 功能性要求

- **准确性**：所有技术参数、命令、路径必须与项目当前状态一致
- **完整性**：涵盖环境设置、配置、运行三个核心环节
- **可操作性**：用户按照文档应能顺利完成本地部署

### 格式规范要求

- 使用标准现代汉语
- 代码块使用正确的语言标识（bash, python, toml）
- 链接路径使用正确的相对路径格式
- RST 语法符合 Sphinx 文档规范

## 五、验证标准

### 内容准确性检查

- [ ] Git 克隆地址指向正确仓库（iflytek/DeepResearch）
- [ ] Poetry 推荐版本为 2.2.1
- [ ] Python 版本要求为 >=3.10,<4.0
- [ ] 运行命令为 `python -m deepresearch.run`
- [ ] 所有配置说明与实际配置文件一致
- [ ] 文档链接指向正确的相对路径

### 格式规范性检查

- [ ] 代码块语法正确（bash, python, toml）
- [ ] RST 图像引用语法正确
- [ ] 文档结构层次清晰
- [ ] 术语使用一致

### 一致性交叉检查

- [ ] intro.md 与 deployment/deployment.md 内容一致
- [ ] intro.md 与 user_guide/user_guide.md 内容一致
- [ ] 文档描述与 pyproject.toml 版本号一致
