from __future__ import annotations

import json
from pathlib import Path

from ..models import ReviewResult


def export_json(result: ReviewResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = result.model_dump(mode="json")
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path
