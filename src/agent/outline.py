# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License
import json
from typing import List

from .message import ReportState, Chapter
from src.llms.llm import llm
from src.prompts.template import apply_prompt_template
from src.utils.print_util import colored_print
from langgraph.types import Command
from src.tools.search import SearchClient
from src.config.workflow_config import workflow_configs
import logging
from datetime import datetime
import re
from src.utils.parse_model_res import extract_xml_content

logger = logging.getLogger(__name__)


def outline_search_node(state: ReportState):
    """Search some knowledge for outline."""
    sq = llm(llm_type="query_generation", messages=apply_prompt_template(
        prompt_name="outline/outline_sq",
        state={
            "now": datetime.now().strftime("%a %b %d %Y"),
            "query": state.get("topic"),
            "reasoning": state.get("logic")
        }
    ), stream=False)
    search_queries = extract_xml_content(sq, "search")
    search_client = SearchClient()
    search_id = state.get("search_id", 1)
    outline_knowledge = state.get("knowledge", [])

    # Parallel search execution with bounded concurrency
    from concurrent.futures import ThreadPoolExecutor, as_completed
    max_workers = min(len(search_queries), 5)

    def _single_outline_search(search_query):
        colored_print(f'Searching: {search_query}', color="purple")
        results = search_client.search(search_query,
                                             workflow_configs.
                                             get("search", {}).
                                             get("topN", 5))
        for result in results:
            colored_print(f'{result.title} -- ', color="cyan", end="")
            colored_print(result.url, color="blue", underline=True)
        return (search_query, results)

    if search_queries and max_workers > 0:
        # Use thread-safe ordered collection
        collected = [None] * len(search_queries)
        query_index = {q: i for i, q in enumerate(search_queries)}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {executor.submit(_single_outline_search, q): q for q in search_queries}
            for future in as_completed(future_map):
                q, results = future.result()
                idx = query_index[q]
                collected[idx] = (q, results)
        # Apply results in original order to maintain deterministic search_id assignment
        for item in collected:
            if item is None:
                continue
            q, results = item
            outline_knowledge += [
                {"id": search_id + i, "content": result.content, "url": result.url}
                for i, result in enumerate(results)
            ]
            search_id += len(results)
    else:
        # Fallback: sequential processing for empty queries or edge cases
        pass

    return {
        "search_id": search_id,
        "knowledge": outline_knowledge,
    }

def outline_node(state: ReportState):
    """Generate outline for this report"""
    outline = ""
    for think, content in llm(llm_type="planner", messages=apply_prompt_template(
            prompt_name="outline/outline",
            state={
                "domain": state.get("domain"),
                "now": datetime.now().strftime("%a %b %d %Y"),
                "query": state.get("topic"),
                "reasoning": state.get("logic"),
                "thinking": state.get("details"),
                "reference": outline_knowledge_2_str(state.get("outline_knowledge", ""))
            }
    ), stream=True):
        if think:
            colored_print(think, color="orange", end="")
        if content:
            outline += content
    try:
        chapter = parse_outline(outline)
    except ValueError as e:
        logger.error(f"outline is invalid: {outline}")
        return Command(goto="__end__",
                      update={
                          "output": {
                              "message": outline
                          }})
    colored_print("\n\n" + chapter.get_outline(), color="green", end="")
    return Command(goto="learning", update={
        "outline": chapter
    })


def outline_knowledge_2_str(outline_knowledge, max_length=100000):
    """
    Convert outline knowledge list to JSON string with max_length truncation.
    Optimized: Single-pass O(N) traversal with proper null handling.
    """
    if not outline_knowledge:
        return "[]"
        
    result = []
    total_length = 0

    # Single pass: flatten all knowledge items in order, truncate at max_length
    for knowledge in outline_knowledge:
        if not isinstance(knowledge, list):
            continue
        for item in knowledge:
            if not isinstance(item, dict):
                continue
            content = item.get("content", "") or ""
            if total_length + len(content) > max_length:
                break
            result.append({"content": content, "id": item.get("id", 0)})
            total_length += len(content)
        # Early exit if limit reached
        if total_length >= max_length:
            break

    try:
        return json.dumps(result, ensure_ascii=False)
    except (TypeError, ValueError):
        return "[]"


markdown_regexp = re.compile(r'(?s)```\s*markdown\n(.*)```')
title_regexp = re.compile(r'^(#+)\s+(.*)')


def parse_outline(outline_str: str) -> Chapter:
    # 使用markdown_regexp提取markdown代码块内容
    markdown_match = markdown_regexp.search(outline_str)
    if markdown_match:
        outline_str = markdown_match.group(1)

    root = Chapter(id=0, level=0)
    current_chapter = root
    id_counter = 0
    title_list: List[str] = []

    lines = outline_str.split('\n')

    # 解析标题并构建章节结构
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 使用title_regexp匹配标题格式
        title_match = title_regexp.match(line)
        if title_match:
            id_counter += 1
            level = len(title_match.group(1))
            title = title_match.group(2)

            # 找到合适的父节点
            # 增加安全检查，防止current_chapter为None
            while current_chapter and current_chapter.level >= level:
                current_chapter = current_chapter.parent_chapter

            # 再次检查current_chapter是否为None
            if not current_chapter:
                current_chapter = root

            # 创建新章节
            new_chapter = Chapter(id=id_counter, level=level, title=title, parent_chapter=current_chapter)

            current_chapter.sub_chapter.append(new_chapter)
            current_chapter = new_chapter
            title_list.append(title_match.group(0))
        else:
            summary_match = extract_xml_content(line, "summary")
            if summary_match:
                current_chapter.summary = summary_match[0]

            # 使用thinking_regexp提取思路
            thinking_match = extract_xml_content(line, "thinking")
            if thinking_match:
                current_chapter.thinking = thinking_match[0]

    if not root.sub_chapter:
        raise ValueError("no valid chapter found")

    # 清理根节点的父引用
    root_chapter = root.sub_chapter[0]
    root_chapter.parent_chapter = None
    parent_to_nil(root_chapter.sub_chapter)

    # 转换为字典
    return root_chapter


def parent_to_nil(chapters: List[Chapter]) -> None:
    for chapter in chapters:
        chapter.parent_chapter = None
        parent_to_nil(chapter.sub_chapter)
