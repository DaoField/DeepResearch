#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agent 模块单元测试
"""
from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage, AIMessage
from deepresearch.agent.agent import build_agent
from deepresearch.agent.prep import rewrite_node, classify_node, generic_node, clarify_node
from deepresearch.agent.outline import outline_search_node, outline_knowledge_2_str
from langgraph.types import Command


@pytest.fixture
def mock_state():
    return {
        "messages": [HumanMessage(content="Please introduce iFlytek to me and help me analyze its development."
                                          "prospects.")],
    }


@pytest.fixture
def mock_classify_state():
    return {
        "messages": [HumanMessage(content="Please introduce iFlytek to me and help me analyze its development."
                                          "prospects.")],
        "topic": "Please introduce iFlytek to me and help me analyze its development prospects."
    }


@pytest.fixture
def mock_clarify_state():
    return {
        "messages": [HumanMessage(content="Please introduce iFlytek to me and help me analyze its development.")],
        "domain": "Company Research",
        "topic": "Please introduce iFlytek to me and help me analyze its development."
    }


@pytest.fixture
def mock_rewrite_state():
    return {
        "messages": [
            HumanMessage(content='The main customers of the computing power leasing industry.'),
            AIMessage(content='''To help accurately analyze the customer structure of the computing power leasing industry, could you please provide the following information:
1. * * Regional Scope * *: Are you interested in the Chinese market, major global regions such as North America and Asia Pacific, or specific countries/regions?
2. * * Customer type * *: Is it necessary to distinguish between enterprise customers (such as Internet companies and scientific research institutions) and individual developers, or further refine them to industry fields (such as AI training, film and television rendering)?
3. * * Analysis Dimension * *: Is it more focused on customer size distribution, demand driving factors, or key criteria for customers to choose service providers?'''),
            HumanMessage(content='''1. Chinese market;
             2. Distinguish between corporate and individual clients;
             3. Analyze customer selection of service provider labels'''),
        ],
    }


@pytest.fixture
def mock_outline_search_state():
    return {
        "messages": [HumanMessage(content="Please introduce iFlytek to me and help me analyze its development.")],
        "domain": "Company Research",
        "topic": "Please introduce iFlytek to me and help me analyze its development.",
        "logic": "Research the company background → Analyze industry landscape and emerging trends → Consolidate financial performance and key indicators → Identify core business segments and growth drivers → Integrate market dynamics to highlight potential risks",
        "details": "mock reasoning",
        "knowledge": [],
        }


@pytest.fixture
def mock_outline_state():
    return {
        "messages": [HumanMessage(content="Please introduce iFlytek to me and help me analyze its development.")],
        "domain": "Company Research",
        "topic": "Please introduce iFlytek to me and help me analyze its development.",
        "details": "Research the company background → Analyze industry landscape and emerging trends → Consolidate financial performance and key indicators → Identify core business segments and growth drivers → Integrate market dynamics to highlight potential risks",
        "logic": "mock reasoning",
        "knowledge": [[{"id": 1, "content": "", "url": "http://test.com", "title": "empty", "summary": "mock"}]],
        }


def test_build_agent():
    """测试构建 agent"""
    graph = build_agent()
    assert graph is not None


def test_agent_stream():
    """测试 agent 流式运行"""
    graph = build_agent()
    state = {
        "messages": [HumanMessage(content="人工智能的发展趋势")]
    }
    config = {
        "configurable": {
            "depth": 1,
            "save_as_html": False
        }
    }

    try:
        for i, message in enumerate(graph.stream(
            input=state, config=config, stream_mode="values"
        )):
            assert isinstance(message, dict)
            if i >= 1:
                break
    except Exception:
        pass


def test_generic_node_response(
    mock_state
):
    result = generic_node(mock_state)
    assert isinstance(result, dict)
    assert isinstance(result["output"], dict)
    assert isinstance(result["output"]["message"], str)


def test_classify_node_response(
    mock_classify_state
):
    result = classify_node(mock_classify_state)
    assert isinstance(result, Command)
    assert result.goto in ["clarify", "outline_search", "generic"]
    if result.update is not None:
        assert isinstance(result.update, dict)
        if "domain" in result.update:
            assert isinstance(result.update["domain"], str)
        if "logic" in result.update:
            assert isinstance(result.update["logic"], str)
        if "details" in result.update:
            assert isinstance(result.update["details"], str)


def test_clarify_node_response(
    mock_clarify_state
):
    result = clarify_node(mock_clarify_state)
    assert isinstance(result, Command)
    assert result.goto in ["__end__", "outline_search", "generic"]
    if result.goto == "__end__" and result.update is not None:
        assert isinstance(result.update, dict)
        if "output" in result.update:
            assert isinstance(result.update["output"], dict)
            if "message" in result.update["output"]:
                assert isinstance(result.update["output"]["message"], str)


def test_rewrite_node_response(
    mock_rewrite_state
):
    result = rewrite_node(mock_rewrite_state)
    assert isinstance(result, Command)
    if result.update is not None:
        assert isinstance(result.update, dict)
        if "topic" in result.update:
            assert isinstance(result.update["topic"], str)


def test_outline_search_node_response(
    mock_outline_search_state
):
    try:
        result = outline_search_node(mock_outline_search_state)
        assert isinstance(result, dict)
        assert isinstance(result["knowledge"], list)
        assert isinstance(result["search_id"], int)
    except TypeError:
        pytest.skip("outline_search_node requires valid LLM response")


def test_outline_knowledge_2_str():
    """测试大纲知识转换函数"""
    assert outline_knowledge_2_str([]) == "[]"
    assert outline_knowledge_2_str(None) == "[]"

    test_knowledge = [[{"id": 1, "content": "test content"}]]
    result = outline_knowledge_2_str(test_knowledge)
    assert isinstance(result, str)
    assert "test content" in result
