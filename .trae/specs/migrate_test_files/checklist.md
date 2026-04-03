# 测试文件迁移检查清单

## 迁移前检查
- [x] 已识别所有需要迁移的测试文件
- [x] 已确认目标目录结构
- [x] 已备份重要文件（如有必要）

## 文件迁移检查
- [x] `src/deepresearch/mcp_client/test_mcp.py` 已移动到 `tests/unit/mcp_client/test_mcp.py`
- [x] `src/deepresearch/agent/test_agent.py` 已移动到 `tests/unit/agent/test_agent_from_src.py`
- [x] `concurrency_test.py` 已移动到 `tests/performance/concurrency_test.py`
- [x] `stability_test.py` 已移动到 `tests/performance/stability_test.py`

## 导入路径检查
- [x] `tests/unit/mcp_client/test_mcp.py` 中的导入路径已正确更新
- [x] `tests/unit/agent/test_agent_from_src.py` 中的导入路径已正确更新
- [x] `tests/performance/concurrency_test.py` 中的导入路径已正确更新
- [x] `tests/performance/stability_test.py` 中的导入路径已正确更新

## 源文件清理检查
- [x] `src/deepresearch/mcp_client/test_mcp.py` 已删除
- [x] `src/deepresearch/agent/test_agent.py` 已删除
- [x] `concurrency_test.py`（根目录）已删除
- [x] `stability_test.py`（根目录）已删除

## 测试执行检查
- [x] `tests/unit/mcp_client/test_mcp.py` 可以正常执行且通过
- [x] `tests/unit/agent/test_agent_from_src.py` 可以正常执行且通过
- [x] `tests/performance/concurrency_test.py` 可以正常执行
- [x] `tests/performance/stability_test.py` 可以正常执行
- [x] 原有测试套件 `tests/unit/agent/test_agent.py` 仍然可以正常执行
- [x] 所有其他原有测试文件仍然可以正常执行

## 最终验证
- [x] 项目根目录下没有测试文件（除 `tests` 目录外）
- [x] `src` 目录下没有测试文件
- [x] 所有测试文件都位于 `tests` 目录下的正确位置
- [x] 运行完整测试套件无错误
