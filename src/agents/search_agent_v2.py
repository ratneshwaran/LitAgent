from __future__ import annotations

import time
import asyncio
from typing import List, Dict, Any, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models import Paper, SearchFilters, SearchDiagnostics, QueryBundle
from ..config_search import get_search_config
from ..utils.logging import get_logger
from ..utils.text import slugify

# Import search tools
from ..tools.openalex_tool import search_openalex
from ..tools.semantic_scholar_tool import search_semantic_scholar
from ..tools.europe_pmc_tool import search_europe_pmc
from ..tools.scholar_provider import search_scholar
# from ..tools.unpaywall_tool import enrich_papers_with_oa  # Disabled for performance
from ..tools.arxiv_tool import search_arxiv
from ..tools.pubmed_tool import search_pubmed
from ..tools.crossref_tool import search_crossref
from ..tools.biorxiv_tool import search_biorxiv
from ..tools.medrxiv_tool import search_medrxiv
from ..tools.dblp_tool import search_dblp
from ..tools.google_scholar_tool import search_google_scholar

# Import search modules
from ..search.query_builder import build_query_bundle, save_query_bundle
from ..search.fusion import (
    dedupe_papers, reciprocal_rank_fusion, calculate_bm25_scores,
    calculate_recency_scores, calculate_dense_scores, calculate_final_scores,
    save_search_report
)

logger = get_logger(__name__)


def _search_source(source_name: str, query: str, filters: SearchFilters) -> List[Paper]:
    """Search a single source and return papers"""
    try:
        if source_name == "openalex":
            return search_openalex(query, filters)
        elif source_name == "semanticscholar":
            return search_semantic_scholar(query, filters)
        elif source_name == "europe_pmc":
            return search_europe_pmc(query, filters)
        elif source_name == "scholar":
            return search_scholar(query, filters)
        elif source_name == "arxiv":
            return search_arxiv(query, filters)
        elif source_name == "pubmed":
            return search_pubmed(query, filters)
        elif source_name == "crossref":
            return search_crossref(query, filters)
        elif source_name == "biorxiv":
            return search_biorxiv(query, filters)
        elif source_name == "medrxiv":
            return search_medrxiv(query, filters)
        elif source_name == "dblp":
            return search_dblp(query, filters)
        elif source_name == "google_scholar":
            return search_google_scholar(query, filters)
        else:
            logger.warning(f"Unknown source: {source_name}")
            return []
    except Exception as e:
        logger.error(f"Error searching {source_name}: {e}")
        return []


def _search_all_sources(query: str, filters: SearchFilters) -> Dict[str, List[Paper]]:
    """Search all enabled sources concurrently"""
    config = get_search_config()
    enabled_sources = [name for name, enabled in config.enable_sources.items() if enabled]
    
    papers_by_source = {}
    
    # Use ThreadPoolExecutor for concurrent searches
    with ThreadPoolExecutor(max_workers=len(enabled_sources)) as executor:
        # Submit all search tasks
        future_to_source = {
            executor.submit(_search_source, source, query, filters): source
            for source in enabled_sources
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                papers = future.result()
                papers_by_source[source] = papers
                logger.info(f"{source} returned {len(papers)} papers")
            except Exception as e:
                logger.error(f"Search failed for {source}: {e}")
                papers_by_source[source] = []
    
    return papers_by_source


def _apply_soft_filters(papers: List[Paper], filters: SearchFilters) -> List[Paper]:
    """Apply soft filters with penalties instead of hard exclusions"""
    config = get_search_config()
    if config.strict_filters:
        # Use original hard filtering logic
        return _apply_hard_filters(papers, filters)
    
    # Soft filtering: penalize but don't exclude
    filtered_papers = []
    
    for paper in papers:
        penalty = 0.0
        
        # Year penalties
        if filters.start_year and paper.year and paper.year < filters.start_year:
            penalty += 0.3
        if filters.end_year and paper.year and paper.year > filters.end_year:
            penalty += 0.3
        
        # Venue penalties
        if filters.venues and paper.venue:
            venue_match = any(venue.lower() in paper.venue.lower() for venue in filters.venues)
            if not venue_match:
                penalty += 0.2
        
        # Keyword penalties
        if filters.include_keywords:
            text = f"{paper.title} {paper.abstract or ''}".lower()
            keyword_matches = sum(1 for keyword in filters.include_keywords if keyword.lower() in text)
            if keyword_matches == 0:
                penalty += 0.4
            else:
                penalty += 0.1 * (len(filters.include_keywords) - keyword_matches)
        
        # Exclude keyword penalties
        if filters.exclude_keywords:
            text = f"{paper.title} {paper.abstract or ''}".lower()
            exclude_matches = sum(1 for keyword in filters.exclude_keywords if keyword.lower() in text)
            penalty += 0.5 * exclude_matches
        
        # Review filter penalties
        if filters.review_filter == "soft":
            text = f"{paper.title} {paper.venue or ''}".lower()
            if any(term in text for term in ["survey", "review", "systematic review"]):
                penalty += 0.3
        elif filters.review_filter == "hard":
            text = f"{paper.title} {paper.venue or ''}".lower()
            if any(term in text for term in ["survey", "review", "systematic review"]):
                continue  # Hard exclude
        
        # Apply penalty to final score
        if paper.score_components:
            paper.score_components.final = max(0, paper.score_components.final - penalty)
        
        filtered_papers.append(paper)
    
    return filtered_papers


def _apply_hard_filters(papers: List[Paper], filters: SearchFilters) -> List[Paper]:
    """Apply hard filters (original logic)"""
    def ok(p: Paper) -> bool:
        if filters.start_year and (p.year or 0) < filters.start_year:
            return False
        if filters.end_year and (p.year or 9999) > filters.end_year:
            return False
        
        # Venue filtering
        if filters.venues:
            venue_text = (p.venue or "").lower()
            venue_matches = any(venue.lower() in venue_text for venue in filters.venues)
            if not venue_matches:
                return False
        
        # Keyword filtering
        if filters.include_keywords:
            text = f"{p.title} {p.abstract or ''}".lower()
            keyword_matches = 0
            for keyword in filters.include_keywords:
                keyword_words = [w.strip() for w in keyword.lower().split() if len(w.strip()) > 2]
                if keyword_words:
                    if all(any(word in text for word in keyword_words if len(word) > 2) for word in keyword_words):
                        keyword_matches += 1
                else:
                    if keyword.lower() in text:
                        keyword_matches += 1
            if keyword_matches == 0:
                return False
        
        # Exclude keywords
        if filters.exclude_keywords:
            text = f"{p.title} {p.abstract or ''}".lower()
            for keyword in filters.exclude_keywords:
                keyword_words = [w.strip() for w in keyword.lower().split() if len(w.strip()) > 2]
                if keyword_words:
                    if any(word in text for word in keyword_words if len(word) > 2):
                        return False
                else:
                    if keyword.lower() in text:
                        return False
        
        # Review filter
        if filters.review_filter == "hard":
            text = f"{p.title} {p.venue or ''}".lower()
            if any(term in text for term in ["survey", "review", "systematic review"]):
                return False
        
        return True
    
    return [p for p in papers if ok(p)]


def run_search_v2(topic: str, filters: SearchFilters) -> Tuple[List[Paper], SearchDiagnostics]:
    """Run the new multi-source search pipeline"""
    start_time = time.time()
    config = get_search_config()
    
    logger.info(f"Starting search for topic: {topic}")
    
    # Step 1: Build query bundle
    query_bundle = build_query_bundle(topic, filters)
    
    # Step 2: Search all sources with all queries
    all_papers = []
    papers_by_source = {}
    api_retries = {}
    
    queries = [
        ("exact", query_bundle.exact_query),
        ("expanded", query_bundle.expanded_query),
        ("domain", query_bundle.domain_query)
    ]
    
    for query_type, query in queries:
        logger.info(f"Searching with {query_type} query: {query}")
        
        # Search all sources for this query
        source_results = _search_all_sources(query, filters)
        
        # Add provenance information
        for source, papers in source_results.items():
            for rank, paper in enumerate(papers):
                from ..models import Provenance
                paper.provenance.append(Provenance(
                    source=source,
                    rank_in_source=rank,
                    query_id=query_type
                ))
            
            # Track papers by source
            if source not in papers_by_source:
                papers_by_source[source] = []
            papers_by_source[source].extend(papers)
            all_papers.extend(papers)
    
    # Step 3: Deduplication
    logger.info(f"Before deduplication: {len(all_papers)} papers")
    deduped_papers, dedupe_stats = dedupe_papers(all_papers)
    logger.info(f"After deduplication: {len(deduped_papers)} papers")
    
    # Step 4: Skip Unpaywall enrichment for performance
    # Unpaywall enrichment is disabled to improve search speed
    
    # Step 5: Apply filters
    filtered_papers = _apply_soft_filters(deduped_papers, filters)
    
    # Step 6: Ranking pipeline
    # Stage 1: RRF fusion
    fusion_results = reciprocal_rank_fusion(papers_by_source, k=60)
    
    # Stage 2: BM25 scoring
    bm25_results = calculate_bm25_scores(fusion_results, topic)
    
    # Stage 3: Recency scoring
    recency_results = calculate_recency_scores(bm25_results)
    
    # Stage 4: Dense re-ranking (top 200)
    top_200 = recency_results[:200]
    dense_results = calculate_dense_scores(top_200, topic)
    
    # Stage 5: Final scoring
    final_results = calculate_final_scores(dense_results)
    
    # Sort by final score
    ranked_papers = sorted(final_results, key=lambda p: p.score_components.final if p.score_components else 0, reverse=True)
    
    # Step 7: Apply limit
    final_papers = ranked_papers[:filters.limit]
    
    # Step 8: Create diagnostics
    per_source_counts = {source: len(papers) for source, papers in papers_by_source.items()}
    
    diagnostics = SearchDiagnostics(
        query_bundle=query_bundle,
        per_source_counts=per_source_counts,
        dedupe_stats=dedupe_stats,
        fusion_params={"k": 60, "weights": {"rrf": 0.6, "dense": 0.25, "recency": 0.15}},
        search_duration=time.time() - start_time,
        api_retries=api_retries
    )
    
    # Step 9: Save debug information
    slug = slugify(topic) or "search"
    output_dir = Path("outputs")
    save_query_bundle(query_bundle, output_dir, slug)
    save_search_report(final_papers, diagnostics, output_dir, slug)
    
    logger.info(f"Search completed: {len(final_papers)} papers in {diagnostics.search_duration:.2f}s")
    
    return final_papers, diagnostics
