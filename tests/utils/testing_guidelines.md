# 测试规范标准

## 1. 目录结构

```
tests/
├── unit/            # 单元测试
│   ├── test_agent.py         # Agent 模块测试
│   ├── test_llms.py          # LLM 模块测试
│   ├── test_tools.py         # 工具模块测试
│   └── test_utils.py         # 工具函数测试
├── integration/     # 集成测试
│   ├── test_workflow.py      # 工作流集成测试
│   ├── test_search.py        # 搜索功能集成测试
│   └── test_generation.py    # 生成功能集成测试
├── performance/     # 性能测试
│   ├── test_performance.py   # 性能测试
│   └── analyze_performance.py # 性能分析
├── e2e/             # 端到端测试
│   ├── test_full_process.py  # 全流程测试
│   └── test_user_scenario.py # 用户场景测试
├── utils/           # 测试工具
│   ├── testing_guidelines.md # 本文档
│   └── test_helpers.py       # 测试辅助函数
└── reports/         # 测试报告
    └── v1.1.1/     # 版本报告
```

## 2. 命名规范

### 文件名
- 单元测试文件: `test_模块名.py`
- 集成测试文件: `test_功能名.py`
- 性能测试文件: `test_performance.py`
- 端到端测试文件: `test_场景名.py`

### 测试函数
- 单元测试函数: `test_功能名`
- 集成测试函数: `test_集成场景`
- 性能测试函数: `test_性能指标`
- 端到端测试函数: `test_用户场景`

## 3. 测试类型

### 单元测试
- 测试单个模块或函数的功能
- 隔离测试，不依赖外部服务
- 应覆盖主要功能和边界情况

### 集成测试
- 测试多个模块之间的交互
- 可以依赖外部服务的模拟
- 应覆盖关键的集成路径

### 性能测试
- 测试系统的性能指标
- 包括响应时间、资源使用等
- 应在不同负载下测试

### 端到端测试
- 测试完整的用户场景
- 模拟真实用户操作
- 应覆盖主要的用户流程

## 4. 测试框架

- 使用 `pytest` 作为测试框架
- 使用 `pytest-cov` 进行覆盖率测试
- 使用 `mock` 库模拟外部依赖

## 5. 测试用例设计

### 基本原则
- 每个测试用例应测试一个特定的功能点
- 测试用例应具有独立性
- 测试用例应可重复执行
- 测试用例应覆盖正常和异常情况

### 测试数据
- 使用真实的测试数据
- 避免硬编码测试数据
- 使用测试数据生成器

### 断言
- 使用明确的断言语句
- 断言应测试预期的行为
- 断言应包含有意义的错误信息

## 6. 测试执行

### 本地执行
- 运行特定测试: `pytest tests/unit/test_agent.py`
- 运行所有测试: `pytest`
- 运行测试并生成覆盖率报告: `pytest --cov=src`

### CI/CD 执行
- 在 CI/CD 流程中自动执行测试
- 测试失败时阻止合并
- 生成测试报告和覆盖率报告

## 7. 测试报告

### 报告内容
- 测试结果摘要
- 测试覆盖率报告
- 性能测试报告
- 失败测试的详细信息

### 报告格式
- 使用 Markdown 格式
- 包含测试执行时间
- 包含测试环境信息

## 8. 最佳实践

### 测试编写
- 测试代码应与生产代码一样高质量
- 测试应易于理解和维护
- 测试应反映实际使用场景

### 测试维护
- 代码变更时应更新相关测试
- 定期运行测试确保功能正常
- 及时修复失败的测试

### 测试覆盖
- 目标覆盖率: 80% 以上
- 重点覆盖核心功能
- 覆盖关键的业务逻辑

## 9. 工具推荐

- `pytest`: 测试框架
- `pytest-cov`: 覆盖率测试
- `mock`: 模拟库
- `psutil`: 系统资源监控
- `timeit`: 性能测试

## 10. 模板

### 单元测试模板
```python
import pytest
from src.module import function


def test_function_normal_case():
    """测试正常情况"""
    result = function(input)
    assert result == expected


def test_function_edge_case():
    """测试边界情况"""
    result = function(edge_input)
    assert result == expected


def test_function_error_case():
    """测试错误情况"""
    with pytest.raises(Exception):
        function(error_input)
```

### 集成测试模板
```python
import pytest
from src.agent.agent import build_agent


@pytest.fixture
def agent():
    return build_agent()


def test_agent_workflow(agent):
    """测试 Agent 工作流"""
    # 测试代码
    pass
```

### 性能测试模板
```python
import time
import psutil

def test_performance():
    """测试性能"""
    start_time = time.time()
    # 执行测试
    end_time = time.time()
    response_time = end_time - start_time
    assert response_time < threshold
```

## 11. 版本控制

- 测试代码应与生产代码一起版本控制
- 测试数据应存储在版本控制系统中
- 测试报告应定期生成并存档
