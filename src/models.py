from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal, Dict, Any

from pydantic import BaseModel, Field


class Filters(BaseModel):
	start_year: Optional[int] = None
	end_year: Optional[int] = None
	include_keywords: List[str] = Field(default_factory=list)
	exclude_keywords: List[str] = Field(default_factory=list)
	venues: List[str] = Field(default_factory=list)
	limit: int = 20


class Paper(BaseModel):
	id: str
	source: Literal["arxiv", "pubmed", "crossref"]
	title: str
	abstract: Optional[str] = None
	authors: List[str] = Field(default_factory=list)
	year: Optional[int] = None
	venue: Optional[str] = None
	doi: Optional[str] = None
	url: Optional[str] = None
	pdf_url: Optional[str] = None
	citations_count: Optional[int] = None
	keywords: List[str] = Field(default_factory=list)


class Quote(BaseModel):
	text: str
	section: Optional[str] = None


class Summary(BaseModel):
	tldr: str
	methods: Optional[str] = None
	results: Optional[str] = None
	limitations: Optional[str] = None
	citations: Optional[int] = None
	grounding_score: float = 0.0
	quotes: List[Quote] = Field(default_factory=list, max_items=3)


class CritiqueIssue(BaseModel):
	tag: Literal[
		"overclaiming",
		"weak_sample",
		"missing_baselines",
		"reproducibility",
	]
	severity: Literal["low", "medium", "high"]
	rationale: str


class Critique(BaseModel):
	issues: List[CritiqueIssue] = Field(default_factory=list)
	overall_note: Optional[str] = None


class MiniReview(BaseModel):
	paper_id: str
	summary: Summary
	critique: Critique


class ComparativeCell(BaseModel):
	value: str


class ComparativeMatrix(BaseModel):
	columns: List[str]
	rows: List[str]
	data: Dict[str, Dict[str, ComparativeCell]]  # row -> col -> cell


class Synthesis(BaseModel):
	executive_summary: str
	gaps: List[str] = Field(default_factory=list)
	future_work: List[str] = Field(default_factory=list)


class ReviewArtifacts(BaseModel):
	markdown_path: str
	json_path: str
	csv_path: str


class ReviewRequest(BaseModel):
	topic: str
	filters: Filters = Field(default_factory=Filters)
	provider: Literal["openai", "anthropic"] = "openai"


class ReviewResult(BaseModel):
	topic: str
	filters: Filters
	raw_papers: List[Paper]
	reviews: List[MiniReview]
	matrix: ComparativeMatrix
	synthesis: Synthesis
	artifacts: ReviewArtifacts
	created_at: datetime = Field(default_factory=datetime.utcnow)


class ErrorInfo(BaseModel):
	message: str
	details: Optional[Any] = None
