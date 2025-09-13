from __future__ import annotations

from pathlib import Path
from typing import List

from ..models import ReviewResult, MiniReview, Paper


def _md_matrix(result: ReviewResult) -> str:
    cols = result.matrix.columns
    rows = result.matrix.rows
    data = result.matrix.data
    
    # Create a more readable header
    header = "| **Paper** | " + " | ".join([f"**{col}**" for col in cols]) + " |\n"
    sep = "|" + " --- |" * (len(cols) + 1) + "\n"
    lines = [header, sep]
    
    for r in rows:
        # Truncate long paper titles for better readability
        paper_title = r.replace("|", "-")
        if len(paper_title) > 60:
            paper_title = paper_title[:57] + "..."
        
        cells = []
        for c in cols:
            cell_value = data[r][c].value.replace("\n", " ").strip()
            # Handle empty cells with better formatting
            if not cell_value:
                cell_value = "—"
            elif len(cell_value) > 50:
                cell_value = cell_value[:47] + "..."
            cells.append(cell_value)
        
        lines.append("| " + paper_title + " | " + " | ".join(cells) + " |\n")
    
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
    
    # Add title and metadata
    parts.append(f"# Literature Review: {result.topic}\n\n")
    parts.append(f"**Generated on:** {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
    parts.append(f"**Papers Reviewed:** {len(result.raw_papers)}\n")
    parts.append(f"**Venues:** {len(set([p.venue for p in result.raw_papers if p.venue]))}\n\n")
    
    # Executive summary with better formatting
    parts.append("## 📋 Executive Summary\n\n")
    parts.append(f"{result.synthesis.executive_summary}\n\n")
    
    # Key insights section
    parts.append("## 🔍 Key Insights\n\n")
    if result.synthesis.gaps:
        parts.append("### Identified Gaps\n")
        parts.extend([f"- {g}\n" for g in result.synthesis.gaps])
        parts.append("\n")
    
    if result.synthesis.future_work:
        parts.append("### Future Research Directions\n")
        parts.extend([f"- {f}\n" for f in result.synthesis.future_work])
        parts.append("\n")
    
    # Comparative matrix with better presentation
    parts.append("## 📊 Comparative Analysis\n\n")
    parts.append("The following table provides a comprehensive comparison of the reviewed papers:\n\n")
    parts.append(_md_matrix(result) + "\n")
    
    # Mini-reviews with better organization
    parts.append("## 📚 Detailed Paper Reviews\n\n")
    by_id = {r.paper_id: r for r in result.reviews}
    
    # Sort papers by relevance score if available
    sorted_papers = sorted(result.raw_papers, key=lambda p: p.citations_count or 0, reverse=True)
    
    for i, p in enumerate(sorted_papers, 1):
        mr = by_id.get(p.id)
        if mr:
            parts.append(f"### {i}. {p.title}\n\n")
            meta_parts = []
            if p.venue:
                meta_parts.append(f"**Venue:** {p.venue}")
            if p.year:
                meta_parts.append(f"**Year:** {p.year}")
            if p.citations_count:
                meta_parts.append(f"**Citations:** {p.citations_count}")
            if p.authors:
                meta_parts.append(f"**Authors:** {', '.join(p.authors[:3])}{' et al.' if len(p.authors) > 3 else ''}")
            
            if meta_parts:
                parts.append(" | ".join(meta_parts) + "\n\n")
            
            # Add summary sections with better formatting
            for title, fn in essential_sections:
                val = fn(mr)
                if val and val.strip():
                    parts.append(f"**{title}:**\n\n{val}\n\n")
            
            # Add grounding quotes if available
            if mr.summary.quotes:
                parts.append("**Key Quotes:**\n\n")
                for q in mr.summary.quotes:
                    sec = f" ({q.section})" if q.section else ""
                    parts.append(f"> {q.text}{sec}\n\n")
            
            parts.append("---\n\n")
    
    # References with better formatting
    parts.append("## 📖 References\n\n")
    parts.append(_md_references(result.raw_papers))

    content = "".join(parts)
    path.write_text(content, encoding="utf-8")
    return path
