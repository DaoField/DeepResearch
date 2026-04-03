# 测试文件迁移任务列表

## [x] 任务 1：迁移 mcp_client 测试文件
- **优先级**：P0
- **依赖**：无
- **描述**：
  - 创建 `tests/unit/mcp_client/` 目录（如不存在）
  - 将 `src/deepresearch/mcp_client/test_mcp.py` 移动到 `tests/unit/mcp_client/test_mcp.py`
  - 检查并更新文件中的导入路径
  - 验证测试文件可以正常执行
- **验收标准**：AC-1, AC-2, AC-3

## [x] 任务 2：迁移 agent 测试文件
- **优先级**：P0
- **依赖**：无
- **描述**：
  - 检查 `tests/unit/agent/test_agent.py` 与 `src/deepresearch/agent/test_agent.py` 的内容差异
  - 将 `src/deepresearch/agent/test_agent.py` 移动到 `tests/unit/agent/test_agent_from_src.py`
  - 检查并更新文件中的导入路径
  - 验证测试文件可以正常执行
- **验收标准**：AC-1, AC-2, AC-3, AC-4

## [x] 任务 3：迁移性能测试文件
- **优先级**：P0
- **依赖**：无
- **描述**：
  - 创建 `tests/performance/` 目录（如不存在）
  - 将 `concurrency_test.py` 移动到 `tests/performance/concurrency_test.py`
  - 将 `stability_test.py` 移动到 `tests/performance/stability_test.py`
  - 检查并更新文件中的导入路径
  - 验证测试文件可以正常执行
- **验收标准**：AC-1, AC-2, AC-3

## [x] 任务 4：清理源文件
- **优先级**：P1
- **依赖**：任务 1, 任务 2, 任务 3
- **描述**：
  - 删除已迁移的源文件
  - 确认源文件已成功删除
  - 确保没有遗留的测试文件在项目根目录或 src 目录下
- **验收标准**：AC-1

## [x] 任务 5：验证测试套件
- **优先级**：P0
- **依赖**：任务 1, 任务 2, 任务 3, 任务 4
- **描述**：
  - 运行完整的测试套件
  - 确保所有测试用例通过
  - 生成测试执行报告
- **验收标准**：AC-3

# 任务依赖关系
- 任务 4 依赖于任务 1, 任务 2, 任务 3
- 任务 5 依赖于任务 1, 任务 2, 任务 3, 任务 4
