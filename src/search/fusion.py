from __future__ import annotations

import json
from typing import List, Dict, Any, Tuple
from pathlib import Path
from collections import defaultdict
import math

from ..models import Paper, SearchFilters, SearchDiagnostics, QueryBundle
from ..utils.logging import get_logger

logger = get_logger(__name__)


def _normalize_title(title: str) -> str:
    """Normalize title for deduplication"""
    return "".join(c.lower() for c in title if c.isalnum() or c.isspace()).strip()


def _fuzzy_title_similarity(title1: str, title2: str) -> float:
    """Calculate fuzzy similarity between titles"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, title1, title2).ratio()


def dedupe_papers(papers: List[Paper]) -> Tuple[List[Paper], Dict[str, int]]:
    """Deduplicate papers by DOI and fuzzy title matching"""
    seen_doi = {}
    seen_titles = {}
    deduped_papers = []
    dedupe_stats = {"total": len(papers), "doi_deduped": 0, "title_deduped": 0, "final": 0}
    
    for paper in papers:
        # Check DOI duplicates first (most reliable)
        if paper.doi:
            doi_key = paper.doi.lower().strip()
            if doi_key in seen_doi:
                dedupe_stats["doi_deduped"] += 1
                continue
            seen_doi[doi_key] = paper
        
        # Check for similar titles
        normalized_title = _normalize_title(paper.title)
        is_duplicate = False
        
        for existing_title, existing_paper in seen_titles.items():
            if _fuzzy_title_similarity(normalized_title, existing_title) > 0.92:
                # Prefer paper with more complete information
                if (len(paper.abstract or "") > len(existing_paper.abstract or "") or
                    (paper.citations_count or 0) > (existing_paper.citations_count or 0)):
                    # Replace existing paper
                    seen_titles[existing_title] = paper
                is_duplicate = True
                dedupe_stats["title_deduped"] += 1
                break
        
        if not is_duplicate:
            seen_titles[normalized_title] = paper
            deduped_papers.append(paper)
    
    dedupe_stats["final"] = len(deduped_papers)
    return deduped_papers, dedupe_stats


def reciprocal_rank_fusion(papers_by_source: Dict[str, List[Paper]], k: int = 60) -> List[Paper]:
    """Apply Reciprocal Rank Fusion (RRF) to combine results from multiple sources"""
    paper_scores = defaultdict(float)
    paper_objects = {}
    
    for source, papers in papers_by_source.items():
        for rank, paper in enumerate(papers):
            # RRF score: 1 / (k + rank)
            rrf_score = 1.0 / (k + rank + 1)
            paper_scores[paper.id] += rrf_score
            paper_objects[paper.id] = paper
    
    # Sort by RRF score
    sorted_papers = sorted(paper_objects.values(), key=lambda p: paper_scores[p.id], reverse=True)
    
    # Update RRF scores in paper objects
    for paper in sorted_papers:
        if not paper.score_components:
            from ..models import ScoreComponents
            paper.score_components = ScoreComponents()
        paper.score_components.rrf = paper_scores[paper.id]
    
    return sorted_papers


def calculate_bm25_scores(papers: List[Paper], query: str) -> List[Paper]:
    """Calculate BM25 scores for papers"""
    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        logger.warning("rank_bm25 not available, skipping BM25 scoring")
        return papers
    
    # Prepare documents (title + abstract)
    documents = []
    for paper in papers:
        doc = f"{paper.title} {paper.abstract or ''}"
        documents.append(doc.lower().split())
    
    if not documents:
        return papers
    
    # Create BM25 index
    bm25 = BM25Okapi(documents)
    
    # Calculate scores
    query_terms = query.lower().split()
    scores = bm25.get_scores(query_terms)
    
    # Update papers with BM25 scores
    for paper, score in zip(papers, scores):
        if not paper.score_components:
            from ..models import ScoreComponents
            paper.score_components = ScoreComponents()
        paper.score_components.bm25 = score
    
    return papers


def calculate_recency_scores(papers: List[Paper]) -> List[Paper]:
    """Calculate recency scores using sigmoid function"""
    import math
    
    for paper in papers:
        if not paper.score_components:
            from ..models import ScoreComponents
            paper.score_components = ScoreComponents()
        
        if paper.year:
            # Sigmoid function: recency_weight = sigmoid((year - 2019)/3)
            recency_score = 1 / (1 + math.exp(-(paper.year - 2019) / 3))
            paper.score_components.recency = recency_score
        else:
            paper.score_components.recency = 0.0
    
    return papers


def calculate_dense_scores(papers: List[Paper], query: str) -> List[Paper]:
    """Calculate dense embedding scores using OpenAI embeddings"""
    try:
        import openai
        from ..config import get_settings
        
        settings = get_settings()
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not available, skipping dense scoring")
            return papers
        
        # Get query embedding
        query_response = openai.embeddings.create(
            model="text-embedding-3-large",
            input=query
        )
        query_embedding = query_response.data[0].embedding
        
        # Get paper embeddings
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
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        # Calculate cosine similarities
        import numpy as np
        
        query_vec = np.array(query_embedding)
        for paper, embedding in zip(papers, all_embeddings):
            if not paper.score_components:
                from ..models import ScoreComponents
                paper.score_components = ScoreComponents()
            
            paper_vec = np.array(embedding)
            cosine_sim = np.dot(query_vec, paper_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(paper_vec))
            paper.score_components.dense = cosine_sim
    
    except Exception as e:
        logger.warning(f"Dense scoring failed: {e}")
    
    return papers


def calculate_final_scores(papers: List[Paper]) -> List[Paper]:
    """Calculate final combined scores"""
    for paper in papers:
        if not paper.score_components:
            from ..models import ScoreComponents
            paper.score_components = ScoreComponents()
        
        # Final score: 0.6*rrf + 0.25*dense + 0.15*recency
        final_score = (
            0.6 * paper.score_components.rrf +
            0.25 * paper.score_components.dense +
            0.15 * paper.score_components.recency
        )
        paper.score_components.final = final_score
    
    return papers


def save_search_report(papers: List[Paper], diagnostics: SearchDiagnostics, output_dir: Path, slug: str) -> None:
    """Save search report with scores and provenance"""
    debug_dir = output_dir / "debug" / slug
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare report data
    report_data = {
        "diagnostics": diagnostics.model_dump(),
        "papers": []
    }
    
    for paper in papers:
        paper_data = {
            "id": paper.id,
            "title": paper.title,
            "source": paper.source,
            "year": paper.year,
            "venue": paper.venue,
            "doi": paper.doi,
            "citations_count": paper.citations_count,
            "score_components": paper.score_components.model_dump() if paper.score_components else None,
            "reasons": paper.reasons,
            "provenance": [p.model_dump() for p in paper.provenance]
        }
        report_data["papers"].append(paper_data)
    
    # Save report
    report_file = debug_dir / "search_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Search report saved to {report_file}")
