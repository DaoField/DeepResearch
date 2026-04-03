
from invoke import task
from taolib.doc import sites

# 导入文档站点功能
namespace = sites('doc', target='doc/_build/html')


@task
def test(c):
    """运行项目测试"""
    c.run("pytest tests/", pty=True)


@task
def format(c):
    """使用 black 格式化代码"""
    c.run("black src/", pty=True)


@task
def lint(c):
    """使用 flake8 检查代码风格"""
    c.run("flake8 src/", pty=True)


@task
def typecheck(c):
    """使用 mypy 进行类型检查"""
    c.run("mypy src/", pty=True)


@task
def clean(c):
    """清理临时文件和构建产物"""
    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/.pytest_cache",
        "**/.mypy_cache",
        "dist",
        "build",
        "*.egg-info",
        "doc/_build",
    ]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}", hide=True, warn=True)


@task(pre=[clean, test, format, lint])
def all(c):
    """运行所有检查和测试"""
    print("✅ 所有检查完成！")
