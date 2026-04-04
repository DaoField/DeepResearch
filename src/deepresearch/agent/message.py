# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from langgraph.graph import MessagesState


@dataclass
class Reference:
    ref_id: int
    source: str | None = None


@dataclass
class Chapter:
    id: int
    level: int | None = None
    title: str | None = None
    thinking: str | None = None
    summary: str | None = None
    sub_chapter: list[Chapter] = field(default_factory=list)
    parent_chapter: Chapter | None = None
    references: list[Reference] = field(default_factory=list)
    learning_knowledge: list[dict[str, Any]] = field(default_factory=list)

    def add_reference(self, reference: Reference | list[Reference]):
        if isinstance(reference, list):
            self.references.extend(reference)
        else:
            self.references.append(reference)

    def get_outline(self) -> str:
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

    def merge_knowledge(self) -> Chapter:
        if not self.learning_knowledge:
            return self

        groups: dict[tuple, list[str]] = {}

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
            valid_insights = [i for i in insights if i and i.strip()]
            if valid_insights:
                merged_insight = "\n\n".join(valid_insights)
                merged_ref = list(ref_tuple)
                merged.append({"insight": merged_insight, "real_reference": merged_ref})

        self.learning_knowledge = merged
        return self

    def get_knowledge_str(self) -> str:
        if not self.learning_knowledge:
            return "[]"
        try:
            return json.dumps(
                [
                    {"id": i, "content": knowledge.get("insight", "")}
                    for i, knowledge in enumerate(self.learning_knowledge)
                    if knowledge.get("insight", "").strip()
                ],
                ensure_ascii=False,
            )
        except (TypeError, ValueError):
            return "[]"


class ReportState(MessagesState):
    outline: Chapter
    messages: list
    topic: str
    domain: str
    logic: str
    details: str
    output: dict
    knowledge: list
    final_report: str
    search_id: int
