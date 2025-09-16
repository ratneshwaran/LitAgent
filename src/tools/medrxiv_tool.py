"""
MedRxiv search tool for medical preprints
"""

import requests
import time
from typing import List, Dict, Any
from ..models import Paper, SearchFilters
from ..utils.logging import get_logger

logger = get_logger(__name__)

def search_medrxiv(query: str, filters: SearchFilters) -> List[Paper]:
    """Search MedRxiv for medical preprints"""
    try:
        # MedRxiv API endpoint
        url = "https://www.medrxiv.org/search"
        
        params = {
            "content": "articlesChapters",
            "searchText": query,
            "pageSize": min(filters.limit, 50),
            "sort": "relevance-rank",
            "format": "json"
        }
        
        # Add year filters if specified
        if filters.start_year:
            params["fromDate"] = f"{filters.start_year}-01-01"
        if filters.end_year:
            params["toDate"] = f"{filters.end_year}-12-31"
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        papers = []
        
        if "collection" in data:
            for item in data["collection"]:
                try:
                    paper = Paper(
                        id=item.get("doi", item.get("uri", "")),
                        source="medrxiv",
                        title=item.get("title", ""),
                        abstract=item.get("abstract", ""),
                        authors=[author.get("name", "") for author in item.get("authors", [])],
                        venue="MedRxiv",
                        year=int(item.get("published", "").split("-")[0]) if item.get("published") else None,
                        doi=item.get("doi"),
                        url=item.get("uri"),
                        pdf_url=item.get("pdf") if item.get("pdf") else None,
                        citations_count=0,  # MedRxiv doesn't provide citation counts
                        keywords=[]
                    )
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing MedRxiv paper: {e}")
                    continue
        
        logger.info(f"MedRxiv returned {len(papers)} papers")
        return papers
        
    except Exception as e:
        logger.error(f"MedRxiv search failed: {e}")
        return []
