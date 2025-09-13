from __future__ import annotations

from unittest.mock import patch

from ..src.models import Paper
from ..src.agents.summarize_agent import summarize_paper


def test_summarizer_heuristic_when_no_abstract():
    paper = Paper(id="1", source="arxiv", title="T", abstract=None, authors=["A"], year=2024)
    s = summarize_paper(paper)
    assert s.tldr
    assert len(s.quotes) <= 3


def test_summarizer_llm_parses_json():
    paper = Paper(id="1", source="arxiv", title="T", abstract="A short abstract.", authors=["A"], year=2024)

    class Dummy:
        content = (
            '{"tldr":"ok","methods":"m","results":"r","limitations":"l","citations":3,'
            '"grounding_score":0.7,"quotes":[{"text":"q1","section":"abstract"},{"text":"q2"},{"text":"q3"},{"text":"q4"}]}'
        )

    with patch("..src.agents.summarize_agent._get_llm", create=True) as mock_get_llm:
        class LLMDummy:
            def invoke(self, x):
                return Dummy()

        mock_get_llm.return_value = LLMDummy()
        s = summarize_paper(paper)
        assert s.tldr == "ok"
        assert s.methods == "m"
        assert s.citations == 3
        assert 0 <= s.grounding_score <= 1
        assert len(s.quotes) <= 3
