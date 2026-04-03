#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prompt 模板模块单元测试
"""

import unittest
from src.deepresearch.prompts.template import load_prompt_templates, apply_prompt_template, load_prompt_templates_lazy
from langchain_core.messages import HumanMessage, SystemMessage


class TestPromptTemplate(unittest.TestCase):
    """Prompt 模板模块测试类"""

    def test_load_prompt_templates(self):
        """测试加载 prompt 模板"""
        templates = load_prompt_templates()
        self.assertIsInstance(templates, dict)
        self.assertGreater(len(templates), 0)

    def test_load_prompt_templates_lazy(self):
        """测试懒加载 prompt 模板"""
        templates = load_prompt_templates_lazy()
        self.assertIsInstance(templates, dict)
        self.assertGreater(len(templates), 0)

    def test_apply_prompt_template(self):
        """测试应用 prompt 模板"""
        # 测试 classify 模板
        state = {
            "topic": "人工智能",
            "messages": [HumanMessage(content="人工智能的发展趋势")]
        }
        messages = apply_prompt_template("classify", state)
        self.assertIsInstance(messages, list)
        self.assertGreater(len(messages), 0)

        # 测试 clarify 模板
        state = {
            "topic": "人工智能",
            "messages": [HumanMessage(content="人工智能的发展趋势")]
        }
        messages = apply_prompt_template("clarify", state)
        self.assertIsInstance(messages, list)
        self.assertGreater(len(messages), 0)

        # 测试 planner 模板
        state = {
            "topic": "人工智能",
            "messages": [HumanMessage(content="人工智能的发展趋势")]
        }
        messages = apply_prompt_template("planner", state)
        self.assertIsInstance(messages, list)
        self.assertGreater(len(messages), 0)


if __name__ == '__main__':
    unittest.main()
