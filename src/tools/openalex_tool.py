from __future__ import annotations

import time
from typing import List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models import Paper, SearchFilters
from ..config_search import get_search_config
from ..utils.logging import get_logger

logger = get_logger(__name__)

OPENALEX_API = "https://api.openalex.org/works"


def _reconstruct_abstract(abstract_inverted_index: Dict[str, List[int]]) -> str:
    """Reconstruct abstract from OpenAlex inverted index format"""
    if not abstract_inverted_index:
        return ""
    
    # Create a list of (position, word) tuples
    word_positions = []
    for word, positions in abstract_inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    
    # Sort by position and join
    word_positions.sort(key=lambda x: x[0])
    return " ".join([word for _, word in word_positions])


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def _make_request(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Make HTTP request with retry logic"""
    config = get_search_config()
    
    headers = {
        "User-Agent": f"LiteratureReviewAgent/1.0 (mailto:{config.openalex_email})"
    } if config.openalex_email else {"User-Agent": "LiteratureReviewAgent/1.0"}
    
    with httpx.Client(timeout=30) as client:
        response = client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


def search_openalex(query: str, filters: SearchFilters) -> List[Paper]:
    """Search OpenAlex for papers"""
    config = get_search_config()
    if not config.enable_sources.get("openalex", True):
        return []
    
    papers = []
    per_page = min(200, config.search_max_per_source)
    
    # Build base search parameters
    base_params = {
        "search": query,
        "per-page": per_page,
        "sort": "relevance_score:desc",
        "filter": []
    }
    
    # Add filters
    if filters.start_year:
        base_params["filter"].append(f"from_publication_date:{filters.start_year}")
    if filters.end_year:
        base_params["filter"].append(f"to_publication_date:{filters.end_year}")
    
    # Add venue filter if specified
    if filters.venues:
        venue_filter = "|".join(filters.venues)
        base_params["filter"].append(f"primary_location.source.display_name:{venue_filter}")
    
    # Only require abstract if strict filters are enabled
    if get_search_config().strict_filters:
        base_params["filter"].append("has_abstract:true")
    # Open access only if requested
    if filters.oa_only:
        base_params["filter"].append("is_oa:true")
    
    try:
        total_target = config.search_max_per_source
        page = 1
        while len(papers) < total_target:
            # Rate limiting
            time.sleep(0.1)  # 10 requests per second max
            search_params = {**base_params, "page": page}
            response = _make_request(OPENALEX_API, search_params)
            results = response.get("results", [])
            if not results:
                break
            for item in results:
                # Extract authors
                authors = []
                for author in item.get("authorships", []):
                    author_name = author.get("author", {}).get("display_name", "")
                    if author_name:
                        authors.append(author_name)
                
                # Get venue information
                venue = ""
                if item.get("primary_location", {}).get("source"):
                    venue = item["primary_location"]["source"].get("display_name", "")
                
                # Get PDF URL if available (do not require OA unless requested)
                pdf_url = None
                for location in item.get("locations", []):
                    if location.get("pdf_url"):
                        pdf_url = location["pdf_url"]
                        break
                
                # Reconstruct abstract
                abstract = _reconstruct_abstract(item.get("abstract_inverted_index", {}))
                
                paper = Paper(
                    id=item.get("id", "").replace("https://openalex.org/", ""),
                    source="openalex",
                    title=item.get("title", ""),
                    abstract=abstract,
                    authors=authors,
                    year=item.get("publication_year"),
                    venue=venue,
                    doi=item.get("doi"),
                    url=item.get("id"),
                    pdf_url=pdf_url,
                    citations_count=item.get("cited_by_count", 0),
                    keywords=[],
                    reasons=[f"OpenAlex relevance score: {item.get('relevance_score', 0):.3f}"]
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
        logger.warning(f"OpenAlex search failed: {e}")
    
    logger.info(f"OpenAlex returned {len(papers)} papers")
    return papers
