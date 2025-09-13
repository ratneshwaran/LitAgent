from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from ..src.models import Filters, Paper, MiniReview, Summary, Critique, CritiqueIssue
from ..src.graph.build_graph import build_graph


def test_graph_pipeline_creates_outputs(tmp_path: Path):
    # Mock search to return 3 papers
    papers = [
        Paper(id=f"p{i}", source="arxiv", title=f"Paper {i}", abstract="Text", authors=["A"], year=2023)
        for i in range(3)
    ]

    with patch("..src.agents.search_agent.run_search", return_value=papers), \
         patch("..src.agents.summarize_agent.summarize_paper", return_value=Summary(tldr="t", methods="m", results="r", limitations="l", citations=1, grounding_score=0.5, quotes=[])), \
         patch("..src.agents.critic_agent.critique_paper", return_value=Critique(issues=[CritiqueIssue(tag="missing_baselines", severity="low", rationale="")])):
        g = build_graph(str(tmp_path / "check.sqlite"))
        out = g.invoke({"topic": "test", "filters": Filters(limit=3)})
        md = out["report_md"]
        js = out["report_json"]
        assert Path(md).exists()
        assert Path(js).exists()
