#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM 模块单元测试
"""

import unittest
from src.deepresearch.llms.llm import _get_llm_instance, llm
from src.deepresearch.llms.llm import LLMType
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class TestLLM(unittest.TestCase):
    """LLM 模块测试类"""

    def test_get_llm_instance(self):
        """测试获取 LLM 实例"""
        # 测试获取 basic LLM 实例
        llm_instance = _get_llm_instance("basic", streaming=False)
        self.assertIsNotNone(llm_instance)

        # 测试获取 clarify LLM 实例
        llm_instance = _get_llm_instance("clarify", streaming=False)
        self.assertIsNotNone(llm_instance)

        # 测试获取 planner LLM 实例
        llm_instance = _get_llm_instance("planner", streaming=False)
        self.assertIsNotNone(llm_instance)

        # 测试获取 query_generation LLM 实例
        llm_instance = _get_llm_instance("query_generation", streaming=False)
        self.assertIsNotNone(llm_instance)

        # 测试获取 evaluate LLM 实例
        llm_instance = _get_llm_instance("evaluate", streaming=False)
        self.assertIsNotNone(llm_instance)

        # 测试获取 report LLM 实例
        llm_instance = _get_llm_instance("report", streaming=False)
        self.assertIsNotNone(llm_instance)

    def test_llm_caching(self):
        """测试 LLM 响应缓存"""
        # 准备测试消息
        messages = [
            HumanMessage(content="测试消息")
        ]

        # 第一次调用 llm 函数
        response1 = llm("basic", messages, stream=False)
        self.assertIsInstance(response1, str)
        self.assertNotEqual(len(response1), 0)

        # 第二次调用 llm 函数，应该使用缓存
        response2 = llm("basic", messages, stream=False)
        self.assertIsInstance(response2, str)
        self.assertEqual(response1, response2)


if __name__ == '__main__':
    unittest.main()
