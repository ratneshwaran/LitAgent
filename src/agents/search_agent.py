from __future__ import annotations

from typing import List

from ..models import Paper, Filters
from ..tools.arxiv_tool import search_arxiv
from ..tools.pubmed_tool import search_pubmed
from ..tools.crossref_tool import search_crossref, enrich_with_crossref
from ..utils.dedupe import dedupe_papers
from ..utils.ranking import rank_papers
from ..utils.logging import get_logger

logger = get_logger(__name__)


def _apply_filters(papers: List[Paper], filters: Filters) -> List[Paper]:
    def ok(p: Paper) -> bool:
        if filters.start_year and (p.year or 0) < filters.start_year:
            return False
        if filters.end_year and (p.year or 9999) > filters.end_year:
            return False
        
        # More flexible venue matching - check if any venue keyword is contained in the paper's venue
        if filters.venues:
            venue_text = (p.venue or "").lower()
            venue_matches = any(venue.lower() in venue_text for venue in filters.venues)
            if not venue_matches:
                return False
        
        # More flexible keyword matching - split multi-word keywords and check for individual terms
        if filters.include_keywords:
            text = f"{p.title} {p.abstract or ''}".lower()
            keyword_matches = 0
            for keyword in filters.include_keywords:
                # Split multi-word keywords and check if any significant word matches
                keyword_words = [w.strip() for w in keyword.lower().split() if len(w.strip()) > 2]
                if keyword_words:
                    # Check if all significant words from the keyword are found
                    if all(any(word in text for word in keyword_words if len(word) > 2) for word in keyword_words):
                        keyword_matches += 1
                else:
                    # Single word or very short keyword - use exact match
                    if keyword.lower() in text:
                        keyword_matches += 1
            
            # Require at least one keyword to match (instead of all)
            if keyword_matches == 0:
                return False
        
        # Exclude keywords - more flexible matching
        if filters.exclude_keywords:
            text = f"{p.title} {p.abstract or ''}".lower()
            for keyword in filters.exclude_keywords:
                # Split multi-word keywords and check if any significant word matches
                keyword_words = [w.strip() for w in keyword.lower().split() if len(w.strip()) > 2]
                if keyword_words:
                    # If any significant word from exclude keyword is found, exclude the paper
                    if any(word in text for word in keyword_words if len(word) > 2):
                        return False
                else:
                    # Single word or very short keyword - use exact match
                    if keyword.lower() in text:
                        return False
        return True

    return [p for p in papers if ok(p)]


def run_search(topic: str, filters: Filters) -> List[Paper]:
    # Gather from all sources to get more papers before filtering
    papers: List[Paper] = []
    papers += search_arxiv(topic, filters)
    papers += search_pubmed(topic, filters)
    papers += search_crossref(topic, filters)  # Always search Crossref for more results

    # Enrich
    enriched = [enrich_with_crossref(p) for p in papers]

    # Dedupe
    deduped = dedupe_papers(enriched)

    # Filter
    filtered = _apply_filters(deduped, filters)

    # If filtering was too restrictive, try with relaxed filters
    if len(filtered) < filters.limit and filters.include_keywords:
        logger.info(f"Only found {len(filtered)} papers after filtering, trying with relaxed keyword matching")
        # Create relaxed filters without include keywords
        relaxed_filters = filters.model_copy()
        relaxed_filters.include_keywords = []
        relaxed_filtered = _apply_filters(deduped, relaxed_filters)
        # Re-rank with original topic to maintain relevance
        relaxed_ranked = rank_papers(relaxed_filtered, topic, filters)
        filtered = relaxed_ranked[:filters.limit * 2]  # Get more papers for better selection

    # Rank & limit
    ranked = rank_papers(filtered, topic, filters)
    return ranked[: filters.limit]
