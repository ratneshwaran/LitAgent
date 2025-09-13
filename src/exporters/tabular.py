from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from ..models import Paper


def export_csv(papers: List[Paper], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "source", "title", "year", "venue", "doi", "url", "pdf_url", "citations", "authors"]) 
        for p in papers:
            writer.writerow([
                p.id, p.source, p.title, p.year or "", p.venue or "", p.doi or "", p.url or "", p.pdf_url or "", p.citations_count or "", "; ".join(p.authors)
            ])
    return path
