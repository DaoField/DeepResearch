# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

import os
import random
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx


class SortOrder(str, Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class SortBy(str, Enum):
    RELEVANCE = "relevance"
    SUBMITTED_DATE = "submittedDate"
    LAST_UPDATED_DATE = "lastUpdatedDate"


@dataclass
class Query:
    """
    Query class for ArXiv API search requests.

    Attributes:
        max_page_number: Maximum number of pages to retrieve.
        terms: Search query terms.
        page_number: Starting page number (zero-based).
        max_results_per_page: Maximum results per page.
        article_ids: List of specific article IDs to retrieve.
        sort_by: Sorting criteria.
        sort_order: Sorting direction.
        throttle_seconds: Delay between pagination requests (seconds).
    """

    max_page_number: int = 0
    terms: str = ""
    page_number: int = 0
    max_results_per_page: int = 10
    article_ids: list[str] = field(default_factory=list)
    sort_by: SortBy | None = None
    sort_order: SortOrder | None = None
    throttle_seconds: int = 3

    def validate(self) -> str | None:
        """
        Validate the query parameters.

        Returns:
            Error message if validation fails, None otherwise.
        """
        if not self.article_ids and not self.terms:
            return "Either article_ids or terms must be provided"
        return None

    def prepare_for_pagination(self) -> None:
        """
        Prepare query parameters for pagination.
        Ensures page_number and max_results_per_page are valid.
        """
        if self.page_number <= 0:
            self.page_number = 0

        if self.max_results_per_page <= 0:
            self.max_results_per_page = 10

    def to_url_params(self) -> dict[str, Any]:
        """
        Convert query parameters to URL parameters dictionary.

        Returns:
            Dictionary of URL parameters.
        """
        params = {
            "search_query": self.terms,
            "start": self.page_number,
            "max_results": self.max_results_per_page,
        }

        if self.article_ids:
            params["id_list"] = ",".join(self.article_ids)

        if self.sort_by:
            params["sortBy"] = self.sort_by.value

        if self.sort_order:
            params["sortOrder"] = self.sort_order.value

        return params


@dataclass
class Link:
    """
    Represents a link element in ArXiv response.

    Attributes:
        rel: Link relationship type.
        href: Link URL.
        type: Link content type.
        title: Link title.
    """

    rel: str | None = None
    href: str = ""
    type: str | None = None
    title: str | None = None


@dataclass
class Person:
    """
    Represents an author in ArXiv response.

    Attributes:
        name: Author's name.
        uri: Author's URI.
        email: Author's email.
    """

    name: str = ""
    uri: str | None = None
    email: str | None = None


@dataclass
class Text:
    """
    Represents text content in ArXiv response.

    Attributes:
        type: Text type.
        body: Text content.
    """

    type: str | None = None
    body: str = ""


@dataclass
class Entry:
    """
    Represents a paper entry in ArXiv response.

    Attributes:
        title: Paper title.
        id: Paper identifier.
        link: List of links related to the paper.
        published: Publication date.
        updated: Last updated date.
        author: List of authors.
        summary: Paper summary.
        content: Paper content.
    """

    title: str = ""
    id: str = ""
    link: list[Link] = field(default_factory=list)
    published: str = ""
    updated: str = ""
    author: list[Person] = field(default_factory=list)
    summary: Text | None = None
    content: Text | None = None


@dataclass
class Feed:
    """
    Represents the main feed in ArXiv response.

    Attributes:
        title: Feed title.
        id: Feed identifier.
        link: List of feed links.
        updated: Last updated date.
        entry: List of paper entries.
    """

    title: str = ""
    id: str = ""
    link: list[Link] = field(default_factory=list)
    updated: str = ""
    entry: list[Entry] = field(default_factory=list)


@dataclass
class ResultsPage:
    """
    Represents a page of search results.

    Attributes:
        feed: Feed containing the results.
        page_number: Current page number.
        error: Error message if any.
    """

    feed: Feed | None = None
    page_number: int = 0
    error: str | None = None


class Client:
    """
    Client for interacting with ArXiv API.

    Attributes:
        base_url: Base URL for ArXiv API.
        recommended_throttle_duration: Recommended delay between requests.
        _client: httpx.Client for HTTP connections.
    """

    def __init__(self):
        self.base_url = "https://export.arxiv.org"
        self.recommended_throttle_duration = 3
        self._client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )

    def __del__(self):
        if hasattr(self, "_client"):
            self._client.close()

    def parse_atom_feed(self, xml_content: bytes) -> Feed:
        """
        Parse XML content into a Feed object.

        Args:
            xml_content: XML content from ArXiv API response.

        Returns:
            Parsed Feed object.
        """
        namespaces = {"atom": "http://www.w3.org/2005/Atom"}

        root = ET.fromstring(xml_content)

        feed = Feed()

        title_elem = root.find("./atom:title", namespaces)
        if title_elem is not None:
            feed.title = title_elem.text or ""

        id_elem = root.find("./atom:id", namespaces)
        if id_elem is not None:
            feed.id = id_elem.text or ""

        updated_elem = root.find("./atom:updated", namespaces)
        if updated_elem is not None:
            feed.updated = updated_elem.text or ""

        for link_elem in root.findall("./atom:link", namespaces):
            link = Link(
                rel=link_elem.get("rel"),
                href=link_elem.get("href", ""),
                type=link_elem.get("type"),
                title=link_elem.get("title"),
            )
            feed.link.append(link)

        for entry_elem in root.findall("./atom:entry", namespaces):
            entry = Entry()

            title_elem = entry_elem.find("./atom:title", namespaces)
            if title_elem is not None:
                entry.title = title_elem.text or ""

            id_elem = entry_elem.find("./atom:id", namespaces)
            if id_elem is not None:
                entry.id = id_elem.text or ""

            published_elem = entry_elem.find("./atom:published", namespaces)
            if published_elem is not None:
                entry.published = published_elem.text or ""

            updated_elem = entry_elem.find("./atom:updated", namespaces)
            if updated_elem is not None:
                entry.updated = updated_elem.text or ""

            for link_elem in entry_elem.findall("./atom:link", namespaces):
                link = Link(
                    rel=link_elem.get("rel"),
                    href=link_elem.get("href", ""),
                    type=link_elem.get("type"),
                    title=link_elem.get("title"),
                )
                entry.link.append(link)

            for author_elem in entry_elem.findall("./atom:author", namespaces):
                person = Person()
                name_elem = author_elem.find("./atom:name", namespaces)
                if name_elem is not None:
                    person.name = name_elem.text or ""

                uri_elem = author_elem.find("./atom:uri", namespaces)
                if uri_elem is not None:
                    person.uri = uri_elem.text

                email_elem = author_elem.find("./atom:email", namespaces)
                if email_elem is not None:
                    person.email = email_elem.text

                entry.author.append(person)

            summary_elem = entry_elem.find("./atom:summary", namespaces)
            if summary_elem is not None:
                entry.summary = Text(
                    type=summary_elem.get("type"), body=summary_elem.text or ""
                )

            content_elem = entry_elem.find("./atom:content", namespaces)
            if content_elem is not None:
                entry.content = Text(
                    type=content_elem.get("type"), body=content_elem.text or ""
                )

            feed.entry.append(entry)

        return feed

    def search(self, query: Query) -> list[ResultsPage]:
        """
        Search ArXiv for papers matching the query.

        Args:
            query: Search query parameters.

        Returns:
            List of ResultsPage objects containing the search results.
        """
        error_msg = query.validate()
        if error_msg:
            return [ResultsPage(error=error_msg)]

        query.prepare_for_pagination()

        throttle_duration = self.recommended_throttle_duration
        if query.throttle_seconds >= 1:
            throttle_duration = query.throttle_seconds
        elif query.throttle_seconds <= -1:
            throttle_duration = 0

        results = []
        current_query = Query(**query.__dict__)

        while True:
            result_page = ResultsPage(page_number=current_query.page_number)

            try:
                url = f"{self.base_url}/api/query"
                params = current_query.to_url_params()

                response = self._client.get(url, params=params)
                response.raise_for_status()

                feed = self.parse_atom_feed(response.content)
                result_page.feed = feed

                results.append(result_page)

                if not feed.entry:
                    break

                current_query.page_number += 1
                if (
                    query.max_page_number > 0
                    and current_query.page_number >= query.max_page_number
                ):
                    break

                if throttle_duration > 0:
                    _backoff = min(
                        throttle_duration * (2 ** min(results.index(result_page), 5)),
                        30.0,
                    ) + random.uniform(0, 1)
                    time.sleep(_backoff)

            except Exception as e:
                result_page.error = str(e)
                results.append(result_page)
                break

        return results

    def download_paper(self, paper_id: str, parent_path: str) -> str | None:
        """
        Download a paper by its ID.

        Args:
            paper_id: ArXiv paper ID.
            parent_path: Directory to save the downloaded paper.

        Returns:
            Error message if download fails, None otherwise.
        """
        file_path = os.path.join(parent_path, f"{paper_id}.pdf")
        if os.path.exists(file_path):
            return None

        os.makedirs(parent_path, exist_ok=True)

        try:
            url = f"{self.base_url}/pdf/{paper_id}"

            with self._client.stream("GET", url, timeout=60.0) as response:
                response.raise_for_status()

                with open(file_path, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            return None

        except Exception as e:
            return str(e)


default_client = Client()


def search(query: Query) -> list[ResultsPage]:
    """
    Convenience function to search using the default client.

    Args:
        query: Search query parameters.

    Returns:
        List of ResultsPage objects containing the search results.
    """
    return default_client.search(query)


def download_paper(paper_id: str, parent_path: str) -> str | None:
    """
    Convenience function to download a paper using the default client.

    Args:
        paper_id: ArXiv paper ID.
        parent_path: Directory to save the downloaded paper.

    Returns:
        Error message if download fails, None otherwise.
    """
    return default_client.download_paper(paper_id, parent_path)
