
from invoke import task
from taolib.doc import sites
import subprocess
import sys
import platform
import os

"""任务定义模块

本模块使用 Invoke 库定义了项目的各种任务，包括测试、代码格式化、
代码检查、类型检查、清理和虚拟环境创建等功能。
"""

# 导入文档站点功能
# 创建文档站点命名空间，目标目录为 doc/_build/html
namespace = sites('doc', target='doc/_build/html')


@task
def test(c):
    """运行项目测试
    
    使用 pytest 运行 tests/ 目录下的所有测试用例，
    确保项目功能正常。
    
    Args:
        c: Invoke 上下文对象，用于执行命令
    """
    try:
        c.run("pytest tests/", pty=True)
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        raise


@task
def format(c):
    """使用 ruff 格式化代码
    
    使用 ruff 工具格式化 src/ 目录下的所有 Python 代码，
    确保代码风格一致。
    
    Args:
        c: Invoke 上下文对象，用于执行命令
    """
    try:
        c.run("ruff format src/", pty=True)
    except Exception as e:
        print(f"❌ 代码格式化失败: {e}")
        raise


@task
def lint(c):
    """使用 ruff 检查代码风格
    
    使用 ruff 工具检查 src/ 目录下的所有 Python 代码，
    确保代码符合 PEP 8 规范。
    
    Args:
        c: Invoke 上下文对象，用于执行命令
    """
    try:
        c.run("ruff check src/", pty=True)
    except Exception as e:
        print(f"❌ 代码风格检查失败: {e}")
        raise


@task
def typecheck(c):
    """使用 mypy 进行类型检查
    
    使用 mypy 工具检查 src/ 目录下的所有 Python 代码，
    确保类型注解正确。
    
    Args:
        c: Invoke 上下文对象，用于执行命令
    """
    try:
        c.run("mypy src/", pty=True)
    except Exception as e:
        print(f"❌ 类型检查失败: {e}")
        raise


@task
def clean(c):
    """清理临时文件和构建产物
    
    使用 Python 标准库的 glob 和 shutil 模块，
    跨平台清理项目中的临时文件和构建产物，
    包括 __pycache__ 目录、编译后的 Python 文件、
    测试缓存、类型检查缓存、分发和构建目录等。
    
    Args:
        c: Invoke 上下文对象，用于执行命令
    """
    import shutil
    import glob
    
    # 需要清理的文件和目录模式
    patterns = [
        "**/__pycache__",          # Python 编译缓存目录
        "**/*.pyc",                # 编译后的 Python 文件
        "**/*.pyo",                # 优化编译的 Python 文件
        "**/*.pyd",                # Python 动态链接库
        "**/.pytest_cache",        # pytest 缓存目录
        "**/.mypy_cache",          # mypy 类型检查缓存目录
        "dist",                    # 分发目录
        "build",                   # 构建目录
        "*.egg-info",              # 包信息目录
        "doc/_build",              # 文档构建目录
    ]
    
    for pattern in patterns:
        # 使用 glob 查找匹配的文件和目录
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            try:
                if os.path.isdir(match):
                    # 删除目录及其所有内容
                    shutil.rmtree(match)
                else:
                    # 删除文件
                    os.remove(match)
            except Exception as e:
                # 忽略删除失败的情况，继续清理其他文件
                pass


@task(pre=[clean, test, format, lint])
def all(c):
    """运行所有检查和测试
    
    依次执行以下任务：
    1. clean: 清理临时文件和构建产物
    2. test: 运行项目测试
    3. format: 使用 ruff 格式化代码
    4. lint: 使用 ruff 检查代码风格
    
    完成后输出成功信息。
    
    Args:
        c: Invoke 上下文对象，用于执行命令
    """
    print("✅ 所有检查完成！")


@task
def venv(c):
    """创建Python 3.14虚拟环境
    
    检查系统Python版本，确保为3.14或更高版本，
    然后创建或重新创建虚拟环境，并验证虚拟环境的正确性。
    
    Args:
        c: Invoke 上下文对象，用于执行命令
    """
    print("🔍 检查系统Python版本...")
    
    try:
        # 检查系统Python版本
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ 无法检测Python版本")
            return
        
        python_version = result.stdout.strip()
        print(f"📦 当前系统Python版本: {python_version}")
        
        # 更可靠的Python版本检查
        import re
        version_match = re.search(r"Python (\d+)\.(\d+)", python_version)
        if not version_match:
            print("❌ 无法解析Python版本")
            return
        
        major, minor = map(int, version_match.groups())
        if major != 3 or minor < 14:
            print("❌ 系统未安装Python 3.14版本或更高版本")
            print("📥 请先安装Python 3.14或更高版本")
            print("🔗 下载地址: https://www.python.org/downloads/")
            return
        
        # 检查虚拟环境目录是否已存在
        venv_dir = ".venv"
        if os.path.exists(venv_dir):
            print(f"⚠️  虚拟环境目录 '{venv_dir}' 已存在")
            print("🔄 重新创建虚拟环境...")
            # 清理现有虚拟环境
            import shutil
            try:
                shutil.rmtree(venv_dir)
            except Exception as e:
                print(f"⚠️  清理现有虚拟环境失败: {e}")
                return
        
        # 创建虚拟环境
        print(f"🚀 创建Python 3.14虚拟环境 '{venv_dir}'...")
        result = subprocess.run(
            [sys.executable, "-m", "venv", venv_dir],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ 创建虚拟环境失败")
            print(f"错误信息: {result.stderr}")
            return
        
        print("✅ 虚拟环境创建成功")
        
        # 确定激活脚本路径
        if platform.system() == "Windows":
            activate_script = os.path.join(venv_dir, "Scripts", "activate.bat")
        else:
            activate_script = os.path.join(venv_dir, "bin", "activate")
        
        print(f"📝 激活虚拟环境的命令:")
        if platform.system() == "Windows":
            print(f"  {activate_script}")
        else:
            print(f"  source {activate_script}")
        
        # 验证虚拟环境
        print("🔍 验证虚拟环境...")
        if platform.system() == "Windows":
            python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            python_exe = os.path.join(venv_dir, "bin", "python")
        
        # 检查Python可执行文件是否存在
        if not os.path.exists(python_exe):
            print(f"❌ 虚拟环境Python可执行文件不存在: {python_exe}")
            return
        
        result = subprocess.run(
            [python_exe, "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            venv_version = result.stdout.strip()
            print(f"✅ 虚拟环境Python版本: {venv_version}")
            # 再次检查版本
            venv_version_match = re.search(r"Python (\d+)\.(\d+)", venv_version)
            if venv_version_match:
                venv_major, venv_minor = map(int, venv_version_match.groups())
                if venv_major == 3 and venv_minor >= 14:
                    print("🎉 虚拟环境成功创建并使用Python 3.14+版本")
                else:
                    print("⚠️  虚拟环境Python版本不是3.14+")
        else:
            print("❌ 无法验证虚拟环境")
            print(f"错误信息: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n📋 后续步骤:")
    print("1. 激活虚拟环境")
    print("2. 安装项目依赖: pip install -e .")
    print("3. 运行项目: deepresearch")


@task
def activate(c):
    r"""激活Python虚拟环境
    
    自动检测项目根目录下的.venv文件夹，根据操作系统执行相应的激活命令：
    - Windows系统：执行 .venv\Scripts\activate.bat
    - Unix/Linux/macOS系统：执行 source .venv/bin/activate
    
    提供明确的成功/失败状态反馈，帮助用户确认虚拟环境是否成功激活。
    
    Args:
        c: Invoke 上下文对象，用于执行命令
    """
    venv_dir = ".venv"
    
    # 检查虚拟环境目录是否存在
    if not os.path.exists(venv_dir):
        print(f"❌ 虚拟环境目录 '{venv_dir}' 不存在")
        print("📥 请先创建虚拟环境: invoke venv")
        return
    
    # 检查虚拟环境目录是否为有效目录
    if not os.path.isdir(venv_dir):
        print(f"❌ '{venv_dir}' 不是有效的目录")
        return
    
    # 根据操作系统确定激活脚本路径和命令
    system = platform.system()
    
    if system == "Windows":
        # Windows系统
        activate_script = os.path.join(venv_dir, "Scripts", "activate.bat")
        activate_cmd = f"call {activate_script}"
        shell_cmd = f"cmd /c {activate_cmd}"
    else:
        # Unix/Linux/macOS系统
        activate_script = os.path.join(venv_dir, "bin", "activate")
        activate_cmd = f"source {activate_script}"
        shell_cmd = f"bash -c '{activate_cmd}'"
    
    # 检查激活脚本是否存在
    if not os.path.exists(activate_script):
        print(f"❌ 激活脚本不存在: {activate_script}")
        print("⚠️  虚拟环境可能已损坏或未正确创建")
        print("🔄 建议重新创建虚拟环境: invoke venv")
        return
    
    print(f"🔍 检测到操作系统: {system}")
    print(f"📂 虚拟环境目录: {os.path.abspath(venv_dir)}")
    print(f"📝 激活脚本路径: {activate_script}")
    
    try:
        # 尝试执行激活命令
        print(f"🚀 正在激活虚拟环境...")
        
        # 使用subprocess执行激活命令
        result = subprocess.run(
            shell_cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 虚拟环境激活命令执行成功")
            print(f"\n📋 手动激活命令:")
            if system == "Windows":
                print(f"  {activate_script}")
                print(f"\n💡 或者在PowerShell中使用:")
                print(f"  .\\{venv_dir}\\Scripts\\Activate.ps1")
            else:
                print(f"  {activate_cmd}")
            
            print(f"\n🔍 验证激活状态:")
            print(f"  激活后，命令行提示符前会显示 '({venv_dir})'")
            print(f"  可以运行 'which python' 或 'where python' 查看Python路径")
        else:
            print(f"❌ 虚拟环境激活失败")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return


namespace.add_task(venv)
namespace.add_task(activate)
namespace.add_task(all)
namespace.add_task(clean)
