from __future__ import annotations

import time
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from ..models import Paper, SearchFilters
from ..utils.logging import get_logger
from .embedding_store import get_embedding_store, EmbeddingRecord
from .fusion import calculate_bm25_scores

logger = get_logger(__name__)


def get_query_embedding(query: str, model: str = "text-embedding-3-large") -> np.ndarray:
    """Get embedding for a query using OpenAI API"""
    try:
        import openai
        from ..config import get_settings
        
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not available")
        
        # Translate non-English queries if needed
        translated_query = _translate_query_if_needed(query)
        
        # Enhance query for better semantic matching
        enhanced_query = _enhance_query_for_semantic_search(translated_query)
        
        response = openai.embeddings.create(
            model=model,
            input=enhanced_query
        )
        
        return np.array(response.data[0].embedding)
        
    except Exception as e:
        logger.error(f"Failed to get query embedding: {e}")
        raise


def _enhance_query_for_semantic_search(query: str) -> str:
    """Enhance query for better semantic search results"""
    # Add context to make the query more descriptive
    if len(query.strip()) < 10:
        # For short queries, add research context
        enhanced = f"research papers about {query.strip()}"
    else:
        # For longer queries, ensure it's clear it's about academic research
        enhanced = f"academic research papers: {query.strip()}"
    
    return enhanced


def _translate_query_if_needed(query: str) -> str:
    """Translate non-English queries to English for better embedding quality"""
    # Simple heuristic: if query contains mostly non-ASCII characters, it might be non-English
    ascii_ratio = sum(1 for c in query if ord(c) < 128) / len(query) if query else 1
    
    if ascii_ratio < 0.7:  # Less than 70% ASCII characters
        try:
            import openai
            from ..config import get_settings
            
            settings = get_settings()
            if settings.openai_api_key:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Translate the following text to English. Return only the translation, no additional text."},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=200,
                    temperature=0
                )
                translated = response.choices[0].message.content.strip()
                logger.info(f"Translated query: '{query}' -> '{translated}'")
                return translated
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
    
    return query


def semantic_search(query: str, filters: SearchFilters, k: int = 20) -> List[Paper]:
    """Perform semantic search using embeddings"""
    start_time = time.time()
    
    try:
        # Ensure embedding store is populated
        ensure_embedding_store_populated()
        
        # Get embedding store
        embedding_store = get_embedding_store()
        if embedding_store is None:
            logger.warning("Embedding store not available, falling back to traditional search")
            return _fallback_to_traditional_search(query, filters, k)
        
        # Get query embedding
        try:
            query_embedding = get_query_embedding(query)
        except Exception as e:
            logger.warning(f"Embedding retrieval failed ({e}); falling back to traditional search.")
            return _fallback_to_traditional_search(query, filters, k)
        
        # Search embedding store
        results = embedding_store.search(query_embedding, k=k * 2)  # Get more for filtering
        
        # Convert to Paper objects
        papers = []
        for record, score in results:
            paper = Paper(
                id=record.paper_id,
                source=record.source,
                title=record.title,
                abstract=record.abstract,
                doi=record.doi,
                year=record.year,
                venue=record.venue,
                reasons=[f"Semantic similarity: {score:.3f}"]
            )
            papers.append(paper)
        
        # Apply filters
        filtered_papers = _apply_semantic_filters(papers, filters)
        
        # Apply BM25 scoring for better ranking
        if len(filtered_papers) > 1:
            filtered_papers = calculate_bm25_scores(filtered_papers, query)
        
        # Sort by combined score (semantic + BM25)
        filtered_papers = _rank_semantic_results(filtered_papers, query)
        
        # Limit results
        final_papers = filtered_papers[:k]
        
        logger.info(f"Semantic search returned {len(final_papers)} papers in {time.time() - start_time:.2f}s")
        return final_papers
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return []


def _apply_semantic_filters(papers: List[Paper], filters: SearchFilters) -> List[Paper]:
    """Apply filters to semantic search results"""
    filtered = []
    
    for paper in papers:
        # Year filter
        if filters.start_year and paper.year and paper.year < filters.start_year:
            continue
        if filters.end_year and paper.year and paper.year > filters.end_year:
            continue
        
        # Venue filter
        if filters.venues and paper.venue:
            if not any(venue.lower() in paper.venue.lower() for venue in filters.venues):
                continue
        
        # Include keywords filter
        if filters.include_keywords:
            text = f"{paper.title} {paper.abstract or ''}".lower()
            if not any(keyword.lower() in text for keyword in filters.include_keywords):
                continue
        
        # Exclude keywords filter
        if filters.exclude_keywords:
            text = f"{paper.title} {paper.abstract or ''}".lower()
            if any(keyword.lower() in text for keyword in filters.exclude_keywords):
                continue
        
        filtered.append(paper)
    
    return filtered


def _rank_semantic_results(papers: List[Paper], query: str) -> List[Paper]:
    """Rank semantic search results using combined scoring"""
    for paper in papers:
        if not paper.score_components:
            from ..models import ScoreComponents
            paper.score_components = ScoreComponents()
        
        # Extract semantic score from reasons
        semantic_score = 0.0
        for reason in paper.reasons:
            if "Semantic similarity:" in reason:
                try:
                    semantic_score = float(reason.split(":")[1].strip())
                    break
                except (ValueError, IndexError):
                    pass
        
        # Combine semantic and BM25 scores
        bm25_score = paper.score_components.bm25 if paper.score_components else 0.0
        combined_score = 0.7 * semantic_score + 0.3 * bm25_score
        
        paper.score_components.final = combined_score
    
    # Sort by final score
    return sorted(papers, key=lambda p: p.score_components.final if p.score_components else 0, reverse=True)


def hybrid_search(title_query: str, description_query: str, filters: SearchFilters, k: int = 20) -> List[Paper]:
    """Perform hybrid search combining semantic and title-based search"""
    start_time = time.time()
    
    # Prioritize description if provided, otherwise use title
    if description_query.strip():
        # Use description as primary semantic query
        semantic_query = description_query.strip()
        # Add title as additional context
        if title_query.strip():
            semantic_query = f"{description_query.strip()} {title_query.strip()}"
    else:
        # Fall back to title query
        semantic_query = title_query.strip()
    
    # Get semantic results using enhanced query
    try:
        semantic_papers = semantic_search(semantic_query, filters, k=k)
    except Exception as e:
        logger.warning(f"Semantic search failed: {e}, falling back to title search only")
        semantic_papers = []
    
    # Get title-based results (using existing search)
    from ..agents.search_agent import run_search
    from ..models import Filters
    
    # Convert SearchFilters to Filters for compatibility
    legacy_filters = Filters(
        start_year=filters.start_year,
        end_year=filters.end_year,
        include_keywords=filters.include_keywords,
        exclude_keywords=filters.exclude_keywords,
        venues=filters.venues,
        limit=k
    )
    
    # Use title query for traditional search
    title_papers = run_search(title_query, legacy_filters)
    
    # Combine and deduplicate
    all_papers = semantic_papers + title_papers
    from .fusion import dedupe_papers
    deduped_papers, _ = dedupe_papers(all_papers)
    
    # Re-rank with hybrid scoring
    description_provided = bool(description_query.strip())
    hybrid_papers = _rank_hybrid_results(deduped_papers, semantic_query, semantic_papers, title_papers, description_provided)
    
    # Limit results
    final_papers = hybrid_papers[:k]
    
    logger.info(f"Hybrid search returned {len(final_papers)} papers in {time.time() - start_time:.2f}s")
    return final_papers


def _rank_hybrid_results(papers: List[Paper], query: str, semantic_papers: List[Paper], title_papers: List[Paper], description_provided: bool = False) -> List[Paper]:
    """Rank hybrid search results with weighted fusion"""
    # Create lookup for semantic and title scores
    semantic_scores = {p.id: _get_semantic_score(p) for p in semantic_papers}
    title_scores = {p.id: _get_title_score(p) for p in title_papers}
    
    for paper in papers:
        if not paper.score_components:
            from ..models import ScoreComponents
            paper.score_components = ScoreComponents()
        
        # Get individual scores
        semantic_score = semantic_scores.get(paper.id, 0.0)
        title_score = title_scores.get(paper.id, 0.0)
        
        # Adjust weights based on whether description was provided
        if description_provided:
            # When description is provided, give more weight to semantic search
            hybrid_score = 0.8 * semantic_score + 0.2 * title_score
        else:
            # When only title is provided, balance between both
            hybrid_score = 0.6 * semantic_score + 0.4 * title_score
        
        paper.score_components.final = hybrid_score
    
    # Sort by hybrid score
    return sorted(papers, key=lambda p: p.score_components.final if p.score_components else 0, reverse=True)


def _get_semantic_score(paper: Paper) -> float:
    """Extract semantic score from paper reasons"""
    for reason in paper.reasons:
        if "Semantic similarity:" in reason:
            try:
                return float(reason.split(":")[1].strip())
            except (ValueError, IndexError):
                pass
    return 0.0


def _get_title_score(paper: Paper) -> float:
    """Get title-based relevance score"""
    if paper.score_components and paper.score_components.bm25:
        return paper.score_components.bm25
    return 0.0


def populate_embedding_store(papers: List[Paper]) -> None:
    """Populate embedding store with paper embeddings"""
    if not papers:
        return
    
    try:
        import openai
        from ..config import get_settings
        
        settings = get_settings()
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not available, skipping embedding population")
            return
        
        # Get embeddings for all papers
        paper_texts = []
        for paper in papers:
            text = f"{paper.title} {paper.abstract or ''}"
            paper_texts.append(text)
        
        # Batch process embeddings
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(paper_texts), batch_size):
            batch = paper_texts[i:i + batch_size]
            response = openai.embeddings.create(
                model="text-embedding-3-large",
                input=batch
            )
            batch_embeddings = [np.array(item.embedding) for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        # Add to embedding store
        embedding_store = get_embedding_store()
        embedding_store.add_papers(papers, all_embeddings)
        
        logger.info(f"Populated embedding store with {len(papers)} papers")
        
    except Exception as e:
        logger.error(f"Failed to populate embedding store: {e}")


def ensure_embedding_store_populated() -> None:
    """Ensure embedding store has papers by running a sample search if empty"""
    try:
        embedding_store = get_embedding_store()
        if embedding_store is None:
            logger.warning("Embedding store could not be initialized - FAISS may not be available")
            return
            
        stats = embedding_store.get_stats()
        
        if stats["total_papers"] == 0:
            logger.info("Embedding store is empty, populating with sample papers...")
            
            # Run a sample search to get papers
            from ..agents.search_agent import run_search
            from ..models import Filters
            
            sample_filters = Filters(limit=100)
            sample_papers = run_search("machine learning", sample_filters)
            
            if sample_papers:
                populate_embedding_store(sample_papers)
            else:
                logger.warning("Could not populate embedding store - no papers found in sample search")
    except Exception as e:
        logger.warning(f"Could not ensure embedding store is populated: {e}")


def _fallback_to_traditional_search(query: str, filters: SearchFilters, k: int) -> List[Paper]:
    """Fallback to traditional search when embedding store is not available"""
    try:
        from ..agents.search_agent import run_search
        from ..models import Filters
        
        # Convert SearchFilters to Filters for compatibility
        legacy_filters = Filters(
            start_year=filters.start_year,
            end_year=filters.end_year,
            include_keywords=filters.include_keywords,
            exclude_keywords=filters.exclude_keywords,
            venues=filters.venues,
            limit=k
        )
        
        papers = run_search(query, legacy_filters)
        logger.info(f"Fallback traditional search returned {len(papers)} papers")
        return papers
        
    except Exception as e:
        logger.error(f"Fallback search also failed: {e}")
        return []
