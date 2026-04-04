# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

import os
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

import httpx
from bs4 import BeautifulSoup

PUB_SEARCH_MED_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
SCI_HUB_URL = "https://sci-hub.se/"


@dataclass
class Author:
    last_name: str
    fore_name: str


@dataclass
class Article:
    title: str
    abstract: str | None = None
    authors: list[Author] = field(default_factory=list)
    year: str | None = None
    month: str | None = None


@dataclass
class MedlineCitation:
    pmid: str
    article: Article


@dataclass
class ArticleId:
    id: str
    id_type: str


@dataclass
class PubmedData:
    article_ids: list[ArticleId] = field(default_factory=list)


@dataclass
class PubMedArticle:
    medline_citation: MedlineCitation
    pubmed_data: PubmedData


@dataclass
class PubMedSearchResult:
    ids: list[str] = field(default_factory=list)


@dataclass
class PubMedFetchResult:
    articles: list[PubMedArticle] = field(default_factory=list)


class PubMedService:
    """
    Service for interacting with PubMed API to search and fetch articles.
    Provides both synchronous and asynchronous methods.
    """

    def __init__(self):
        self._timeout = httpx.Timeout(30.0)
        self._download_timeout = httpx.Timeout(60.0)

    def generate_pubmed_search_url(
        self, query: str, start_date: str, end_date: str, num_results: int
    ) -> str:
        """
        Generate URL for PubMed search API with given query parameters.

        Args:
            query: Search query string
            start_date: Start date in format "YYYY.MM.DD"
            end_date: End date in format "YYYY.MM.DD"
            num_results: Maximum number of results to return

        Returns:
            Formatted URL string for PubMed search API
        """
        keywords = query.split()
        query_parts = [urllib.parse.quote(kw) for kw in keywords]

        start_date_formatted = start_date.replace(".", "/")
        end_date_formatted = end_date.replace(".", "/")
        date_filter = f"{start_date_formatted}:{end_date_formatted}[Date - Publication]"
        query_parts.append(date_filter)

        params = {
            "db": "pubmed",
            "term": "+AND+".join(query_parts),
            "retmax": str(num_results),
            "retmode": "xml",
        }

        return f"{PUB_SEARCH_MED_URL}?{urllib.parse.urlencode(params)}"

    def search_pubmed(
        self, query: str, start_date: str, end_date: str, num_results: int
    ) -> PubMedSearchResult:
        """
        Search PubMed for articles matching the query.

        Args:
            query: Search query string
            start_date: Start date in format "YYYY.MM.DD"
            end_date: End date in format "YYYY.MM.DD"
            num_results: Maximum number of results to return

        Returns:
            PubMedSearchResult object containing list of article IDs
        """
        url = self.generate_pubmed_search_url(query, start_date, end_date, num_results)

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url)
                response.raise_for_status()

                root = ET.fromstring(response.content)
                id_list = []

                for id_elem in root.findall(".//Id"):
                    id_list.append(id_elem.text)

                return PubMedSearchResult(ids=id_list)

        except Exception as e:
            raise Exception(f"Error searching PubMed: {str(e)}")

    def fetch_articles(self, article_ids: list[str]) -> PubMedFetchResult:
        """
        Fetch detailed information for PubMed articles by their IDs.

        Args:
            article_ids: List of PubMed article IDs

        Returns:
            PubMedFetchResult object containing list of articles
        """
        if not article_ids:
            return PubMedFetchResult()

        params = {"db": "pubmed", "id": ",".join(article_ids), "retmode": "xml"}

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(PUBMED_FETCH_URL, params=params)
                response.raise_for_status()

                root = ET.fromstring(response.content)
                articles = []

                for article_elem in root.findall(".//PubmedArticle"):
                    medline_citation_elem = article_elem.find(".//MedlineCitation")
                    pmid = medline_citation_elem.find(".//PMID").text

                    article_elem_in = medline_citation_elem.find(".//Article")
                    title = (
                        article_elem_in.find(".//ArticleTitle").text
                        if article_elem_in.find(".//ArticleTitle") is not None
                        else ""
                    )

                    abstract_elem = article_elem_in.find(".//AbstractText")
                    abstract = abstract_elem.text if abstract_elem is not None else None

                    authors = []
                    for author_elem in article_elem_in.findall(".//Author"):
                        last_name_elem = author_elem.find(".//LastName")
                        fore_name_elem = author_elem.find(".//ForeName")

                        if last_name_elem is not None and fore_name_elem is not None:
                            authors.append(
                                Author(
                                    last_name=last_name_elem.text,
                                    fore_name=fore_name_elem.text,
                                )
                            )

                    year_elem = article_elem_in.find(".//PubDate/Year")
                    month_elem = article_elem_in.find(".//PubDate/Month")

                    year = year_elem.text if year_elem is not None else None
                    month = month_elem.text if month_elem is not None else None

                    article = Article(
                        title=title,
                        abstract=abstract,
                        authors=authors,
                        year=year,
                        month=month,
                    )

                    medline_citation = MedlineCitation(pmid=pmid, article=article)

                    pubmed_data_elem = article_elem.find(".//PubmedData")
                    article_ids_list = []

                    for article_id_elem in pubmed_data_elem.findall(".//ArticleId"):
                        article_id = ArticleId(
                            id=article_id_elem.text,
                            id_type=article_id_elem.get("IdType", ""),
                        )
                        article_ids_list.append(article_id)

                    pubmed_data = PubmedData(article_ids=article_ids_list)

                    pubmed_article = PubMedArticle(
                        medline_citation=medline_citation, pubmed_data=pubmed_data
                    )

                    articles.append(pubmed_article)

                return PubMedFetchResult(articles=articles)

        except Exception as e:
            raise Exception(f"Error fetching PubMed articles: {str(e)}")

    def download_pubmed_paper(self, doi: str, paper_id: str, parent_path: str) -> bool:
        """
        Download a paper from Sci-Hub using DOI or paper ID.

        Args:
            doi: DOI of the paper
            paper_id: Paper ID to use for saving the file
            parent_path: Directory to save the downloaded PDF

        Returns:
            True if download successful, False otherwise
        """
        save_path = os.path.join(parent_path, f"{paper_id}.pdf")
        if os.path.exists(save_path):
            return True

        try:
            os.makedirs(parent_path, exist_ok=True)

            page_url = f"{SCI_HUB_URL}{doi}"

            with httpx.Client(
                timeout=self._download_timeout, follow_redirects=True
            ) as client:
                response = client.get(page_url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                download_url = ""

                iframe = soup.find("iframe")
                if iframe and "src" in iframe.attrs and ".pdf" in iframe["src"]:
                    download_url = iframe["src"]

                if not download_url:
                    embed = soup.find("embed")
                    if embed and "src" in embed.attrs:
                        download_url = embed["src"]

                if download_url.startswith("//"):
                    download_url = f"https:{download_url}"
                elif not download_url.startswith("http"):
                    raise Exception("Could not find PDF download URL")

                pdf_response = client.get(download_url)
                pdf_response.raise_for_status()

                with open(save_path, "wb") as f:
                    f.write(pdf_response.content)

            return True

        except Exception as e:
            print(f"Error downloading paper {doi}: {str(e)}")
            return False

    async def download_pubmed_paper_async(
        self, doi: str, paper_id: str, parent_path: str
    ) -> bool:
        """
        Async version of download_pubmed_paper.

        Args:
            doi: DOI of the paper
            paper_id: Paper ID to use for saving the file
            parent_path: Directory to save the downloaded PDF

        Returns:
            True if download successful, False otherwise
        """
        save_path = os.path.join(parent_path, f"{paper_id}.pdf")
        if os.path.exists(save_path):
            return True

        try:
            os.makedirs(parent_path, exist_ok=True)

            page_url = f"{SCI_HUB_URL}{doi}"

            async with httpx.AsyncClient(
                timeout=self._download_timeout, follow_redirects=True
            ) as client:
                response = await client.get(page_url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                download_url = ""

                iframe = soup.find("iframe")
                if iframe and "src" in iframe.attrs and ".pdf" in iframe["src"]:
                    download_url = iframe["src"]

                if not download_url:
                    embed = soup.find("embed")
                    if embed and "src" in embed.attrs:
                        download_url = embed["src"]

                if download_url.startswith("//"):
                    download_url = f"https:{download_url}"
                elif not download_url.startswith("http"):
                    raise Exception("Could not find PDF download URL")

                pdf_response = await client.get(download_url)
                pdf_response.raise_for_status()

                with open(save_path, "wb") as f:
                    f.write(pdf_response.content)

            return True

        except Exception as e:
            print(f"Error downloading paper {doi}: {str(e)}")
            return False

    async def search_pubmed_async(
        self, query: str, start_date: str, end_date: str, num_results: int
    ) -> PubMedSearchResult:
        """
        Async version of search_pubmed.

        Args:
            query: Search query string
            start_date: Start date in format "YYYY.MM.DD"
            end_date: End date in format "YYYY.MM.DD"
            num_results: Maximum number of results to return

        Returns:
            PubMedSearchResult object containing list of article IDs
        """
        url = self.generate_pubmed_search_url(query, start_date, end_date, num_results)

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url)
                response.raise_for_status()

                root = ET.fromstring(response.content)
                id_list = []

                for id_elem in root.findall(".//Id"):
                    id_list.append(id_elem.text)

                return PubMedSearchResult(ids=id_list)

        except Exception as e:
            raise Exception(f"Error searching PubMed: {str(e)}")

    async def fetch_articles_async(self, article_ids: list[str]) -> PubMedFetchResult:
        """
        Async version of fetch_articles.

        Args:
            article_ids: List of PubMed article IDs

        Returns:
            PubMedFetchResult object containing list of articles
        """
        if not article_ids:
            return PubMedFetchResult()

        params = {"db": "pubmed", "id": ",".join(article_ids), "retmode": "xml"}

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(PUBMED_FETCH_URL, params=params)
                response.raise_for_status()

                root = ET.fromstring(response.content)
                articles = []

                for article_elem in root.findall(".//PubmedArticle"):
                    medline_citation_elem = article_elem.find(".//MedlineCitation")
                    pmid = medline_citation_elem.find(".//PMID").text

                    article_elem_in = medline_citation_elem.find(".//Article")
                    title = (
                        article_elem_in.find(".//ArticleTitle").text
                        if article_elem_in.find(".//ArticleTitle") is not None
                        else ""
                    )

                    abstract_elem = article_elem_in.find(".//AbstractText")
                    abstract = abstract_elem.text if abstract_elem is not None else None

                    authors = []
                    for author_elem in article_elem_in.findall(".//Author"):
                        last_name_elem = author_elem.find(".//LastName")
                        fore_name_elem = author_elem.find(".//ForeName")

                        if last_name_elem is not None and fore_name_elem is not None:
                            authors.append(
                                Author(
                                    last_name=last_name_elem.text,
                                    fore_name=fore_name_elem.text,
                                )
                            )

                    year_elem = article_elem_in.find(".//PubDate/Year")
                    month_elem = article_elem_in.find(".//PubDate/Month")

                    year = year_elem.text if year_elem is not None else None
                    month = month_elem.text if month_elem is not None else None

                    article = Article(
                        title=title,
                        abstract=abstract,
                        authors=authors,
                        year=year,
                        month=month,
                    )

                    medline_citation = MedlineCitation(pmid=pmid, article=article)

                    pubmed_data_elem = article_elem.find(".//PubmedData")
                    article_ids_list = []

                    for article_id_elem in pubmed_data_elem.findall(".//ArticleId"):
                        article_id = ArticleId(
                            id=article_id_elem.text,
                            id_type=article_id_elem.get("IdType", ""),
                        )
                        article_ids_list.append(article_id)

                    pubmed_data = PubmedData(article_ids=article_ids_list)

                    pubmed_article = PubMedArticle(
                        medline_citation=medline_citation, pubmed_data=pubmed_data
                    )

                    articles.append(pubmed_article)

                return PubMedFetchResult(articles=articles)

        except Exception as e:
            raise Exception(f"Error fetching PubMed articles: {str(e)}")


def path_exists(path: str) -> bool:
    """
    Check if a path exists.

    Args:
        path: Path to check

    Returns:
        True if path exists, False otherwise
    """
    return os.path.exists(path)


pub_med = PubMedService()
