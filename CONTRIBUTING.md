# Contributing to DeepResearch

Thank you for your interest in contributing to DeepResearch! We welcome contributions of all kinds from the community.

## What you can contribute

The list below mentions some contributions you can make, but it is not a complete list.:

- **Code Contributions**: Add new features, fix bugs, or improve performance
- **Documentation**: Improve README, add code comments, or create examples
- **Bug Reports**: Submit detailed bug reports through issues
- **Feature Requests**: Suggest new features or improvements
- **Community Support**: Help others in discussions and issues

## Development Setup

### 环境要求

- Python版本: >= 3.10, < 4.0
- 构建系统: scikit-build-core >= 0.10

### 1. Fork and Clone

```bash
git clone git@github.com:<yourname>/DeepResearch.git
cd DeepResearch
```

### 2. 安装开发依赖

本项目使用 [scikit-build-core](https://scikit-build-core.readthedocs.io/) 作为构建系统，支持以下安装方式：

#### 方式一：使用 pip 进行开发安装（推荐）

```bash
# 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 以可编辑模式安装，包含开发依赖
pip install -e ".[dev]"
```



### 3. 验证安装

安装完成后，验证开发环境是否配置正确：

```bash
# 检查项目是否正确安装
python -c "import deepresearch; print(deepresearch.__version__)"

# 运行测试套件
make test
```

## 开发依赖说明

项目的开发依赖包括以下工具：

- **invoke**: 任务运行工具
- **black**: 代码格式化工具
- **flake8**: 代码风格检查工具
- **mypy**: 静态类型检查工具

安装开发依赖：

```bash
pip install -e ".[dev]"
```

## Development Process

1. Create a new branch:
   ```bash
   git checkout -b feature/feature-name   # e.g., feature/text-summarization
   ```

2. Make your changes following our coding standards:
   - Write clear, documented code
   - Follow PEP 8 style guidelines
   - Add tests for new features
   - Update documentation as needed

3. Run tests and checks:
   ```bash
   make format    # Format code
   make test      # Run tests
   make coverage  # Check test coverage
   ```

4. Commit your changes:
   ```bash
   git commit -m 'Add a new feature'
   ```

5. Push to your fork:
   ```bash
   git push origin feature/feature-name
   ```

6. Submit a pull request for review.

## Pull Request Guidelines
- Fill in the pull request template completely
- Include tests for new features
- Update documentation as needed
- Keep pull requests focused on a single feature or fix
- Reference any related issues

## Code Style
- Follow PEP 8 guidelines
- Write descriptive docstrings
- Keep functions and methods focused and single-purpose
- Comment complex logic
- Python version requirement: >= 3.10, < 4.0

## Testing
Run the test suite:
```bash
# Run all tests
make test

# Run specific test file
pytest src/agent/test_agent.py

# Run with coverage
make coverage
```

## Community Guidelines
- Be respectful and inclusive
- Follow our Code of Conduct
- Help others learn and grow
- Give constructive feedback
- Stay focused on improving the project

## Need Help?
If you need help with anything:
- Check existing issues and discussions
- Join our community channels
- Ask questions in discussions

## License
By contributing to DeepResearch, you agree that your contributions will be licensed under the Apache 2.0 License.

We appreciate your contributions to making DeepResearch better!
