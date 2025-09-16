from __future__ import annotations

from typing import List, Optional
import httpx
from xml.etree import ElementTree as ET

from ..models import Paper, SearchFilters
from ..utils.logging import get_logger

logger = get_logger(__name__)


ESARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


def _fetch_summaries(ids: List[str]) -> List[Paper]:
    if not ids:
        return []
    params = {"db": "pubmed", "id": ",".join(ids), "retmode": "xml"}
    papers: List[Paper] = []
    try:
        with httpx.Client(timeout=30) as client:
            r = client.get(ESUMMARY, params=params)
            r.raise_for_status()
            root = ET.fromstring(r.text)
            for doc in root.findall("DocSum"):
                uid = next((i.text for i in doc.findall("Id") if i.text), None)
                title = None
                authors: List[str] = []
                year: Optional[int] = None
                journal = None
                doi = None
                for item in doc.findall("Item"):
                    if item.attrib.get("Name") == "Title":
                        title = (item.text or "").strip()
                    if item.attrib.get("Name") == "AuthorList":
                        for a in item.findall("Item"):
                            if a.text:
                                authors.append(a.text)
                    if item.attrib.get("Name") == "PubDate":
                        txt = (item.text or "").strip()
                        if txt[:4].isdigit():
                            year = int(txt[:4])
                    if item.attrib.get("Name") == "FullJournalName":
                        journal = item.text
                    if item.attrib.get("Name") == "ELocationID" and item.attrib.get("Type") == "doi":
                        doi = (item.text or "").strip()
                if title:
                    papers.append(
                        Paper(
                            id=uid or title,
                            source="pubmed",
                            title=title,
                            abstract=None,
                            authors=authors,
                            year=year,
                            venue=journal,
                            doi=doi,
                            url=f"https://pubmed.ncbi.nlm.nih.gov/{uid}/" if uid else None,
                            pdf_url=None,
                            citations_count=None,
                            keywords=[],
                        )
                    )
    except Exception as e:  # pragma: no cover - network
        logger.warning("PubMed summary fetch failed: %s", e)
    return papers


def search_pubmed(query: str, filters: SearchFilters) -> List[Paper]:
    term = query
    if filters.start_year or filters.end_year:
        start = filters.start_year or 1900
        end = filters.end_year or 2100
        term = f"{query} AND ({start}:{end}[dp])"
    params = {"db": "pubmed", "term": term, "retmax": max(20, filters.limit), "retmode": "xml"}
    ids: List[str] = []
    try:
        with httpx.Client(timeout=30) as client:
            r = client.get(ESARCH, params=params)
            r.raise_for_status()
            root = ET.fromstring(r.text)
            ids = [i.text for i in root.findall("IdList/Id") if i.text]
    except Exception as e:  # pragma: no cover - network
        logger.warning("PubMed search failed: %s", e)
    return _fetch_summaries(ids)
