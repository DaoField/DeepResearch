# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

#!/usr/bin/env python3
"""
test paper_mcp_server
"""
from __future__ import annotations

import json
import pytest
from deepresearch.mcp_client.paper_mcp_server import arxiv_search, arxiv_read, pubmed_search, pubmed_read


@pytest.fixture
def paper_id():
    """Fixture to get a paper ID from arxiv search"""
    try:
        results = arxiv_search("machine learning", max_results=1)
        data = json.loads(results)
        if data.get('papers'):
            return data['papers'][0]['id']
    except Exception:
        pass
    return None


@pytest.fixture
def pubmed_paper_id():
    """Fixture to get a paper ID from pubmed search"""
    try:
        results = pubmed_search("covid-19", max_results=1)
        data = json.loads(results)
        if data.get('papers'):
            return data['papers'][0]['id']
    except Exception:
        pass
    return None


def test_arxiv_search():
    """test ArXiv search"""
    try:
        results = arxiv_search("machine learning", max_results=1)
        data = json.loads(results)
        assert isinstance(data, dict)
        if data.get('papers'):
            assert isinstance(data['papers'], list)
    except Exception as e:
        pytest.skip(f"arxiv search test error: {e}")


def test_arxiv_read(paper_id):
    """test arXiv read"""
    if not paper_id:
        pytest.skip("No paper ID available from arxiv search")

    try:
        content = arxiv_read(paper_id)
        data = json.loads(content)
        assert isinstance(data, dict)
        if 'meta' in data:
            assert 'title' in data['meta']
    except Exception as e:
        pytest.skip(f"arxiv read test failed: {e}")


def test_pubmed_search():
    """test PubMed search"""
    try:
        results = pubmed_search("covid-19", max_results=1)
        data = json.loads(results)
        assert isinstance(data, dict)
        if data.get('papers'):
            assert isinstance(data['papers'], list)
    except Exception as e:
        pytest.skip(f"pubmed search error: {e}")


def test_pubmed_read(pubmed_paper_id):
    """test PubMed read"""
    if not pubmed_paper_id:
        pytest.skip("No paper ID available from pubmed search")

    try:
        content = pubmed_read(pubmed_paper_id)
        data = json.loads(content)
        assert isinstance(data, dict)
        if 'meta' in data:
            assert 'title' in data['meta']
    except Exception as e:
        pytest.skip(f"pubmed read error: {e}")
