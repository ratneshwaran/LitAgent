from __future__ import annotations

from typing import Tuple

from ..models import Filters, ReviewRequest
from ..config import get_settings
from .build_graph import build_graph


def run_review(topic: str, filters: Filters) -> Tuple[str, str]:
    settings = get_settings()
    graph = build_graph(settings.checkpoint_path)
    state = {"topic": topic, "filters": filters}
    final = graph.invoke(state)
    return final.get("report_md", ""), final.get("report_json", "")
