from __future__ import annotations

import time
from typing import List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models import Paper, SearchFilters
from ..config_search import get_search_config
from ..utils.logging import get_logger

logger = get_logger(__name__)

EUROPE_PMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def _build_europe_pmc_query(query: str, filters: SearchFilters) -> str:
    """Build Europe PMC query string"""
    # Start with the main query
    epmc_query = query
    
    # Add year filters
    if filters.start_year and filters.end_year:
        epmc_query += f" AND PUB_YEAR:[{filters.start_year} TO {filters.end_year}]"
    elif filters.start_year:
        epmc_query += f" AND PUB_YEAR:>={filters.start_year}"
    elif filters.end_year:
        epmc_query += f" AND PUB_YEAR:<={filters.end_year}"
    
    # Add venue filters
    if filters.venues:
        venue_query = " OR ".join([f'JOURNAL:"{venue}"' for venue in filters.venues])
        epmc_query += f" AND ({venue_query})"
    
    return epmc_query


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def _make_request(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Make HTTP request with retry logic"""
    with httpx.Client(timeout=30) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def search_europe_pmc(query: str, filters: SearchFilters) -> List[Paper]:
    """Search Europe PMC for papers"""
    config = get_search_config()
    if not config.enable_sources.get("europe_pmc", True):
        return []
    
    papers = []
    page_size = min(100, config.search_max_per_source)
    
    # Build base search parameters
    base_params = {
        "query": _build_europe_pmc_query(query, filters),
        "format": "json",
        "pageSize": page_size,
        "resultType": "core",
        "sortBy": "relevance"
    }
    
    try:
        total_target = config.search_max_per_source
        page = 1
        while len(papers) < total_target:
            # Rate limiting
            time.sleep(0.1)  # 10 requests per second max
            params = {**base_params, "page": page}
            response = _make_request(EUROPE_PMC_API, params)
            results = response.get("resultList", {}).get("result", [])
            if not results:
                break
            for item in results:
                # Extract authors
                authors = []
                for author in item.get("authorList", {}).get("author", []):
                    if isinstance(author, dict):
                        author_name = author.get("fullName", "")
                        if author_name:
                            authors.append(author_name)
            
                # Get PDF URL if available
                pdf_url = None
                for link in item.get("fullTextUrlList", {}).get("fullTextUrl", []):
                    if link.get("documentStyle") == "pdf" and link.get("availability") == "Open access":
                        pdf_url = link.get("url")
                        break
            
                # Prefer stable URL; fall back to DOI link if PMID is missing
                pmid = item.get("pmid")
                doi = item.get("doi")
                url = f"https://europepmc.org/article/MED/{pmid}" if pmid else (f"https://doi.org/{doi}" if doi else None)

                paper = Paper(
                    id=item.get("id", ""),
                    source="europe_pmc",
                    title=item.get("title", ""),
                    abstract=item.get("abstractText", ""),
                    authors=authors,
                    year=int(item.get("pubYear", 0)) if item.get("pubYear") else None,
                    venue=item.get("journalTitle", ""),
                    doi=doi,
                    url=url,
                    pdf_url=pdf_url,
                    citations_count=item.get("citedByCount", 0),
                    keywords=[],
                    reasons=[f"Europe PMC match for: {query}"]
                )
                # Apply must_have_pdf post-filter
                if filters.must_have_pdf and not paper.pdf_url:
                    pass
                else:
                    papers.append(paper)

                if len(papers) >= total_target:
                    break

            page += 1
            
    except Exception as e:
        logger.warning(f"Europe PMC search failed: {e}")
    
    logger.info(f"Europe PMC returned {len(papers)} papers")
    return papers
