# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DeepResearch'
copyright = '2026, iFLYTEK'
author = 'iFLYTEK'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'myst_parser',
    'sphinxcontrib.mermaid',
    'sphinx_design',
    # 代码相关
    "sphinx.ext.viewcode",  # 在文档中展示源码并提供跳转
    'sphinx_copybutton',  # 为代码块提供“一键复制”按钮
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'zh_CN'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'xyzstyle'
html_static_path = ['_static']

# === 主题选项加载（从 _config.toml） ===
html_theme_options = {}  # 主题选项：由主题定义具体可用项，默认空 dict
try:
    # tomllib：Python 3.11+ 标准库。若运行在更低版本或解析失败，则忽略并使用默认值。
    import tomllib as _tomllib
    from pathlib import Path
    cfg_path = Path(__file__).parent / "_config.toml"  # doc/_config.toml：集中存放主题/站点个性化配置
    if cfg_path.exists():
        _cfg = _tomllib.loads(cfg_path.read_text('utf-8'))  # 读取并解析 TOML 文本
        html_theme_options = _cfg.get('html_theme_options', {})  # 从 TOML 中提取主题选项
except Exception:
    # 容错策略：配置解析失败不应阻塞文档构建（避免 CI 因非关键配置中断）
    pass

# -- Extension configuration -------------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/configuration.html

# 配置Myst Parser以支持Markdown文件
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# 配置源文件后缀
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# 添加路径以便能够导入代码
sys.path.insert(0, os.path.abspath('..'))
