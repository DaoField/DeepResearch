# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

import logging
from typing import *

import requests

from deepresearch.config.search_config import search_config
from deepresearch.tools._search import SearchClient, SearchResult

logger = logging.getLogger(__name__)


class JinaSearchClient(SearchClient):
    """Client for searching web using Jina HTTP API"""

    def __init__(self):
        # Initialize configuration from search config
        self._url = "https://s.jina.ai/"
        self._headers = {
            "Authorization": f"Bearer {search_config.jina_api_key}",
            "Accept": "application/json",
            "X-Retain-Images": "none",
            "X-Timeout": str(search_config.timeout),
        }

    def search(self, query: str, top_n: int) -> list[SearchResult]:
        """
        Perform a web search and retrieve results

        Args:
            query: Search query string
            top_n: Number of results to retrieve

        Returns:
            List of SearchResult objects containing search information
        """
        search_results: list[SearchResult] = []
        if not query or not query.strip():
            return search_results

        try:
            params = {
                "q": query.strip(),
                "num": min(max(top_n, 1), 20),  # 限制范围 1-20
            }
            response = requests.get(
                self._url,
                headers=self._headers,
                params=params,
                timeout=search_config.timeout,
            )
            response.raise_for_status()
            result = response.json()
            for i, data in enumerate(result.get("data", [])):
                url = data.get("url", "").strip()
                if not url:  # 跳过无效URL
                    continue
                search_results.append(
                    SearchResult(
                        url=url,
                        title=data.get("title", "") or "Untitled",
                        summary=data.get("description", ""),
                        content=data.get("content", ""),
                        date=data.get("publishedTime", ""),
                        id=i,
                    )
                )
        except requests.exceptions.Timeout:
            logger.error(f"Jina search timeout for query: {query[:50]}...")
        except requests.exceptions.RequestException as e:
            logger.error(f"Jina search request error: {e}")
        except Exception as e:
            logger.error(f"Error in Jina search: {e}")
        return search_results


if __name__ == "__main__":
    # Example usage
    client = JinaSearchClient()
    query = "What is the best pc game in 2024?"
    top_n = 5
    results = client.search(query, top_n)
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"Title: {result.title}")
        print(f"Summary: {result.summary}")
        print(f"Content: {result.content[:200]}...")
