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
        
        # Generate more meaningful content for empty fields
        methods = s.methods if s and s.methods else _extract_methods_from_abstract(p.abstract or "")
        results = s.results if s and s.results else _extract_results_from_abstract(p.abstract or "")
        limitations = s.limitations if s and s.limitations else _extract_limitations_from_abstract(p.abstract or "")
        
        data[p.title] = {
            "Venue": ComparativeCell(value=p.venue or "Unknown"),
            "Year": ComparativeCell(value=str(p.year or "N/A")),
            "Citations": ComparativeCell(value=str(s.citations or p.citations_count or "N/A")),
            "Methods": ComparativeCell(value=methods[:140]),
            "Results": ComparativeCell(value=results[:140]),
            "Limitations": ComparativeCell(value=limitations[:140]),
        }
    return ComparativeMatrix(columns=cols, rows=rows, data=data)


def _extract_methods_from_abstract(abstract: str) -> str:
    """Extract method information from abstract using keyword matching"""
    if not abstract:
        return "Not specified"
    
    abstract_lower = abstract.lower()
    method_keywords = ["method", "approach", "technique", "algorithm", "model", "framework", "system"]
    
    for keyword in method_keywords:
        if keyword in abstract_lower:
            # Find sentences containing the keyword
            sentences = abstract.split(".")
            for sentence in sentences:
                if keyword in sentence.lower():
                    return sentence.strip()[:140]
    
    return "Method details not available in abstract"


def _extract_results_from_abstract(abstract: str) -> str:
    """Extract results information from abstract using keyword matching"""
    if not abstract:
        return "Not specified"
    
    abstract_lower = abstract.lower()
    result_keywords = ["result", "achieve", "improve", "accuracy", "performance", "outcome", "finding"]
    
    for keyword in result_keywords:
        if keyword in abstract_lower:
            sentences = abstract.split(".")
            for sentence in sentences:
                if keyword in sentence.lower():
                    return sentence.strip()[:140]
    
    return "Results not detailed in abstract"


def _extract_limitations_from_abstract(abstract: str) -> str:
    """Extract limitations information from abstract using keyword matching"""
    if not abstract:
        return "Not specified"
    
    abstract_lower = abstract.lower()
    limitation_keywords = ["limit", "constraint", "challenge", "difficult", "restriction", "drawback"]
    
    for keyword in limitation_keywords:
        if keyword in abstract_lower:
            sentences = abstract.split(".")
            for sentence in sentences:
                if keyword in sentence.lower():
                    return sentence.strip()[:140]
    
    return "Limitations not mentioned in abstract"


def synthesize(papers: List[Paper], reviews: List[MiniReview]) -> Synthesis:
    # Enhanced synthesis with better analysis
    venues = [p.venue for p in papers if p.venue]
    unique_venues = len(set(venues))
    years = [p.year for p in papers if p.year]
    recent_papers = len([y for y in years if y and y >= 2020])
    
    # Create more informative executive summary
    exec_summary = (
        f"This literature review analyzed {len(papers)} papers across {unique_venues} venues, "
        f"with {recent_papers} papers published since 2020. The analysis reveals key trends, "
        f"methodological approaches, and identifies critical gaps in the current research landscape."
    )
    
    # Enhanced gap analysis
    gaps = []
    limitations_text = "\n".join([r.summary.limitations or "" for r in reviews]).lower()
    methods_text = "\n".join([r.summary.methods or "" for r in reviews]).lower()
    results_text = "\n".join([r.summary.results or "" for r in reviews]).lower()
    
    # Analyze common limitations
    if "data" in limitations_text and ("availability" in limitations_text or "access" in limitations_text):
        gaps.append("Limited data availability and accessibility across studies")
    
    if "baseline" in limitations_text or not any("baseline" in (r.summary.results or "").lower() for r in reviews):
        gaps.append("Insufficient comparison against established baselines")
    
    if "reproducibility" in limitations_text or "reproduce" in limitations_text:
        gaps.append("Lack of reproducibility and code availability")
    
    if "generalization" in limitations_text or "generalize" in limitations_text:
        gaps.append("Limited generalizability across different domains or datasets")
    
    if "evaluation" in limitations_text or "metric" in limitations_text:
        gaps.append("Inconsistent evaluation metrics and methodologies")
    
    # Add default gaps if none found
    if not gaps:
        gaps = [
            "Need for more systematic benchmarking and evaluation",
            "Limited cross-domain validation and generalization studies"
        ]
    
    # Enhanced future work recommendations
    future = []
    
    # Based on venue analysis
    if "arxiv" in [v.lower() for v in venues]:
        future.append("Transition from preprint to peer-reviewed publications")
    
    # Based on year analysis
    if recent_papers < len(papers) * 0.5:
        future.append("Focus on more recent developments and state-of-the-art methods")
    
    # Based on content analysis
    if "machine learning" in methods_text or "deep learning" in methods_text:
        future.append("Integration of more advanced AI/ML techniques")
    
    if "healthcare" in methods_text or "medical" in methods_text:
        future.append("Clinical validation and real-world deployment studies")
    
    # Default future work
    future.extend([
        "Open-sourcing code and datasets for reproducibility",
        "Larger, diverse datasets and multi-institutional studies",
        "Standardized evaluation frameworks and metrics"
    ])
    
    return Synthesis(executive_summary=exec_summary, gaps=gaps, future_work=future)
