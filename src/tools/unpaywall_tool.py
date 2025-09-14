from __future__ import annotations

import time
from typing import List, Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models import Paper
from ..config_search import get_search_config
from ..utils.logging import get_logger

logger = get_logger(__name__)

UNPAYWALL_API = "https://api.unpaywall.org/v2"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def _make_request(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Make HTTP request with retry logic"""
    config = get_search_config()
    
    headers = {}
    if config.unpaywall_email:
        params["email"] = config.unpaywall_email
    
    with httpx.Client(timeout=30) as client:
        response = client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


def resolve_open_access(doi: str) -> Optional[Dict[str, Any]]:
    """Resolve open access URL for a DOI using Unpaywall"""
    if not doi:
        return None
    
    try:
        # Rate limiting
        time.sleep(0.1)  # 10 requests per second max
        
        params = {"doi": doi}
        response = _make_request(f"{UNPAYWALL_API}/{doi}", params)
        
        if response.get("is_oa"):
            # Find the best open access URL
            oa_locations = response.get("oa_locations", [])
            if oa_locations:
                # Prefer PDF URLs
                for location in oa_locations:
                    if location.get("url_for_pdf"):
                        return {
                            "pdf_url": location["url_for_pdf"],
                            "url": location.get("url"),
                            "license": location.get("license"),
                            "version": location.get("version")
                        }
                
                # Fallback to any URL
                location = oa_locations[0]
                return {
                    "pdf_url": location.get("url_for_pdf"),
                    "url": location.get("url"),
                    "license": location.get("license"),
                    "version": location.get("version")
                }
        
        return None
        
    except Exception as e:
        logger.warning(f"Unpaywall resolution failed for DOI {doi}: {e}")
        return None


def enrich_papers_with_oa(papers: List[Paper]) -> List[Paper]:
    """Enrich papers with open access URLs from Unpaywall"""
    enriched_papers = []
    
    for paper in papers:
        # Only try to resolve if we don't already have a PDF URL
        if paper.doi and not paper.pdf_url:
            oa_info = resolve_open_access(paper.doi)
            if oa_info:
                paper.pdf_url = oa_info.get("pdf_url")
                if oa_info.get("license"):
                    paper.reasons.append(f"Open access via {oa_info['license']} license")
        
        enriched_papers.append(paper)
    
    return enriched_papers
