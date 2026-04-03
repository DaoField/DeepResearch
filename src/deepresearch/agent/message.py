# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License
import json
from dataclasses import dataclass, field

from langgraph.graph import MessagesState
from typing import List, Optional, Any, Dict


@dataclass
class Reference:
    ref_id: int  # 对应Go的RefId
    source: Optional[str] = None


@dataclass
class Chapter:
    id: int
    level: Optional[int] = None
    title: Optional[str] = None
    thinking: Optional[str] = None
    summary: Optional[str] = None
    sub_chapter: List["Chapter"] = field(default_factory=list)
    parent_chapter: Optional["Chapter"] = None
    references: List[Reference] = field(default_factory=list)
    learning_knowledge: List[Dict[str, Any]] = field(default_factory=list)

    def add_reference(self, reference: Reference | List[Reference]):
        """添加引用到章节"""
        if isinstance(reference, list):
            self.references.extend(reference)
        else:
            self.references.append(reference)

    def get_outline(self) -> str:
        """
        Convert chapters and their sub chapters to Markdown text

        Returns:
            Generated Markdown string
        """
        markdown_parts = []

        if self.title and self.level is not None:
            level = max(1, self.level)
            title_line = f"{'#' * level} {self.title}"
            markdown_parts.append(title_line)

        if self.thinking:
            markdown_parts.append(self.thinking.strip())

        if self.summary:
            markdown_parts.append(self.summary.strip())

        for sub in self.sub_chapter:
            sub_markdown = sub.get_outline()
            if sub_markdown:
                markdown_parts.append(sub_markdown)

        return "\n\n".join(markdown_parts)

    def merge_knowledge(self) -> "Chapter":
        """
        合并具有相同引用的知识点，避免重复内容
        
        Returns:
            返回自身以支持链式调用
        """
        if not self.learning_knowledge:
            return self
            
        groups: Dict[tuple, List[str]] = {}

        for knowledge in self.learning_knowledge:
            real_ref = knowledge.get("real_reference", [])
            if not isinstance(real_ref, list):
                real_ref = [real_ref] if real_ref else []
            ref_tuple = tuple(sorted(real_ref))

            if ref_tuple in groups:
                groups[ref_tuple].append(knowledge.get("insight", ""))
            else:
                groups[ref_tuple] = [knowledge.get("insight", "")]

        merged = []
        for ref_tuple, insights in groups.items():
            # 过滤空字符串
            valid_insights = [i for i in insights if i and i.strip()]
            if valid_insights:
                merged_insight = "\n\n".join(valid_insights)
                merged_ref = list(ref_tuple)
                merged.append({"insight": merged_insight, "real_reference": merged_ref})
        
        self.learning_knowledge = merged
        return self

    def get_knowledge_str(self) -> str:
        """获取知识点的JSON字符串表示"""
        if not self.learning_knowledge:
            return "[]"
        try:
            return json.dumps([
                {'id': i, 'content': knowledge.get("insight", "")} 
                for i, knowledge in enumerate(self.learning_knowledge)
                if knowledge.get("insight", "").strip()
            ], ensure_ascii=False)
        except (TypeError, ValueError) as e:
            return "[]"


class ReportState(MessagesState):
    # Report outline
    outline: Chapter
    # User request
    messages: List
    # Report topic, rewritten by user request
    topic: str
    # domain
    domain: str
    logic: str
    details: str
    output: dict
    knowledge: list
    # Final report
    final_report: str
    # Do you want to save the final report as a html
    search_id: int
