from __future__ import annotations

from typing import List, Dict

from ..models import Paper, MiniReview, ComparativeMatrix, ComparativeCell, Synthesis


COMPARISON_COLUMNS = [
    "Venue",
    "Year",
    "Citations",
    "Methods",
    "Results",
    "Limitations",
]


def build_comparative_matrix(papers: List[Paper], reviews: List[MiniReview]) -> ComparativeMatrix:
    rows = [p.title for p in papers]
    cols = COMPARISON_COLUMNS
    data: Dict[str, Dict[str, ComparativeCell]] = {}
    by_id = {r.paper_id: r for r in reviews}
    for p in papers:
        r = by_id.get(p.id)
        s = r.summary if r else None
        data[p.title] = {
            "Venue": ComparativeCell(value=p.venue or ""),
            "Year": ComparativeCell(value=str(p.year or "")),
            "Citations": ComparativeCell(value=str(s.citations or p.citations_count or "")),
            "Methods": ComparativeCell(value=(s.methods or "")[:140]),
            "Results": ComparativeCell(value=(s.results or "")[:140]),
            "Limitations": ComparativeCell(value=(s.limitations or "")[:140]),
        }
    return ComparativeMatrix(columns=cols, rows=rows, data=data)


def synthesize(papers: List[Paper], reviews: List[MiniReview]) -> Synthesis:
    # Simple synthesis: extract common themes and gaps
    methods = [r.summary.methods or "" for r in reviews]
    limitations = [r.summary.limitations or "" for r in reviews]
    exec_summary = (
        f"Reviewed {len(papers)} papers across {len(set([p.venue for p in papers if p.venue]))} venues. "
        "We summarize methods, results, and limitations, and identify common gaps."
    )
    gaps = []
    text_all = "\n".join(limitations).lower()
    if "data" in text_all and "availability" in text_all:
        gaps.append("Limited data availability and standardization across studies.")
    if not any("baseline" in (r.summary.results or "").lower() for r in reviews):
        gaps.append("Few works report comparisons against strong baselines.")
    if not gaps:
        gaps = ["More systematic benchmarking is needed."]
    future = ["Open-sourcing code and datasets", "Larger, diverse cohorts", "Robust baseline comparisons"]
    return Synthesis(executive_summary=exec_summary, gaps=gaps, future_work=future)
