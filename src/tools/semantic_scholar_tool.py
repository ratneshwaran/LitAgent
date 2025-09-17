from __future__ import annotations

import time
from typing import List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models import Paper, SearchFilters
from ..config_search import get_search_config
from ..utils.logging import get_logger

logger = get_logger(__name__)

S2_API = "https://api.semanticscholar.org/graph/v1/paper/search"


def _build_s2_query(query: str, filters: SearchFilters) -> str:
    """Build Semantic Scholar query string"""
    # Start with the main query
    s2_query = query
    
    # Add year filters
    if filters.start_year and filters.end_year:
        s2_query += f" AND year:[{filters.start_year} TO {filters.end_year}]"
    elif filters.start_year:
        s2_query += f" AND year:>={filters.start_year}"
    elif filters.end_year:
        s2_query += f" AND year:<={filters.end_year}"
    
    # Add venue filters
    if filters.venues:
        venue_query = " OR ".join([f'venue:"{venue}"' for venue in filters.venues])
        s2_query += f" AND ({venue_query})"
    
    return s2_query


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def _make_request(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Make HTTP request with retry logic"""
    config = get_search_config()
    
    headers = {}
    if config.s2_api_key:
        headers["x-api-key"] = config.s2_api_key
    
    with httpx.Client(timeout=30) as client:
        response = client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


def search_semantic_scholar(query: str, filters: SearchFilters) -> List[Paper]:
    """Search Semantic Scholar for papers"""
    config = get_search_config()
    if not config.enable_sources.get("semanticscholar", True):
        return []
    
    papers = []
    limit = min(100, config.search_max_per_source)
    
    # Build base search parameters
    base_params = {
        "query": _build_s2_query(query, filters),
        "limit": min(100, limit),
        "fields": "paperId,title,abstract,authors,year,venue,doi,url,openAccessPdf,citationCount,isOpenAccess"
    }
    
    try:
        # Semantic Scholar Graph API supports pagination via offset+limit
        fetched = 0
        offset = 0
        while fetched < limit:
            # Rate limiting
            time.sleep(0.1)  # 10 requests per second max
            params = {**base_params, "offset": offset}
            response = _make_request(S2_API, params)
            data = response.get("data", [])
            if not data:
                break
            for item in data:
                # Extract authors
                authors = []
                for author in item.get("authors", []):
                    author_name = author.get("name", "")
                    if author_name:
                        authors.append(author_name)
                
                # Get PDF URL
                pdf_url = None
                if item.get("openAccessPdf", {}).get("url"):
                    pdf_url = item["openAccessPdf"]["url"]
                
                paper = Paper(
                    id=item.get("paperId", ""),
                    source="semanticscholar",
                    title=item.get("title", ""),
                    abstract=item.get("abstract", ""),
                    authors=authors,
                    year=item.get("year"),
                    venue=item.get("venue", ""),
                    doi=item.get("doi"),
                    url=item.get("url"),
                    pdf_url=pdf_url,
                    citations_count=item.get("citationCount", 0),
                    keywords=[],
                    reasons=[f"Semantic Scholar match for: {query}"]
                )
                # Apply OA/PDF post-filtering
                if filters.must_have_pdf and not paper.pdf_url:
                    pass
                elif filters.oa_only and not (item.get("isOpenAccess") or item.get("openAccessPdf")):
                    pass
                else:
                    papers.append(paper)
            
            fetched = len(papers)
            offset += base_params["limit"]
        
    except Exception as e:
        logger.warning(f"Semantic Scholar search failed: {e}")
    
    logger.info(f"Semantic Scholar returned {len(papers)} papers")
    return papers
