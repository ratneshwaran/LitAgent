from __future__ import annotations

from pathlib import Path
from typing import List

from ..models import ReviewResult, MiniReview, Paper


def _md_matrix(result: ReviewResult) -> str:
    cols = result.matrix.columns
    rows = result.matrix.rows
    data = result.matrix.data
    header = "| Paper | " + " | ".join(cols) + " |\n"
    sep = "|" + " --- |" * (len(cols) + 1) + "\n"
    lines = [header, sep]
    for r in rows:
        cells = [data[r][c].value.replace("\n", " ") for c in cols]
        lines.append("| " + r.replace("|", "-") + " | " + " | ".join(cells) + " |\n")
    return "".join(lines)


essential_sections = [
    ("TL;DR", lambda mr: mr.summary.tldr),
    ("Methods", lambda mr: mr.summary.methods or ""),
    ("Results", lambda mr: mr.summary.results or ""),
    ("Limitations", lambda mr: mr.summary.limitations or ""),
    ("Critique", lambda mr: "\n".join([f"- {i.tag}: {i.rationale} (severity: {i.severity})" for i in mr.critique.issues]) or ""),
]


def _md_paper_section(paper: Paper, mr: MiniReview) -> str:
    lines: List[str] = []
    lines.append(f"### {paper.title}\n\n")
    meta = [paper.venue or "", str(paper.year or ""), "; ".join(paper.authors)]
    lines.append(f"{', '.join([m for m in meta if m])}\n\n")
    for title, fn in essential_sections:
        val = fn(mr)
        if val:
            lines.append(f"**{title}**\n\n{val}\n\n")
    if mr.summary.quotes:
        lines.append("**Grounding quotes**\n\n")
        for q in mr.summary.quotes:
            sec = f" ({q.section})" if q.section else ""
            lines.append(f"> {q.text}{sec}\n\n")
    return "".join(lines)


def _md_references(papers: List[Paper]) -> str:
    lines = ["### References\n\n"]
    for p in papers:
        authors = ", ".join(p.authors)
        year = f" ({p.year})" if p.year else ""
        venue = f" {p.venue}." if p.venue else ""
        doi = f" doi:{p.doi}" if p.doi else ""
        url = f" {p.url}" if p.url else ""
        lines.append(f"- {authors}.{year} {p.title}.{venue}{doi}{url}\n")
    lines.append("\n")
    return "".join(lines)


def export_markdown(result: ReviewResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    parts: List[str] = []
    parts.append(f"## Executive summary\n\n{result.synthesis.executive_summary}\n\n")
    parts.append("## Comparative matrix\n\n")
    parts.append(_md_matrix(result) + "\n\n")
    parts.append("## Mini-reviews\n\n")
    by_id = {r.paper_id: r for r in result.reviews}
    for p in result.raw_papers:
        mr = by_id.get(p.id)
        if mr:
            parts.append(_md_paper_section(p, mr))
    parts.append("## Gaps & future work\n\n")
    if result.synthesis.gaps:
        parts.extend([f"- {g}\n" for g in result.synthesis.gaps])
    if result.synthesis.future_work:
        parts.extend([f"- {f}\n" for f in result.synthesis.future_work])
    parts.append("\n")
    parts.append(_md_references(result.raw_papers))

    content = "".join(parts)
    path.write_text(content, encoding="utf-8")
    return path
