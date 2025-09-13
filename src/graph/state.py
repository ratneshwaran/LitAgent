from __future__ import annotations

from typing import TypedDict, List, Optional

from ..models import Paper, MiniReview, Filters, ComparativeMatrix, Synthesis


class ReviewState(TypedDict, total=False):
	topic: str
	filters: Filters
	raw_papers: List[Paper]
	reviews: List[MiniReview]
	matrix: ComparativeMatrix
	report_md: Optional[str]
	report_json: Optional[str]
	errors: List[str]
