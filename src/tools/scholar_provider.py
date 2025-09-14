from __future__ import annotations

import time
from typing import List, Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models import Paper, SearchFilters
from ..config_search import get_search_config
from ..utils.logging import get_logger

logger = get_logger(__name__)

SERPAPI_URL = "https://serpapi.com/search"
SERPER_URL = "https://google.serper.dev/scholar"


def _search_serpapi(query: str, filters: SearchFilters) -> List[Paper]:
    """Search Google Scholar via SerpAPI"""
    config = get_search_config()
    if not config.serpapi_key:
        return []
    
    papers = []
    
    # Build search parameters
    search_params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": config.serpapi_key,
        "num": min(20, config.search_max_per_source // 3)  # Limit for cost control
    }
    
    # Add year filters
    if filters.start_year and filters.end_year:
        search_params["as_ylo"] = filters.start_year
        search_params["as_yhi"] = filters.end_year
    elif filters.start_year:
        search_params["as_ylo"] = filters.start_year
    elif filters.end_year:
        search_params["as_yhi"] = filters.end_year
    
    try:
        # Rate limiting
        time.sleep(0.5)  # 2 requests per second max for SerpAPI
        
        with httpx.Client(timeout=30) as client:
            response = client.get(SERPAPI_URL, params=search_params)
            response.raise_for_status()
            data = response.json()
        
        for item in data.get("organic_results", []):
            # Extract basic information
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            
            # Extract authors and venue from snippet or title
            authors = []
            venue = ""
            
            # Try to extract venue from snippet
            if " - " in snippet:
                parts = snippet.split(" - ")
                if len(parts) > 1:
                    venue = parts[1].split(",")[0].strip()
            
            # Extract year if available
            year = None
            if " - " in snippet:
                parts = snippet.split(" - ")
                for part in parts:
                    if part.strip().isdigit() and len(part.strip()) == 4:
                        year = int(part.strip())
                        break
            
            paper = Paper(
                id=f"scholar_{hash(link)}",
                source="scholar",
                title=title,
                abstract=snippet,
                authors=authors,
                year=year,
                venue=venue,
                doi=None,
                url=link,
                pdf_url=None,
                citations_count=0,
                keywords=[],
                reasons=[f"Google Scholar match for: {query}"]
            )
            
            papers.append(paper)
            
    except Exception as e:
        logger.warning(f"SerpAPI search failed: {e}")
    
    return papers


def _search_serper(query: str, filters: SearchFilters) -> List[Paper]:
    """Search Google Scholar via Serper"""
    config = get_search_config()
    if not config.serper_api_key:
        return []
    
    papers = []
    
    # Build search parameters
    search_params = {
        "q": query,
        "num": min(20, config.search_max_per_source // 3)  # Limit for cost control
    }
    
    headers = {
        "X-API-KEY": config.serper_api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # Rate limiting
        time.sleep(0.5)  # 2 requests per second max for Serper
        
        with httpx.Client(timeout=30) as client:
            response = client.post(SERPER_URL, json=search_params, headers=headers)
            response.raise_for_status()
            data = response.json()
        
        for item in data.get("organic", []):
            # Extract basic information
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            
            # Extract venue and year from snippet
            venue = ""
            year = None
            
            if " - " in snippet:
                parts = snippet.split(" - ")
                if len(parts) > 1:
                    venue = parts[1].split(",")[0].strip()
                
                # Look for year in the snippet
                for part in parts:
                    if part.strip().isdigit() and len(part.strip()) == 4:
                        year = int(part.strip())
                        break
            
            paper = Paper(
                id=f"scholar_{hash(link)}",
                source="scholar",
                title=title,
                abstract=snippet,
                authors=[],
                year=year,
                venue=venue,
                doi=None,
                url=link,
                pdf_url=None,
                citations_count=0,
                keywords=[],
                reasons=[f"Google Scholar match for: {query}"]
            )
            
            papers.append(paper)
            
    except Exception as e:
        logger.warning(f"Serper search failed: {e}")
    
    return papers


def search_scholar(query: str, filters: SearchFilters) -> List[Paper]:
    """Search Google Scholar using configured provider"""
    config = get_search_config()
    if not config.enable_sources.get("scholar", True):
        return []
    
    if config.scholar_provider == "serpapi":
        return _search_serpapi(query, filters)
    elif config.scholar_provider == "serper":
        return _search_serper(query, filters)
    else:
        logger.info("Google Scholar search disabled")
        return []
