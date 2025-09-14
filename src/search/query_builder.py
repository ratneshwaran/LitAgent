from __future__ import annotations

import json
from typing import List, Dict, Any
from pathlib import Path

from ..models import SearchFilters, QueryBundle
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Load MeSH terms from JSON file
import json
from pathlib import Path

MESH_TERMS_FILE = Path(__file__).parent.parent / "resources" / "mesh_terms.json"

try:
    with open(MESH_TERMS_FILE, "r", encoding="utf-8") as f:
        MESH_TERMS = json.load(f)
except FileNotFoundError:
    # Fallback to basic terms if file not found
    MESH_TERMS = {
        "machine learning": ["machine learning", "artificial intelligence", "deep learning", "neural networks"],
        "healthcare": ["healthcare", "medical", "clinical", "health", "medicine"],
        "cancer": ["cancer", "oncology", "tumor", "neoplasm", "carcinoma"],
        "diabetes": ["diabetes", "diabetic", "glucose", "insulin"],
        "cardiovascular": ["cardiovascular", "heart", "cardiac", "vascular"],
        "mental health": ["mental health", "psychiatry", "psychology", "depression", "anxiety"],
        "covid": ["covid", "sars-cov-2", "coronavirus", "pandemic"],
        "drug": ["drug", "pharmaceutical", "medication", "therapy", "treatment"],
        "diagnosis": ["diagnosis", "diagnostic", "screening", "detection"],
        "treatment": ["treatment", "therapy", "intervention", "management"]
    }


def _expand_with_mesh_terms(query: str) -> List[str]:
    """Expand query with MeSH terms for biomedical concepts"""
    query_lower = query.lower()
    expanded_terms = []
    
    for concept, terms in MESH_TERMS.items():
        if concept in query_lower:
            expanded_terms.extend(terms)
    
    return list(set(expanded_terms))


def _build_exact_query(topic: str, filters: SearchFilters) -> str:
    """Build exact/phrase query with quoted key phrases"""
    # Extract key phrases and quote them
    key_phrases = []
    
    # Add main topic
    if len(topic.split()) > 1:
        key_phrases.append(f'"{topic}"')
    else:
        key_phrases.append(topic)
    
    # Add include keywords as phrases
    for keyword in filters.include_keywords:
        if len(keyword.split()) > 1:
            key_phrases.append(f'"{keyword}"')
        else:
            key_phrases.append(keyword)
    
    return " AND ".join(key_phrases)


def _build_expanded_query(topic: str, filters: SearchFilters) -> str:
    """Build boolean expanded query with synonyms and acronyms"""
    terms = [topic]
    
    # Add include keywords
    terms.extend(filters.include_keywords)
    
    # Add MeSH term expansions
    mesh_expansions = _expand_with_mesh_terms(topic)
    terms.extend(mesh_expansions)
    
    # Add common acronyms and synonyms
    expansions = {
        "ai": ["artificial intelligence", "machine learning"],
        "ml": ["machine learning", "artificial intelligence"],
        "dl": ["deep learning", "neural networks"],
        "nlp": ["natural language processing", "text mining"],
        "cv": ["computer vision", "image processing"],
        "healthcare": ["medical", "clinical", "health"],
        "cancer": ["oncology", "tumor", "neoplasm"],
        "diabetes": ["diabetic", "glucose", "insulin"]
    }
    
    for term in terms:
        term_lower = term.lower()
        if term_lower in expansions:
            terms.extend(expansions[term_lower])
    
    # Remove duplicates and build query
    unique_terms = list(set(terms))
    expanded_query = " OR ".join(unique_terms)
    
    # Add exclude terms
    if filters.exclude_keywords:
        exclude_query = " AND NOT ".join(filters.exclude_keywords)
        expanded_query = f"({expanded_query}) AND NOT ({exclude_query})"
    
    return expanded_query


def _build_domain_query(topic: str, filters: SearchFilters) -> str:
    """Build domain-specific query with related terms, datasets, and methods"""
    domain_terms = []
    
    # Add main topic
    domain_terms.append(topic)
    
    # Add domain-specific expansions
    if "healthcare" in topic.lower() or "medical" in topic.lower():
        domain_terms.extend([
            "clinical decision support",
            "electronic health records",
            "medical imaging",
            "patient monitoring",
            "drug discovery",
            "precision medicine",
            "telemedicine",
            "health informatics"
        ])
    
    if "machine learning" in topic.lower() or "ai" in topic.lower():
        domain_terms.extend([
            "supervised learning",
            "unsupervised learning",
            "reinforcement learning",
            "feature engineering",
            "model validation",
            "cross-validation",
            "hyperparameter tuning",
            "ensemble methods"
        ])
    
    if "deep learning" in topic.lower():
        domain_terms.extend([
            "convolutional neural networks",
            "recurrent neural networks",
            "transformer",
            "attention mechanism",
            "transfer learning",
            "fine-tuning",
            "data augmentation"
        ])
    
    # Add include keywords
    domain_terms.extend(filters.include_keywords)
    
    # Build domain query
    domain_query = " OR ".join(domain_terms)
    
    # Add exclude terms
    if filters.exclude_keywords:
        exclude_query = " AND NOT ".join(filters.exclude_keywords)
        domain_query = f"({domain_query}) AND NOT ({exclude_query})"
    
    return domain_query


def build_query_bundle(topic: str, filters: SearchFilters) -> QueryBundle:
    """Build a comprehensive query bundle for multi-source search"""
    
    # Build the three main queries
    exact_query = _build_exact_query(topic, filters)
    expanded_query = _build_expanded_query(topic, filters)
    domain_query = _build_domain_query(topic, filters)
    
    # Get MeSH terms
    mesh_terms = _expand_with_mesh_terms(topic)
    
    # Get related terms
    related_terms = []
    if "healthcare" in topic.lower():
        related_terms.extend(["clinical", "medical", "health", "patient"])
    if "machine learning" in topic.lower():
        related_terms.extend(["algorithm", "model", "prediction", "classification"])
    
    query_bundle = QueryBundle(
        exact_query=exact_query,
        expanded_query=expanded_query,
        domain_query=domain_query,
        mesh_terms=mesh_terms,
        related_terms=related_terms
    )
    
    return query_bundle


def save_query_bundle(query_bundle: QueryBundle, output_dir: Path, slug: str) -> None:
    """Save query bundle to debug directory"""
    debug_dir = output_dir / "debug" / slug
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    query_file = debug_dir / "query_bundle.json"
    with open(query_file, "w", encoding="utf-8") as f:
        json.dump(query_bundle.model_dump(), f, indent=2, ensure_ascii=False)
    
    logger.info(f"Query bundle saved to {query_file}")
