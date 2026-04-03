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
        self.references += reference

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

    def merge_knowledge(self):
        """
        Convert chapters and their sub chapters to Markdown text

        Returns:
            Generated Markdown string
        """
        groups = {}

        for knowledge in self.learning_knowledge:
            ref_tuple = tuple(sorted(knowledge["real_reference"]))

            if ref_tuple in groups:
                groups[ref_tuple].append(knowledge["insight"])
            else:
                groups[ref_tuple] = [knowledge["insight"]]

        merged = []
        for ref_tuple, insights in groups.items():
            merged_insight = "\n\n".join(insights)
            merged_ref = list(ref_tuple)
            merged.append({"insight": merged_insight, "real_reference": merged_ref})
        self.learning_knowledge = merged
        return self

    def get_knowledge_str(self) -> str:
        if self.learning_knowledge:
            return json.dumps([{'id': i, 'content': knowledge["insight"]} for i, knowledge in enumerate(self.learning_knowledge)])
        else:
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
