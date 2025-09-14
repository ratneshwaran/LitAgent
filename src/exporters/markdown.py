from __future__ import annotations

from pathlib import Path
from typing import List

from ..models import ReviewResult, MiniReview, Paper


def _md_matrix(result: ReviewResult) -> str:
    """Create a concise comparative analysis table with max 5 columns"""
    by_id = {r.paper_id: r for r in result.reviews}
    
    # Build concise table with key information
    header = "| **Paper** | **Venue | Year** | **Methods** | **Results** | **Critique Flags** |\n"
    sep = "| --- | --- | --- | --- | --- | --- |\n"
    lines = [header, sep]
    
    for paper in result.raw_papers:
        mr = by_id.get(paper.id)
        
        # Paper title with link
        paper_title = paper.title.replace("|", "-")
        if len(paper_title) > 50:
            paper_title = paper_title[:47] + "..."
        
        # Add link if available
        if paper.doi:
            paper_cell = f"[{paper_title}](https://doi.org/{paper.doi})"
        elif paper.url:
            paper_cell = f"[{paper_title}]({paper.url})"
        else:
            paper_cell = paper_title
        
        # Venue and year
        venue_year = f"{paper.venue or 'Unknown'} | {paper.year or 'N/A'}"
        
        # Methods (truncated)
        methods = ""
        if mr and mr.summary.methods:
            methods = mr.summary.methods[:50] + ("..." if len(mr.summary.methods) > 50 else "")
        else:
            methods = "Not specified"
        
        # Results (truncated)
        results = ""
        if mr and mr.summary.results:
            results = mr.summary.results[:50] + ("..." if len(mr.summary.results) > 50 else "")
        else:
            results = "Not specified"
        
        # Critique flags with icons
        critique_flags = []
        if mr and mr.critique.issues:
            for issue in mr.critique.issues:
                if "baseline" in issue.tag.lower():
                    critique_flags.append("⚠️ missing baselines")
                elif "reproducibility" in issue.tag.lower():
                    critique_flags.append("🔒 reproducibility")
                elif "data" in issue.tag.lower():
                    critique_flags.append("📊 data issues")
                elif "evaluation" in issue.tag.lower():
                    critique_flags.append("📈 evaluation")
                else:
                    critique_flags.append(f"⚠️ {issue.tag}")
        
        critique_cell = ", ".join(critique_flags[:2])  # Max 2 flags
        if len(critique_flags) > 2:
            critique_cell += f" (+{len(critique_flags) - 2} more)"
        
        if not critique_cell:
            critique_cell = "✅ No major issues"
        
        lines.append(f"| {paper_cell} | {venue_year} | {methods} | {results} | {critique_cell} |\n")
    
    return "".join(lines)


essential_sections = [
    ("TL;DR", lambda mr: mr.summary.tldr),
    ("Methods", lambda mr: mr.summary.methods or ""),
    ("Results", lambda mr: mr.summary.results or ""),
    ("Limitations", lambda mr: mr.summary.limitations or ""),
    ("Critique", lambda mr: "\n".join([f"- {i.tag}: {i.rationale} (severity: {i.severity})" for i in mr.critique.issues]) or ""),
]


def _md_paper_section(paper: Paper, mr: MiniReview) -> str:
    """Create a clean card-style section for each paper"""
    lines: List[str] = []
    
    # Title with link
    if paper.doi:
        title_link = f"[{paper.title}](https://doi.org/{paper.doi})"
    elif paper.url:
        title_link = f"[{paper.title}]({paper.url})"
    else:
        title_link = paper.title
    
    lines.append(f"### {title_link}\n")
    
    # Metadata line
    meta_parts = []
    if paper.venue:
        meta_parts.append(f"**Venue:** {paper.venue}")
    if paper.year:
        meta_parts.append(f"**Year:** {paper.year}")
    if paper.authors:
        authors_str = ", ".join(paper.authors[:3])
        if len(paper.authors) > 3:
            authors_str += " et al."
        meta_parts.append(f"**Authors:** {authors_str}")
    
    if meta_parts:
        lines.append(" | ".join(meta_parts) + "\n")
    
    lines.append("\n")
    
    # TL;DR (2-3 sentences max)
    if mr.summary.tldr:
        tldr = mr.summary.tldr
        # Truncate to 2-3 sentences
        sentences = tldr.split('. ')
        if len(sentences) > 3:
            tldr = '. '.join(sentences[:3]) + "..."
        lines.append(f"**TL;DR:** {tldr}\n\n")
    
    # Methods as bullet list
    if mr.summary.methods:
        methods_bullets = _format_as_bullets(mr.summary.methods)
        lines.append(f"**Methods:**\n{methods_bullets}\n")
    
    # Results as bullet list
    if mr.summary.results:
        results_bullets = _format_as_bullets(mr.summary.results)
        lines.append(f"**Results:**\n{results_bullets}\n")
    
    # Limitations as bullet list
    if mr.summary.limitations:
        limitations_bullets = _format_as_bullets(mr.summary.limitations)
        lines.append(f"**Limitations:**\n{limitations_bullets}\n")
    
    # Critique flags with severity
    if mr.critique.issues:
        lines.append("**Critique Flags:**\n")
        for issue in mr.critique.issues:
            severity_icon = _get_severity_icon(issue.severity)
            lines.append(f"- {severity_icon} **{issue.tag}:** {issue.rationale}\n")
        lines.append("\n")
    
    # Key quotes in blockquote style
    if mr.summary.quotes:
        lines.append("**Key Quotes:**\n")
        for q in mr.summary.quotes:
            section_marker = f" *({q.section})*" if q.section else ""
            lines.append(f"> {q.text}{section_marker}\n\n")
    
    lines.append("---\n\n")
    return "".join(lines)


def _format_as_bullets(text: str) -> str:
    """Convert text into bullet points"""
    # Split by sentences and create bullets
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    bullets = []
    for sentence in sentences:
        if len(sentence) > 10:  # Only include substantial sentences
            bullets.append(f"- {sentence}")
    return "\n".join(bullets) if bullets else "- " + text


def _get_severity_icon(severity: str) -> str:
    """Get icon for critique severity"""
    severity_lower = severity.lower()
    if "high" in severity_lower:
        return "🔴"
    elif "medium" in severity_lower or "med" in severity_lower:
        return "🟡"
    else:
        return "🟢"


def _md_references(papers: List[Paper]) -> str:
    """Format references as a numbered list with clickable links"""
    lines = ["## 📖 References\n\n"]
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.authors) if p.authors else "Unknown authors"
        year = f" ({p.year})" if p.year else ""
        venue = f" {p.venue}." if p.venue else ""
        
        # Create clickable link
        if p.doi:
            link = f"https://doi.org/{p.doi}"
        elif p.url:
            link = p.url
        else:
            link = None
        
        if link:
            lines.append(f"{i}. [{authors}{year} {p.title}.{venue}]({link})\n")
        else:
            lines.append(f"{i}. {authors}{year} {p.title}.{venue}\n")
    
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
    
    # Key insights section with icons
    parts.append("## 🔍 Key Insights\n\n")
    if result.synthesis.gaps:
        parts.append("### 🔍 Identified Gaps\n")
        for gap in result.synthesis.gaps:
            parts.append(f"- {gap}\n")
        parts.append("\n")
    
    if result.synthesis.future_work:
        parts.append("### 🚀 Future Research Directions\n")
        for future in result.synthesis.future_work:
            parts.append(f"- {future}\n")
        parts.append("\n")
    
    # Comparative matrix with concise presentation
    parts.append("## 📊 Comparative Analysis\n\n")
    parts.append("High-level comparison of reviewed papers (click titles for full details):\n\n")
    parts.append(_md_matrix(result) + "\n")
    
    # Detailed reviews with card-style sections
    parts.append("## 📚 Detailed Paper Reviews\n\n")
    by_id = {r.paper_id: r for r in result.reviews}
    
    # Sort papers by citations for better organization
    sorted_papers = sorted(result.raw_papers, key=lambda p: p.citations_count or 0, reverse=True)
    
    for i, p in enumerate(sorted_papers, 1):
        mr = by_id.get(p.id)
        if mr:
            parts.append(f"### {i}. {p.title}\n\n")
            parts.append(_md_paper_section(p, mr))
    
    # References with numbered list and clickable links
    parts.append(_md_references(result.raw_papers))

    content = "".join(parts)
    path.write_text(content, encoding="utf-8")
    return path
