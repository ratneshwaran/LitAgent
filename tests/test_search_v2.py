import pytest
from unittest.mock import patch, MagicMock
from src.agents.search_agent_v2 import run_search_v2
from src.models import SearchFilters


@pytest.fixture
def sample_filters():
    return SearchFilters(
        start_year=2020,
        end_year=2024,
        include_keywords=["machine learning", "healthcare"],
        exclude_keywords=["survey"],
        venues=["Nature", "Science"],
        limit=10,
        must_have_pdf=False,
        oa_only=False,
        review_filter="soft",
        enabled_sources=["openalex", "semanticscholar"]
    )


@patch('src.agents.search_agent_v2.get_search_config')
@patch('src.agents.search_agent_v2._search_all_sources')
@patch('src.agents.search_agent_v2.dedupe_papers')
@patch('src.agents.search_agent_v2.enrich_papers_with_oa')
@patch('src.agents.search_agent_v2.reciprocal_rank_fusion')
@patch('src.agents.search_agent_v2.calculate_bm25_scores')
@patch('src.agents.search_agent_v2.calculate_recency_scores')
@patch('src.agents.search_agent_v2.calculate_dense_scores')
@patch('src.agents.search_agent_v2.calculate_final_scores')
def test_run_search_v2(
    mock_final_scores,
    mock_dense_scores,
    mock_recency_scores,
    mock_bm25_scores,
    mock_rrf,
    mock_enrich,
    mock_dedupe,
    mock_search_sources,
    mock_config,
    sample_filters
):
    # Mock configuration
    mock_config.return_value.enable_sources = {
        "openalex": True,
        "semanticscholar": True,
        "unpaywall": True
    }
    mock_config.return_value.strict_filters = False
    
    # Mock search results
    from src.models import Paper, ScoreComponents
    mock_papers = [
        Paper(
            id="test1",
            source="openalex",
            title="Test Paper 1",
            abstract="Test abstract",
            authors=["Author 1"],
            year=2023,
            venue="Nature",
            doi="10.1000/test1",
            url="https://example.com/1",
            pdf_url=None,
            citations_count=10,
            keywords=[],
            score_components=ScoreComponents(rrf=0.8, bm25=0.7, dense=0.9, recency=0.8, final=0.8),
            reasons=["Test match"],
            provenance=[]
        )
    ]
    
    mock_search_sources.return_value = {"openalex": mock_papers}
    mock_dedupe.return_value = (mock_papers, {"total": 1, "doi_deduped": 0, "title_deduped": 0, "final": 1})
    mock_enrich.return_value = mock_papers
    mock_rrf.return_value = mock_papers
    mock_bm25_scores.return_value = mock_papers
    mock_recency_scores.return_value = mock_papers
    mock_dense_scores.return_value = mock_papers
    mock_final_scores.return_value = mock_papers
    
    # Run the search
    papers, diagnostics = run_search_v2("machine learning healthcare", sample_filters)
    
    # Verify results
    assert len(papers) == 1
    assert papers[0].title == "Test Paper 1"
    assert diagnostics.search_duration > 0
    assert "openalex" in diagnostics.per_source_counts


def test_search_filters_validation():
    """Test that SearchFilters validates correctly"""
    filters = SearchFilters(
        start_year=2020,
        end_year=2024,
        include_keywords=["AI", "healthcare"],
        exclude_keywords=["survey"],
        venues=["Nature"],
        limit=25,
        must_have_pdf=True,
        oa_only=True,
        review_filter="hard",
        enabled_sources=["openalex", "semanticscholar", "arxiv"]
    )
    
    assert filters.start_year == 2020
    assert filters.end_year == 2024
    assert "AI" in filters.include_keywords
    assert "survey" in filters.exclude_keywords
    assert filters.must_have_pdf is True
    assert filters.oa_only is True
    assert filters.review_filter == "hard"
    assert len(filters.enabled_sources) == 3
