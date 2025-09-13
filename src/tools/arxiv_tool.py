from __future__ import annotations

import httpx
from typing import List
from xml.etree import ElementTree as ET

from ..models import Paper, Filters
from ..utils.logging import get_logger

logger = get_logger(__name__)


ARXIV_API = "https://export.arxiv.org/api/query"


def search_arxiv(query: str, filters: Filters) -> List[Paper]:
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max(20, filters.limit),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    papers: List[Paper] = []
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(ARXIV_API, params=params)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("a:entry", ns):
                title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
                abstract = (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()
                authors = [
                    (a.findtext("a:name", default="", namespaces=ns) or "").strip()
                    for a in entry.findall("a:author", ns)
                ]
                link_pdf = None
                link_url = None
                for l in entry.findall("a:link", ns):
                    href = l.attrib.get("href")
                    if l.attrib.get("title") == "pdf" or l.attrib.get("type") == "application/pdf":
                        link_pdf = href
                    elif l.attrib.get("rel") == "alternate":
                        link_url = href
                arxiv_id = (entry.findtext("a:id", default="", namespaces=ns) or "").strip()
                year = None
                published = entry.findtext("a:published", default="", namespaces=ns)
                if published:
                    try:
                        year = int(published[:4])
                    except Exception:
                        year = None
                papers.append(
                    Paper(
                        id=arxiv_id or title,
                        source="arxiv",
                        title=title,
                        abstract=abstract,
                        authors=[a for a in authors if a],
                        year=year,
                        venue="arXiv",
                        doi=None,
                        url=link_url,
                        pdf_url=link_pdf,
                        citations_count=None,
                        keywords=[],
                    )
                )
    except Exception as e:  # pragma: no cover - network
        logger.warning("arXiv search failed: %s", e)
    return papers
