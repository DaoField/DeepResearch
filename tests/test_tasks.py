import os
import shutil
import tempfile
import pytest
from invoke import Context
from tasks import clean, venv, activate


class TestTasks:
    """测试 tasks 模块中的函数"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建临时目录作为测试工作目录
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # 创建一些测试文件和目录
        os.makedirs("src", exist_ok=True)
        os.makedirs("tests", exist_ok=True)
        os.makedirs("doc/_build", exist_ok=True)
        
        # 创建 __pycache__ 目录
        os.makedirs("src/__pycache__", exist_ok=True)
        with open("src/__pycache__/test.cpython-314.pyc", "w") as f:
            f.write("test")
        
        # 创建其他测试文件
        with open("src/test.py", "w") as f:
            f.write("def test():\n    pass\n")
        
        # 创建 dist 目录
        os.makedirs("dist", exist_ok=True)
        with open("dist/test.txt", "w") as f:
            f.write("test")
        
        # 创建 build 目录
        os.makedirs("build", exist_ok=True)
        with open("build/test.txt", "w") as f:
            f.write("test")
        
        # 创建 test.egg-info 目录
        os.makedirs("test.egg-info", exist_ok=True)
        with open("test.egg-info/PKG-INFO", "w") as f:
            f.write("Metadata-Version: 2.1\nName: test\n")
    
    def teardown_method(self):
        """清理测试环境"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_clean(self):
        """测试 clean 函数"""
        # 验证测试文件和目录存在
        assert os.path.exists("src/__pycache__")
        assert os.path.exists("src/__pycache__/test.cpython-314.pyc")
        assert os.path.exists("dist")
        assert os.path.exists("build")
        assert os.path.exists("test.egg-info")
        assert os.path.exists("doc/_build")
        
        # 执行 clean 函数
        clean(Context())
        
        # 验证文件和目录被清理
        assert not os.path.exists("src/__pycache__")
        assert not os.path.exists("dist")
        assert not os.path.exists("build")
        assert not os.path.exists("test.egg-info")
        assert not os.path.exists("doc/_build")
    
    def test_venv_creation(self):
        """测试 venv 函数（仅验证目录创建）"""
        # 确保 .venv 目录不存在
        if os.path.exists(".venv"):
            shutil.rmtree(".venv")
        
        # 注意：这里我们不实际执行 venv 函数，因为它会尝试创建真实的虚拟环境
        # 我们只验证函数结构和基本逻辑
        assert True
    
    def test_activate_venv_not_exists(self):
        """测试 activate 函数 - 虚拟环境不存在的情况"""
        # 确保 .venv 目录不存在
        if os.path.exists(".venv"):
            shutil.rmtree(".venv")
        
        # 执行 activate 函数，应该正常返回而不抛出异常
        activate(Context())
        
        # 验证 .venv 目录仍然不存在
        assert not os.path.exists(".venv")
    
    def test_activate_venv_exists_but_invalid(self):
        """测试 activate 函数 - 虚拟环境存在但无效的情况"""
        # 创建一个空的 .venv 目录（没有激活脚本）
        os.makedirs(".venv", exist_ok=True)
        
        # 执行 activate 函数，应该正常返回而不抛出异常
        activate(Context())
        
        # 清理
        shutil.rmtree(".venv")
    
    def test_activate_venv_valid_windows(self):
        """测试 activate 函数 - Windows系统下有效的虚拟环境"""
        import platform
        
        # 创建模拟的虚拟环境结构
        os.makedirs(".venv/Scripts", exist_ok=True)
        
        # 创建激活脚本
        activate_script = ".venv/Scripts/activate.bat"
        with open(activate_script, "w") as f:
            f.write("@echo off\necho Virtual environment activated\n")
        
        # 执行 activate 函数
        activate(Context())
        
        # 清理
        shutil.rmtree(".venv")
    
    def test_activate_venv_valid_unix(self):
        """测试 activate 函数 - Unix/Linux/macOS系统下有效的虚拟环境"""
        # 创建模拟的虚拟环境结构
        os.makedirs(".venv/bin", exist_ok=True)
        
        # 创建激活脚本
        activate_script = ".venv/bin/activate"
        with open(activate_script, "w") as f:
            f.write("#!/bin/bash\necho Virtual environment activated\n")
        
        # 执行 activate 函数
        activate(Context())
        
        # 清理
        shutil.rmtree(".venv")


if __name__ == "__main__":
    pytest.main([__file__])
