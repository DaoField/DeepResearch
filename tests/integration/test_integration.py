#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集成测试
测试模块间的交互
"""

import unittest
from src.deepresearch.llms.llm import llm
from src.deepresearch.prompts.template import apply_prompt_template
from langchain_core.messages import HumanMessage, SystemMessage


class TestIntegration(unittest.TestCase):
    """集成测试类"""

    def test_llm_and_prompt_integration(self):
        """测试 LLM 和 prompt 模板的集成"""
        # 准备测试数据
        state = {
            "topic": "人工智能",
            "messages": [HumanMessage(content="人工智能的发展趋势")]
        }

        # 应用 prompt 模板
        messages = apply_prompt_template("classify", state)
        self.assertIsInstance(messages, list)
        self.assertGreater(len(messages), 0)

        # 调用 LLM
        response = llm("basic", messages, stream=False)
        self.assertIsInstance(response, str)
        self.assertNotEqual(len(response), 0)


if __name__ == '__main__':
    unittest.main()
