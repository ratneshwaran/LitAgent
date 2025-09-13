from __future__ import annotations

from typing import List, Optional
import httpx

from ..models import Paper, Filters
from ..utils.logging import get_logger

logger = get_logger(__name__)


CROSSREF = "https://api.crossref.org/works"


def enrich_with_crossref(paper: Paper) -> Paper:
    if paper.doi:
        try:
            with httpx.Client(timeout=30) as client:
                r = client.get(f"{CROSSREF}/{paper.doi}")
                if r.status_code == 200:
                    item = r.json().get("message", {})
                    title = item.get("title", [paper.title])[0]
                    year = None
                    if item.get("issued", {}).get("date-parts"):
                        year = item["issued"]["date-parts"][0][0]
                    venue = (item.get("container-title") or [paper.venue or None])[0]
                    authors = [
                        " ".join([a.get("given", ""), a.get("family", "")]).strip()
                        for a in item.get("author", [])
                    ] or paper.authors
                    url = item.get("URL", paper.url)
                    return paper.model_copy(update={
                        "title": title,
                        "year": year or paper.year,
                        "venue": venue or paper.venue,
                        "authors": authors,
                        "url": url,
                    })
        except Exception as e:  # pragma: no cover - network
            logger.warning("Crossref enrich DOI failed: %s", e)
    return paper


def search_crossref(query: str, filters: Filters) -> List[Paper]:
    params = {
        "query": query,
        "select": "title,author,issued,container-title,DOI,URL",
        "rows": max(20, filters.limit),
        "sort": "relevance",
        "order": "desc",
    }
    results: List[Paper] = []
    try:
        with httpx.Client(timeout=30) as client:
            r = client.get(CROSSREF, params=params)
            r.raise_for_status()
            items = r.json().get("message", {}).get("items", [])
            for it in items:
                title = (it.get("title") or [""])[0]
                year = None
                if it.get("issued", {}).get("date-parts"):
                    year = it["issued"]["date-parts"][0][0]
                venue = (it.get("container-title") or [None])[0]
                authors = [
                    " ".join([a.get("given", ""), a.get("family", "")]).strip()
                    for a in it.get("author", [])
                ]
                doi = it.get("DOI")
                url = it.get("URL")
                results.append(
                    Paper(
                        id=doi or title,
                        source="crossref",
                        title=title,
                        abstract=None,
                        authors=authors,
                        year=year,
                        venue=venue,
                        doi=doi,
                        url=url,
                        pdf_url=None,
                        citations_count=None,
                        keywords=[],
                    )
                )
    except Exception as e:  # pragma: no cover - network
        logger.warning("Crossref search failed: %s", e)
    return results
