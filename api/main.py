from __future__ import annotations

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Literal, Optional
from uuid import uuid4
from pathlib import Path
from datetime import datetime

from src.models import Filters, SearchFilters
from src.graph.run_graph import run_review
from src.search.semantic_search import semantic_search, hybrid_search
from src.agents.search_agent import run_search


class JobStatus(BaseModel):
	status: Literal["running", "done", "failed"]
	message: Optional[str] = None


class Job(BaseModel):
	job_id: str
	topic: str
	created_at: datetime
	filters: Filters
	status: Literal["running", "done", "failed"] = "running"
	markdown_path: Optional[str] = None
	json_path: Optional[str] = None
	csv_path: Optional[str] = None
	message: Optional[str] = None


class RunPayload(BaseModel):
	topic: str
	start_year: int | None = None
	end_year: int | None = None
	include: str | None = None
	exclude: str | None = None
	venues: str | None = None
	limit: int = 20
	provider: Literal["openai", "anthropic"] | None = None
	# New advanced options
	must_have_pdf: bool = False
	oa_only: bool = False
	review_filter: Literal["off", "soft", "hard"] = "off"
	enabled_sources: str | None = None  # Comma-separated list


app = FastAPI(title="Literature Review Agent API")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

_JOBS: Dict[str, Job] = {}


def _to_filters(p: RunPayload) -> Filters:
	# Parse enabled sources
	enabled_sources = []
	if p.enabled_sources:
		enabled_sources = [s.strip() for s in p.enabled_sources.split(",") if s.strip()]
	
	return Filters(
		start_year=p.start_year,
		end_year=p.end_year,
		include_keywords=[s.strip() for s in (p.include.split(",") if p.include else []) if s.strip()],
		exclude_keywords=[s.strip() for s in (p.exclude.split(",") if p.exclude else []) if s.strip()],
		venues=[s.strip() for s in (p.venues.split(",") if p.venues else []) if s.strip()],
		limit=p.limit,
	)


async def _execute_job(job_id: str) -> None:
	job = _JOBS.get(job_id)
	if not job:
		return
	try:
		md, js = run_review(job.topic, job.filters)
		csv = str(Path(js).with_name(Path(js).name.replace("review_", "papers_").replace(".json", ".csv")))
		# Update
		job.status = "done"
		job.markdown_path = md
		job.json_path = js
		job.csv_path = csv
	except Exception as e:  # pragma: no cover - runtime safeguard
		job.status = "failed"
		job.message = str(e)


@app.post("/run", response_model=Job)
async def run(payload: RunPayload, bg: BackgroundTasks):
	filters = _to_filters(payload)
	job_id = str(uuid4())
	job = Job(job_id=job_id, topic=payload.topic, created_at=datetime.utcnow(), filters=filters)
	_JOBS[job_id] = job
	bg.add_task(_execute_job, job_id)
	return job


@app.get("/result/{job_id}", response_model=Job)
async def result(job_id: str):
	job = _JOBS.get(job_id)
	if not job:
		raise HTTPException(status_code=404, detail="Job not found")
	return job


@app.get("/jobs", response_model=List[Job])
async def jobs():
	# Most recent first
	return sorted(_JOBS.values(), key=lambda j: j.created_at, reverse=True)


@app.get("/download/{job_id}/{kind}")
async def download(job_id: str, kind: Literal["md", "json", "csv"]):
	job = _JOBS.get(job_id)
	if not job:
		raise HTTPException(status_code=404, detail="Job not found")
	path = None
	if kind == "md":
		path = job.markdown_path
	elif kind == "json":
		path = job.json_path
	else:
		path = job.csv_path
	if not path or not Path(path).exists():
		raise HTTPException(status_code=404, detail="File not available")
	return FileResponse(path, filename=Path(path).name)


@app.get("/api/search")
async def search_papers(
	q: str,
	description: Optional[str] = None,
	mode: Literal["title", "semantic", "hybrid"] = "title",
	k: int = 20,
	start_year: Optional[int] = None,
	end_year: Optional[int] = None,
	include_keywords: Optional[str] = None,
	exclude_keywords: Optional[str] = None,
	venues: Optional[str] = None,
	must_have_pdf: bool = False,
	oa_only: bool = False,
	review_filter: Literal["off", "soft", "hard"] = "off"
):
	"""Search for papers using different modes"""
	if not q or len(q.strip()) < 3:
		raise HTTPException(status_code=400, detail="Query must be at least 3 characters long")
	
	# Parse filters
	search_filters = SearchFilters(
		start_year=start_year,
		end_year=end_year,
		include_keywords=[s.strip() for s in (include_keywords.split(",") if include_keywords else []) if s.strip()],
		exclude_keywords=[s.strip() for s in (exclude_keywords.split(",") if exclude_keywords else []) if s.strip()],
		venues=[s.strip() for s in (venues.split(",") if venues else []) if s.strip()],
		limit=k,
		must_have_pdf=must_have_pdf,
		oa_only=oa_only,
		review_filter=review_filter
	)
	
	try:
		if mode == "title":
			# Use existing title-based search
			legacy_filters = Filters(
				start_year=start_year,
				end_year=end_year,
				include_keywords=search_filters.include_keywords,
				exclude_keywords=search_filters.exclude_keywords,
				venues=search_filters.venues,
				limit=k
			)
			papers = run_search(q, legacy_filters)
		elif mode == "semantic":
			papers = semantic_search(q, search_filters, k=k)
		elif mode == "hybrid":
			description_query = description or ""
			papers = hybrid_search(q, description_query, search_filters, k=k)
		else:
			raise HTTPException(status_code=400, detail="Invalid search mode")
		
		# Convert papers to response format
		results = []
		for paper in papers:
			result = {
				"id": paper.id,
				"title": paper.title,
				"abstract": paper.abstract,
				"authors": paper.authors,
				"year": paper.year,
				"venue": paper.venue,
				"doi": paper.doi,
				"url": paper.url,
				"pdf_url": paper.pdf_url,
				"citations_count": paper.citations_count,
				"source": paper.source,
				"relevance_score": paper.score_components.final if paper.score_components else 0.0,
				"reasons": paper.reasons
			}
			results.append(result)
		
		return {
			"query": q,
			"mode": mode,
			"total_results": len(results),
			"papers": results
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
