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
    query_terms = query.lower().split()
    for paper, score in zip(papers, scores):
        if not paper.score_components:
            from ..models import ScoreComponents
            paper.score_components = ScoreComponents()
        # Base BM25
        bm25_score = float(score)
        
        # Title match boost: reward direct matches in title
        title_tokens = (paper.title or "").lower().split()
        if title_tokens and query_terms:
            title_matches = sum(1 for t in query_terms if any(t in w for w in title_tokens))
            ratio = title_matches / max(1, len(set(query_terms)))
            bm25_score += 0.5 * ratio  # modest but meaningful
        
        paper.score_components.bm25 = bm25_score
    
    return papers


def _tokenize(text: str) -> List[str]:
    return [t for t in text.lower().split() if t.isalpha() or any(c.isalnum() for c in t)]


def apply_prompt_coverage_boost(papers: List[Paper], query: str) -> List[Paper]:
    """Boost papers whose title/abstract cover more of the user's prompt terms and phrases.

    - Unigrams: fraction of unique prompt tokens covered
    - Bigrams: fraction of consecutive prompt token pairs found
    Adds small, stable boosts to bm25 to improve prompt faithfulness.
    """
    stop = {"the","and","or","for","with","without","on","in","of","to","a","an","by","about","using","use","study","papers","research"}
    q_tokens = [t for t in _tokenize(query) if t not in stop and len(t) > 2]
    if not q_tokens:
        return papers
    q_uni = list(dict.fromkeys(q_tokens))
    q_bi = [" ".join(q_tokens[i:i+2]) for i in range(len(q_tokens)-1)]

    for p in papers:
        text = f"{p.title} {p.abstract or ''}".lower()
        if not p.score_components:
            from ..models import ScoreComponents
            p.score_components = ScoreComponents()
        # Unigram coverage
        covered = sum(1 for t in q_uni if t in text)
        uni_cov = covered / max(1, len(q_uni))
        # Bigram coverage
        bi_cov = 0.0
        if q_bi:
            bi_cov = sum(1 for bg in q_bi if bg in text) / max(1, len(q_bi))
        # Boost capped to avoid overwhelming BM25
        boost = 0.4 * uni_cov + 0.3 * bi_cov
        p.score_components.bm25 = (p.score_components.bm25 or 0.0) + boost
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


def _venue_quality_score(venue: str | None) -> float:
    if not venue:
        return 0.0
    quality: Dict[str, float] = {
        "nature": 1.0,
        "science": 1.0,
        "cell": 0.95,
        "jama": 0.9,
        "new england journal of medicine": 0.95,
        "nejm": 0.95,
        "lancet": 0.95,
        "nature methods": 0.85,
        "nature communications": 0.8,
        "icml": 0.8,
        "neurips": 0.85,
        "cvpr": 0.8,
        "medical image analysis": 0.8,
        "nature reviews": 0.9,
    }
    v = venue.lower()
    return max((score for key, score in quality.items() if key in v), default=0.0)


def calculate_final_scores(papers: List[Paper]) -> List[Paper]:
    """Calculate final combined scores with venue and citation boosts.

    Conservative weighting to avoid overfitting to any single signal.
    """
    # Precompute citation normalization denominator
    import math
    max_citations = max((p.citations_count or 0) for p in papers) or 1
    norm_den = math.log1p(max(1000, max_citations))

    for paper in papers:
        if not paper.score_components:
            from ..models import ScoreComponents
            paper.score_components = ScoreComponents()

        # Base score from fusion signals
        rrf = paper.score_components.rrf or 0.0
        dense = paper.score_components.dense or 0.0
        recency = paper.score_components.recency or 0.0
        bm25 = paper.score_components.bm25 or 0.0

        # Emphasize lexical relevance (title/abstract) a bit more for prompt faithfulness
        base = 0.45 * rrf + 0.15 * dense + 0.3 * bm25 + 0.1 * recency

        # Venue boost (0..0.1)
        venue_boost = 0.1 * _venue_quality_score(paper.venue)

        # Citation boost using log normalization (0..0.1)
        citations = paper.citations_count or 0
        citations_boost = 0.1 * (math.log1p(citations) / norm_den)

        # PDF/DOI availability slight boosts (each up to 0.02/0.01)
        pdf_boost = 0.02 if getattr(paper, "pdf_url", None) else 0.0
        doi_boost = 0.01 if paper.doi else 0.0

        paper.score_components.final = base + venue_boost + citations_boost + pdf_boost + doi_boost

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
