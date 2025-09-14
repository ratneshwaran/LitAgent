from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class SearchConfig:
    # Source toggles
    enable_sources: Dict[str, bool]
    scholar_provider: Literal["serpapi", "serper", "none"]
    
    # API keys
    openalex_email: Optional[str]
    s2_api_key: Optional[str]
    serpapi_key: Optional[str]
    serper_api_key: Optional[str]
    unpaywall_email: Optional[str]
    
    # Search parameters
    search_max_per_source: int
    fusion_top_k: int
    rerank_embedding_provider: str
    strict_filters: bool
    
    # Rate limiting
    requests_per_minute: int
    retry_attempts: int
    retry_delay: float


def get_search_config() -> SearchConfig:
    load_dotenv()
    
    # Source configuration
    enable_sources = {
        "openalex": os.getenv("ENABLE_OPENALEX", "true").lower() == "true",
        "semanticscholar": os.getenv("ENABLE_SEMANTICSCHOLAR", "true").lower() == "true",
        "crossref": os.getenv("ENABLE_CROSSREF", "true").lower() == "true",
        "arxiv": os.getenv("ENABLE_ARXIV", "true").lower() == "true",
        "europe_pmc": os.getenv("ENABLE_EUROPE_PMC", "true").lower() == "true",
        "biorxiv": os.getenv("ENABLE_BIORXIV", "true").lower() == "true",
        "medrxiv": os.getenv("ENABLE_MEDRXIV", "true").lower() == "true",
        "dblp": os.getenv("ENABLE_DBLP", "true").lower() == "true",
        "scholar": os.getenv("ENABLE_SCHOLAR", "true").lower() == "true",
    }
    
    return SearchConfig(
        enable_sources=enable_sources,
        scholar_provider=os.getenv("SCHOLAR_PROVIDER", "serpapi"),
        openalex_email=os.getenv("OPENALEX_EMAIL"),
        s2_api_key=os.getenv("S2_API_KEY"),
        serpapi_key=os.getenv("SERPAPI_KEY"),
        serper_api_key=os.getenv("SERPER_API_KEY"),
        unpaywall_email=os.getenv("UNPAYWALL_EMAIL"),
        search_max_per_source=int(os.getenv("SEARCH_MAX_PER_SOURCE", "50")),
        fusion_top_k=int(os.getenv("FUSION_TOP_K", "200")),
        rerank_embedding_provider=os.getenv("RERANK_EMBEDDING_PROVIDER", "openai"),
        strict_filters=os.getenv("STRICT_FILTERS", "false").lower() == "true",
        requests_per_minute=int(os.getenv("REQUESTS_PER_MINUTE", "60")),
        retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
        retry_delay=float(os.getenv("RETRY_DELAY", "1.0")),
    )
