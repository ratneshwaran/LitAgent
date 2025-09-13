from __future__ import annotations

from typing import List, Dict

from ..models import Paper


def _norm(s: str) -> str:
    # More conservative normalization - keep some punctuation to avoid over-deduplication
    return "".join(ch.lower() for ch in s if ch.isalnum() or ch.isspace()).strip()


def _similar_title(title1: str, title2: str) -> bool:
    """Check if two titles are similar enough to be considered duplicates"""
    norm1 = _norm(title1)
    norm2 = _norm(title2)
    
    # If normalized titles are identical, they're duplicates
    if norm1 == norm2:
        return True
    
    # If one title is a substring of the other and they're close in length, consider duplicates
    if len(norm1) > 20 and len(norm2) > 20:
        if norm1 in norm2 or norm2 in norm1:
            length_ratio = min(len(norm1), len(norm2)) / max(len(norm1), len(norm2))
            if length_ratio > 0.8:  # 80% similarity threshold
                return True
    
    return False


def dedupe_papers(papers: List[Paper]) -> List[Paper]:
    seen_doi: Dict[str, Paper] = {}
    result: List[Paper] = []
    
    for p in papers:
        # Check DOI duplicates first (most reliable)
        if p.doi:
            doi_key = p.doi.lower().strip()
            if doi_key in seen_doi:
                continue
            seen_doi[doi_key] = p
        
        # Check for similar titles (more conservative approach)
        is_duplicate = False
        for existing_paper in result:
            if _similar_title(p.title, existing_paper.title):
                is_duplicate = True
                break
        
        if not is_duplicate:
            result.append(p)
    
    return result
