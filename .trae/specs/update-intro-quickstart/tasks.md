# 任务清单

## 任务 1：更新 doc/intro.md 快速开始章节

### 1.1 环境设置章节更新
- [x] 修正 Git 克隆地址：`DaoField/DeepResearch` → `iflytek/DeepResearch`
- [x] 修正 Poetry 推荐版本：2.1.1 → 2.2.1
- [x] 优化 Python 版本说明：3.10.0 → >=3.10,<4.0
- [x] 验证 Poetry 安装命令

### 1.2 环境配置章节更新
- [x] 补充 `[basic]` 配置段说明
- [x] 更新 LLM 配置模块列表（basic, clarify, planner, query_generation, evaluate, report）
- [x] 验证搜索工具配置说明
- [x] 更新 API 获取链接说明

### 1.3 运行章节更新
- [x] 修正运行命令：`poetry run python -m src.run` → `python -m deepresearch.run`
- [x] 验证参考文档链接

### 1.4 其他更新
- [x] 验证文档头部版本号信息
- [x] 补充性能优化特性说明（可选）

## 任务 2：更新 doc/user_guide/user_guide.md

- [x] 修正模块导入路径：`from src.deepresearch.run` → 正确路径
- [x] 验证运行命令一致性
- [x] 验证示例代码正确性

## 任务 3：验证 doc/deployment/deployment.md 一致性

- [x] 检查运行命令与 intro.md 一致
- [x] 检查模块导入路径与 user_guide.md 一致
- [x] 验证配置示例与实际配置文件一致

## 任务 4：最终验证

- [x] 交叉检查所有文档一致性
- [x] 验证 RST 语法正确性
- [x] 确认所有链接可访问
