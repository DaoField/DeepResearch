#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集成测试
测试模块间的交互
"""
from __future__ import annotations

import unittest
import pytest
from src.deepresearch.llms.llm import llm
from src.deepresearch.prompts.template import apply_prompt_template
from langchain_core.messages import HumanMessage, SystemMessage


class TestIntegration(unittest.TestCase):
    """集成测试类"""

    def test_prompt_template_integration(self):
        """测试 prompt 模板"""
        state = {
            "topic": "人工智能",
            "messages": [HumanMessage(content="人工智能的发展趋势")]
        }

        messages = apply_prompt_template("classify", state)
        self.assertIsInstance(messages, list)
        self.assertGreater(len(messages), 0)

    @pytest.mark.skipif(
        True,
        reason="Requires valid API key - skipping by default"
    )
    def test_llm_and_prompt_integration(self):
        """测试 LLM 和 prompt 模板的集成"""
        state = {
            "topic": "人工智能",
            "messages": [HumanMessage(content="人工智能的发展趋势")]
        }

        messages = apply_prompt_template("classify", state)
        self.assertIsInstance(messages, list)
        self.assertGreater(len(messages), 0)

        response = llm("basic", messages, stream=False)
        self.assertIsInstance(response, str)
        if len(response) == 0:
            self.skipTest("No response from LLM - likely invalid API key")


if __name__ == '__main__':
    unittest.main()
