from __future__ import annotations

from typing import List

from ..models import Paper, Filters


def score_paper(paper: Paper, topic: str, filters: Filters) -> float:
    # Topic relevance scoring
    topic_terms = set(topic.lower().split())
    title_terms = set((paper.title or "").lower().split())
    abstract_terms = set((paper.abstract or "").lower().split())
    overlap = len(topic_terms & (title_terms | abstract_terms))

    # More flexible keyword scoring
    keyword_boost = 0
    if filters.include_keywords:
        text = f"{paper.title or ''} {paper.abstract or ''}".lower()
        for keyword in filters.include_keywords:
            # Split multi-word keywords and give partial credit for individual words
            keyword_words = [w.strip() for w in keyword.lower().split() if len(w.strip()) > 2]
            if keyword_words:
                # Give partial credit for each matching word
                matching_words = sum(1 for word in keyword_words if word in text)
                keyword_boost += (matching_words / len(keyword_words)) * 2
            else:
                # Single word keyword
                if keyword.lower() in text:
                    keyword_boost += 2
    
    if filters.exclude_keywords:
        text = f"{paper.title or ''} {paper.abstract or ''}".lower()
        for keyword in filters.exclude_keywords:
            keyword_words = [w.strip() for w in keyword.lower().split() if len(w.strip()) > 2]
            if keyword_words:
                matching_words = sum(1 for word in keyword_words if word in text)
                keyword_boost -= (matching_words / len(keyword_words)) * 2
            else:
                if keyword.lower() in text:
                    keyword_boost -= 2

    # Venue boost for preferred venues
    venue_boost = 0
    if filters.venues and paper.venue:
        venue_text = paper.venue.lower()
        for venue in filters.venues:
            if venue.lower() in venue_text:
                venue_boost += 1
                break

    # Recency scoring (more recent papers get higher scores)
    recency = 0
    if paper.year:
        recency = max(0, paper.year - 2015) * 0.1

    # Citation scoring (logarithmic to avoid extreme bias)
    cites = (paper.citations_count or 0) ** 0.5 * 0.2

    return overlap + keyword_boost + venue_boost + recency + cites


def rank_papers(papers: List[Paper], topic: str, filters: Filters) -> List[Paper]:
    return sorted(papers, key=lambda p: score_paper(p, topic, filters), reverse=True)
