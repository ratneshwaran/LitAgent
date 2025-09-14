from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from ..models import Paper


def export_csv(papers: List[Paper], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Concise columns for comparative analysis
        writer.writerow([
            "id", "title", "venue", "year", "methods", "results", "critique_flags", 
            "doi", "url", "citations", "authors"
        ]) 
        for p in papers:
            # Get critique flags
            critique_flags = []
            # Note: This would need access to MiniReview data, but for now we'll keep it simple
            critique_str = "No major issues"  # Placeholder
            
            # Truncate methods and results if they exist
            methods = ""  # Would need MiniReview access
            results = ""  # Would need MiniReview access
            
            writer.writerow([
                p.id, p.title, p.venue or "", p.year or "", methods, results, critique_str,
                p.doi or "", p.url or "", p.citations_count or "", "; ".join(p.authors)
            ])
    return path
