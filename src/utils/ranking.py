from __future__ import annotations

from typing import List

from ..models import Paper, Filters


def score_paper(paper: Paper, topic: str, filters: Filters) -> float:
    # Enhanced topic relevance scoring with weighted terms
    topic_terms = set(topic.lower().split())
    title_terms = set((paper.title or "").lower().split())
    abstract_terms = set((paper.abstract or "").lower().split())
    
    # Weight title matches more heavily than abstract matches
    title_overlap = len(topic_terms & title_terms) * 3
    abstract_overlap = len(topic_terms & abstract_terms) * 1
    overlap = title_overlap + abstract_overlap

    # Enhanced keyword scoring with better relevance weighting
    keyword_boost = 0
    if filters.include_keywords:
        text = f"{paper.title or ''} {paper.abstract or ''}".lower()
        for keyword in filters.include_keywords:
            keyword_words = [w.strip() for w in keyword.lower().split() if len(w.strip()) > 2]
            if keyword_words:
                # Give higher weight for exact phrase matches
                if keyword.lower() in text:
                    keyword_boost += 3
                else:
                    # Partial credit for individual words
                    matching_words = sum(1 for word in keyword_words if word in text)
                    keyword_boost += (matching_words / len(keyword_words)) * 2
            else:
                if keyword.lower() in text:
                    keyword_boost += 2
    
    if filters.exclude_keywords:
        text = f"{paper.title or ''} {paper.abstract or ''}".lower()
        for keyword in filters.exclude_keywords:
            keyword_words = [w.strip() for w in keyword.lower().split() if len(w.strip()) > 2]
            if keyword_words:
                matching_words = sum(1 for word in keyword_words if word in text)
                keyword_boost -= (matching_words / len(keyword_words)) * 3
            else:
                if keyword.lower() in text:
                    keyword_boost -= 3

    # Enhanced venue scoring with tier-based weighting
    venue_boost = 0
    if filters.venues and paper.venue:
        venue_text = paper.venue.lower()
        for venue in filters.venues:
            if venue.lower() in venue_text:
                # Higher tier venues get more boost
                if any(tier in venue_text for tier in ["nature", "science", "cell", "lancet"]):
                    venue_boost += 3
                elif any(tier in venue_text for tier in ["ieee", "acm", "springer", "elsevier"]):
                    venue_boost += 2
                else:
                    venue_boost += 1
                break

    # Enhanced recency scoring with exponential decay for very old papers
    recency = 0
    if paper.year:
        current_year = 2024
        age = current_year - paper.year
        if age <= 2:
            recency = 2  # Very recent
        elif age <= 5:
            recency = 1.5  # Recent
        elif age <= 10:
            recency = 1  # Moderately recent
        else:
            recency = max(0, 1 - (age - 10) * 0.1)  # Gradual decay

    # Enhanced citation scoring with better normalization
    cites = 0
    if paper.citations_count:
        # Use logarithmic scaling with different weights for different citation ranges
        if paper.citations_count >= 1000:
            cites = 3
        elif paper.citations_count >= 100:
            cites = 2
        elif paper.citations_count >= 10:
            cites = 1
        else:
            cites = 0.5

    # Quality indicators bonus
    quality_bonus = 0
    if paper.abstract and len(paper.abstract) > 200:
        quality_bonus += 0.5  # Well-documented papers
    if paper.doi:
        quality_bonus += 0.3  # Published papers with DOI
    if paper.authors and len(paper.authors) > 1:
        quality_bonus += 0.2  # Collaborative work

    return overlap + keyword_boost + venue_boost + recency + cites + quality_bonus


def rank_papers(papers: List[Paper], topic: str, filters: Filters) -> List[Paper]:
    return sorted(papers, key=lambda p: score_paper(p, topic, filters), reverse=True)
