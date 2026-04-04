# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_core.runnables import RunnableConfig

from deepresearch.config.workflow_config import workflow_configs
from deepresearch.tools.search import SearchResult

from .deepsearch import DeepSearch, DeepSearchResult
from .message import ReportState


def learning_node(state: ReportState, config: RunnableConfig):
    outline = state.get("outline")
    knowledge = state.get("knowledge", [])
    search_id = state.get("search_id", 1)
    # Thread-safe counter for search_id allocation
    search_id_lock = threading.Lock()
    knowledge_lock = threading.Lock()
    chapter_results = [None] * len(outline.sub_chapter)

    def _process_chapter(idx_and_chapter):
        idx, chapter = idx_and_chapter
        ds = DeepSearch(
            outline.title,
            chapter.title,
            [title for title in chapter.sub_chapter],
            chapter.summary,
            config.get("configurable", {}).get("depth", 3),
            workflow_configs.get("search", {}).get("topN", 5),
        )
        results = ds.deep_search()
        search_results = get_all_search_results(results)
        local_knowledge = []
        local_search_id_start = 0

        with search_id_lock:
            nonlocal search_id
            local_search_id_start = search_id
            for key, value in search_results.items():
                for i, result in enumerate(value):
                    local_knowledge.append(
                        {
                            "id": search_id + i,
                            "content": result.content,
                            "url": result.url,
                        }
                    )
                search_id += len(value)

        learning_knowledge = [
            {
                "insight": re_knowledge.insight,
                "real_reference": [],
            }  # placeholder, filled after merge
            for re_knowledge in results.re_knowledge
        ]
        return (idx, results, local_knowledge, learning_knowledge, search_results)

    chapters = list(enumerate(outline.sub_chapter))
    max_workers = min(
        len(chapters), 3
    )  # Bound concurrency to avoid overwhelming LLM APIs
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_chapter, ch): ch for ch in chapters}
        for future in as_completed(futures):
            idx, results, local_knowledge, learning_knowledge, search_results = (
                future.result()
            )
            chapter_results[idx] = (results, learning_knowledge)
            with knowledge_lock:
                knowledge.extend(local_knowledge)
                # Fill real_reference IDs now that global knowledge is available
                for lk in learning_knowledge:
                    re_knowledge = results.re_knowledge[learning_knowledge.index(lk)]
                    if hasattr(re_knowledge, "references") and re_knowledge.references:
                        lk["real_reference"] = get_real_reference_ids(
                            knowledge, re_knowledge.references
                        )

    # Assign learning_knowledge back to chapters in order
    for idx, chapter in enumerate(outline.sub_chapter):
        if chapter_results[idx] is not None:
            _, learning_knowledge = chapter_results[idx]
            chapter.learning_knowledge = learning_knowledge

    return {
        "outline": outline,
        "search_id": search_id,
        "knowledge": knowledge,
    }


def get_all_search_results(result: DeepSearchResult) -> list[SearchResult]:
    search_result = {}
    while result:
        search_result = search_result | result.search_result
        result = result.children
    return search_result


def get_real_reference_ids(
    search_results: list, references: list[SearchResult]
) -> list[int]:
    """获取真实引用ID列表，去重并排序"""
    if not search_results or not references:
        return []

    url_to_id = {
        search.get("url"): search.get("id")
        for search in search_results
        if search.get("url")
    }

    reference_ids = []
    seen = set()

    for reference in references:
        if reference and reference.url and reference.url in url_to_id:
            ref_id = url_to_id[reference.url]
            if ref_id is not None and ref_id not in seen:
                reference_ids.append(ref_id)
                seen.add(ref_id)

    reference_ids.sort()
    return reference_ids
