# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from langgraph.graph import END, START, StateGraph

from .generate import generate_node, save_local_node, save_report_local
from .learning import learning_node
from .message import ReportState
from .outline import outline_node, outline_search_node
from .prep import (
    clarify_node,
    classify_node,
    generic_node,
    preprocess_node,
    rewrite_node,
)


def build_agent():
    """Build and return the base state graph with all nodes and edges."""
    agent = StateGraph(ReportState)
    agent.add_edge(START, "preprocess")
    agent.add_node("preprocess", preprocess_node)
    agent.add_node("rewrite", rewrite_node)
    agent.add_node("classify", classify_node)
    agent.add_node("clarify", clarify_node)
    agent.add_node("generic", generic_node)
    agent.add_node("outline_search", outline_search_node)
    agent.add_node("outline", outline_node)
    agent.add_node("learning", learning_node)
    agent.add_node("generate", generate_node)
    agent.add_node("save_local_node", save_local_node)

    agent.add_edge("rewrite", "classify")
    agent.add_edge("outline_search", "outline")
    agent.add_edge("learning", "generate")
    agent.add_conditional_edges(
        "generate",
        save_report_local,
        ["save_local_node", END],
    )
    agent.add_edge("generic", END)

    return agent.compile()
