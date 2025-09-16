"""
DBLP search tool for computer science literature
"""

import requests
import time
from typing import List, Dict, Any
from ..models import Paper, SearchFilters
from ..utils.logging import get_logger

logger = get_logger(__name__)

def search_dblp(query: str, filters: SearchFilters) -> List[Paper]:
    """Search DBLP for computer science papers"""
    try:
        # DBLP API endpoint
        url = "https://dblp.org/search/publ/api"
        
        params = {
            "q": query,
            "format": "json",
            "h": min(filters.limit, 50)  # DBLP uses 'h' for hit count
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        papers = []
        
        if "result" in data and "hits" in data["result"]:
            hits = data["result"]["hits"]
            if "hit" in hits:
                for item in hits["hit"]:
                    try:
                        info = item.get("info", {})
                        
                        # Extract year from key or venue
                        year = None
                        if "year" in info:
                            year = int(info["year"])
                        elif "key" in item:
                            # Try to extract year from key like "journals/.../2023"
                            key_parts = item["key"].split("/")
                            for part in key_parts:
                                if part.isdigit() and len(part) == 4:
                                    year = int(part)
                                    break
                        
                        # Apply year filter
                        if filters.start_year and year and year < filters.start_year:
                            continue
                        if filters.end_year and year and year > filters.end_year:
                            continue
                        
                        # Extract venue from key
                        venue = "Unknown"
                        if "key" in item:
                            key_parts = item["key"].split("/")
                            if len(key_parts) > 1:
                                venue = key_parts[1].replace("_", " ").title()
                        
                        paper = Paper(
                            id=item.get("key", info.get("title", "")),
                            source="dblp",
                            title=info.get("title", ""),
                            abstract="",  # DBLP doesn't provide abstracts
                            authors=[author.get("text", "") for author in info.get("authors", {}).get("author", [])],
                            venue=venue,
                            year=year,
                            doi=info.get("doi"),
                            url=info.get("url"),
                            pdf_url=None,  # DBLP doesn't provide direct PDF links
                            citations_count=0,  # DBLP doesn't provide citation counts
                            keywords=[]
                        )
                        papers.append(paper)
                    except Exception as e:
                        logger.warning(f"Error parsing DBLP paper: {e}")
                        continue
        
        logger.info(f"DBLP returned {len(papers)} papers")
        return papers
        
    except Exception as e:
        logger.error(f"DBLP search failed: {e}")
        return []
