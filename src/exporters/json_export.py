from __future__ import annotations

import json
from pathlib import Path
from typing import List

from ..models import ReviewResult


def export_json(result: ReviewResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create structured data with the new format
    by_id = {r.paper_id: r for r in result.reviews}
    
    # Comparative analysis (concise table data)
    comparative = []
    for paper in result.raw_papers:
        mr = by_id.get(paper.id)
        
        # Critique flags
        critique_flags = []
        if mr and mr.critique.issues:
            for issue in mr.critique.issues:
                critique_flags.append({
                    "tag": issue.tag,
                    "severity": issue.severity,
                    "icon": _get_critique_icon(issue.tag)
                })
        
        comparative.append({
            "id": paper.id,
            "title": paper.title,
            "title_link": f"https://doi.org/{paper.doi}" if paper.doi else paper.url,
            "venue": paper.venue,
            "year": paper.year,
            "methods": mr.summary.methods[:50] + "..." if mr and mr.summary.methods and len(mr.summary.methods) > 50 else (mr.summary.methods if mr else "Not specified"),
            "results": mr.summary.results[:50] + "..." if mr and mr.summary.results and len(mr.summary.results) > 50 else (mr.summary.results if mr else "Not specified"),
            "critique_flags": critique_flags
        })
    
    # Detailed reviews (card-style data)
    detailed = []
    for paper in result.raw_papers:
        mr = by_id.get(paper.id)
        if mr:
            # Format methods, results, limitations as bullet lists
            methods_bullets = _format_as_bullets_json(mr.summary.methods) if mr.summary.methods else []
            results_bullets = _format_as_bullets_json(mr.summary.results) if mr.summary.results else []
            limitations_bullets = _format_as_bullets_json(mr.summary.limitations) if mr.summary.limitations else []
            
            # Critique flags with severity
            critique_flags = []
            for issue in mr.critique.issues:
                critique_flags.append({
                    "tag": issue.tag,
                    "rationale": issue.rationale,
                    "severity": issue.severity,
                    "icon": _get_severity_icon(issue.severity)
                })
            
            # Key quotes
            quotes = []
            for q in mr.summary.quotes:
                quotes.append({
                    "text": q.text,
                    "section": q.section
                })
            
            detailed.append({
                "id": paper.id,
                "title": paper.title,
                "title_link": f"https://doi.org/{paper.doi}" if paper.doi else paper.url,
                "venue": paper.venue,
                "year": paper.year,
                "authors": paper.authors,
                "tldr": mr.summary.tldr,
                "methods": methods_bullets,
                "results": results_bullets,
                "limitations": limitations_bullets,
                "critique_flags": critique_flags,
                "quotes": quotes
            })
    
    # Structured data
    data = {
        "metadata": {
            "topic": result.topic,
            "generated_at": result.created_at.isoformat(),
            "papers_reviewed": len(result.raw_papers),
            "venues": len(set([p.venue for p in result.raw_papers if p.venue]))
        },
        "executive_summary": result.synthesis.executive_summary,
        "key_insights": {
            "gaps": result.synthesis.gaps,
            "future_work": result.synthesis.future_work
        },
        "comparative": comparative,
        "detailed": detailed,
        "references": [
            {
                "id": paper.id,
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.year,
                "venue": paper.venue,
                "doi": paper.doi,
                "url": paper.url
            }
            for paper in result.raw_papers
        ]
    }
    
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def _format_as_bullets_json(text: str) -> List[str]:
    """Convert text into bullet points for JSON"""
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    bullets = []
    for sentence in sentences:
        if len(sentence) > 10:
            bullets.append(sentence)
    return bullets if bullets else [text]


def _get_critique_icon(tag: str) -> str:
    """Get icon for critique tag"""
    tag_lower = tag.lower()
    if "baseline" in tag_lower:
        return "⚠️"
    elif "reproducibility" in tag_lower:
        return "🔒"
    elif "data" in tag_lower:
        return "📊"
    elif "evaluation" in tag_lower:
        return "📈"
    else:
        return "⚠️"


def _get_severity_icon(severity: str) -> str:
    """Get icon for critique severity"""
    severity_lower = severity.lower()
    if "high" in severity_lower:
        return "🔴"
    elif "medium" in severity_lower or "med" in severity_lower:
        return "🟡"
    else:
        return "🟢"
