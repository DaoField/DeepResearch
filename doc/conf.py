# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime
from pathlib import Path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DeepResearch'
copyright = f'{datetime.now().year}, iFLYTEK'
author = 'iFLYTEK'

try:
    from importlib.metadata import version as _pkg_version
    release = _pkg_version("deepresearch")
except Exception:
    release = os.environ.get("DEEPRESEARCH_VERSION", "1.1.1")

version = release.rsplit('.', 1)[0] if '.' in release else release

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'myst_parser',
    'sphinxcontrib.mermaid',
    'sphinx_design',
    'sphinx_copybutton',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**/__pycache__']

language = 'zh_CN'

# -- Extension configuration -------------------------------------------------

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_preprocess_types = True
napoleon_type_aliases = {
    'Callable': 'typing.Callable',
    'Dict': 'typing.Dict',
    'List': 'typing.List',
    'Optional': 'typing.Optional',
    'Tuple': 'typing.Tuple',
    'Union': 'typing.Union',
}

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
    'imported-members': True,
}
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'
autodoc_inherit_docstrings = True
autodoc_mock_imports = ['langchain', 'langgraph', 'langchain_deepseek']

# Autosummary settings
autosummary_generate = True
autosummary_generate_overwrite = True
autosummary_imported_members = True

# Intersphinx settings for linking to external documentation
intersphinx_mapping = {
    'python': ('https://docs.python.org/zh-cn/3.14/', None),
    'sphinx': ('https://www.sphinx-doc.org/zh-cn/master/', None),
    'langchain': ('https://python.langchain.com/docs/', None),
}

# Todo extension settings
todo_include_todos = True

# Myst Parser settings
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
myst_heading_anchors = 3
myst_footnote_transition = True
myst_dmath_double_inline = True

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'xyzstyle'
html_static_path = ['_static']
html_last_updated_fmt = '%Y-%m-%d %H:%M'
html_use_smartypants = True
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'sourcelink.html',
    ]
}

# Theme options from _config.toml
html_theme_options = {}
try:
    import tomllib as _tomllib
    cfg_path = Path(__file__).parent / "_config.toml"
    if cfg_path.exists():
        _cfg = _tomllib.loads(cfg_path.read_text('utf-8'))
        html_theme_options = _cfg.get('html_theme_options', {})
except Exception:
    pass

# -- Options for HTML help output --------------------------------------------
htmlhelp_basename = 'DeepResearchdoc'

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
    'preamble': r'''
\usepackage{ctex}
\usepackage{fontspec}
''',
    'babel': r'\usepackage[english]{babel}',
}

latex_documents = [
    ('index', 'DeepResearch.tex', 'DeepResearch 文档', 'iFLYTEK', 'manual'),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    ('index', 'deepresearch', 'DeepResearch 文档', ['iFLYTEK'], 1),
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    ('index', 'DeepResearch', 'DeepResearch 文档', 'iFLYTEK', 'DeepResearch',
     '深度研究框架', 'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ['search.html']

# -- Path setup --------------------------------------------------------------
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../src'))

# -- Coverage configuration --------------------------------------------------
coverage_ignore_modules = [
    'tests.*',
    'tests',
]
coverage_ignore_functions = [
    'main',
    '__repr__',
    '__str__',
]
coverage_ignore_classes = []

# -- Doctest configuration ---------------------------------------------------
doctest_default_flags = (
    doctest.ELLIPSIS
    | doctest.IGNORE_EXCEPTION_DETAIL
    | doctest.DONT_ACCEPT_TRUE_FOR_1
    | doctest.NORMALIZE_WHITESPACE
)
