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
from src.agents.search_agent_v2 import run_search_v2


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


class QARequest(BaseModel):
	question: str
	paper_ids: List[str]
	mode: Literal["concise", "detailed"] = "concise"


class QAAnswer(BaseModel):
	answer: str
	citations: List[Dict[str, str]]


class RelatedRequest(BaseModel):
    paper_id: Optional[str] = None
    query: Optional[str] = None
    k: int = 10


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
    k: int = 50,
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

	# Auto-derive include keywords from NL query if none provided
	if not search_filters.include_keywords:
		# Extract quoted phrases first
		import re
		q_lower = q.lower()
		quoted = re.findall(r'"([^"]+)"', q_lower)
		# Extract salient tokens (>=4 chars, not stopwords)
		stop = {
			"the","and","that","with","from","using","about","into","their","within",
			"study","studies","papers","paper","research","for","on","in","of","to",
			"this","those","these","please","find","show","give","need","want","me",
		}
		words = [w for w in re.split(r"[^a-zA-Z0-9]+", q_lower) if len(w) >= 4 and w not in stop]
		# Add common bigrams of interest (e.g., cell annotation)
		tokens = [t for t in re.split(r"[^a-zA-Z0-9]+", q_lower) if t]
		bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)]
		phrases = []
		for bg in bigrams:
			if any(k in bg for k in ["cell annotation","case control","meta analysis","zero shot","few shot"]):
				phrases.append(bg)
		candidates = list(dict.fromkeys([*quoted, *phrases, *words]))[:6]
		# Normalize zero-shot variants
		norm = []
		for c in candidates:
			if c.replace(" ", "") == "zeroshot" or c == "zero-shot" or c == "zero shot":
				norm.extend(["zero-shot","zero shot","zeroshot"])
			else:
				norm.append(c)
		if norm:
			search_filters.include_keywords = list(dict.fromkeys(norm))
	
	try:
		if mode == "title":
			# Use V2 multi-source pipeline for better recall and ranking
			papers, _diagnostics = run_search_v2(q, search_filters)
			if not papers:
				# Fallback to legacy title-based search if V2 returns empty
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
				"relevance_score": (paper.score_components.final if paper.score_components else 0.0),
				"reasons": paper.reasons
			}
			results.append(result)
		
		# Ensure results are already ranked by backend; do not resort here
		return {
			"query": q,
			"mode": mode,
			"total_results": len(results),
			"papers": results
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/api/qa", response_model=QAAnswer)
async def qa(payload: QARequest):
	"""Heuristic QA over current papers (no external LLM required)."""
	if not payload.paper_ids or not payload.question.strip():
		raise HTTPException(status_code=400, detail="paper_ids and question are required")

	# For simplicity, re-use title search to fetch paper metadata quickly
	filters = Filters(limit=200)
	papers = run_search(" ".join(payload.paper_ids), filters)
	# Build small, focused synthesis
	q_lower = payload.question.lower()
	selected = []
	for p in papers:
		blob = f"{p.title} {p.abstract or ''} {p.venue or ''}"
		if any(tok in blob.lower() for tok in q_lower.split()[:6]):
			selected.append(p)
			if len(selected) >= 15:
				break

	if not selected:
		return QAAnswer(answer="No direct matches found in current results.", citations=[])

	# Extract simple signals
	methods = []
	findings = []
	citations = []
	for p in selected:
		text = (p.abstract or "")
		if any(k in text.lower() for k in ["randomized", "rct", "survey", "meta-analysis", "cohort", "case-control", "qualitative", "experiment"]):
			methods.append(f"- {p.title}: {p.venue or ''} {p.year or ''}")
		if any(k in text.lower() for k in ["improv", "increase", "decrease", "significant", "association", "effect"]):
			findings.append(f"- {p.title} ({p.year or ''})")
		citations.append({"id": p.id, "title": p.title, "url": p.url or (p.doi and f"https://doi.org/{p.doi}") or ""})

	sections = []
	if methods:
		sections.append("Methods observed:\n" + "\n".join(methods))
	if findings:
		sections.append("Key findings:\n" + "\n".join(findings))
	if not sections:
		sections.append("Synthesized summary based on abstracts. No specific methods/findings keywords detected.")

	answer = "\n\n".join(sections)
	if payload.mode == "detailed":
		answer += "\n\nCaveats: heuristic QA without external LLM; refine your question or apply filters for sharper answers."

	return QAAnswer(answer=answer, citations=citations[:20])


@app.post("/api/related")
async def related(payload: RelatedRequest):
    """Return related papers using either an explicit query or by resolving a paper_id.

    - If `query` is provided, we use it directly (prefer title + abstract from the client).
    - Else, if `paper_id` is provided, we try to resolve metadata from the embedding store
      to build a query from title + abstract. If that fails, we fall back to using the id
      text itself as a query (legacy behavior).
    """
    if not payload.paper_id and not payload.query:
        raise HTTPException(status_code=400, detail="query or paper_id is required")

    # Determine query text
    q_text: Optional[str] = None
    if payload.query and payload.query.strip():
        q_text = payload.query.strip()
    elif payload.paper_id:
        # Try resolving from embedding store for richer context
        try:
            from src.search.embedding_store import get_embedding_store
            store = get_embedding_store()
            rec = store.get_paper_by_id(payload.paper_id)
            if rec:
                # rec has title and abstract attributes
                q_text = f"{rec.title} {getattr(rec, 'abstract', '') or ''}".strip()
        except Exception:
            # Best-effort only; ignore resolution errors
            pass

    if not q_text:
        # Fallback legacy: use the id string
        q_text = str(payload.paper_id or "").strip()

    # Build filters and execute search
    search_k = max(5, min(50, payload.k))
    search_filters = SearchFilters(limit=search_k)
    try:
        papers, _diag = run_search_v2(q_text, search_filters)
        if not papers:
            papers = run_search(q_text, Filters(limit=search_k))
    except Exception:
        papers = run_search(q_text, Filters(limit=search_k))

    # Map and exclude the original paper if present
    mapped = []
    for p in papers:
        if payload.paper_id and p.id == payload.paper_id:
            continue
        mapped.append({
            "id": p.id,
            "title": p.title,
            "year": p.year,
            "venue": p.venue,
            "url": p.url,
            "doi": p.doi
        })

    # Build lightweight insights from titles/abstracts
    try:
        blob_parts: List[str] = [q_text]
        for p in papers:
            blob_parts.append(p.title or "")
            if p.abstract:
                blob_parts.append(p.abstract)
        blob = " \n ".join([b for b in blob_parts if b])
        blob_lower = blob.lower()

        # Themes
        themes: List[str] = []
        def add_theme(flag: bool, label: str) -> None:
            if flag and label not in themes:
                themes.append(label)
        add_theme("zero-shot" in blob_lower or "zeroshot" in blob_lower, "Zero-shot methods")
        add_theme("few-shot" in blob_lower or "fewshot" in blob_lower, "Few-shot/low-data learning")
        add_theme("meta-analysis" in blob_lower, "Meta-analyses")
        add_theme("benchmark" in blob_lower or "dataset" in blob_lower, "Benchmarking and datasets")
        add_theme("clinical" in blob_lower or "patient" in blob_lower, "Clinical applications")
        add_theme("transfer" in blob_lower or "generalization" in blob_lower, "Transfer/generalization")

        # Gaps
        gaps: List[str] = []
        if "replication" not in blob_lower and "reproduc" not in blob_lower:
            gaps.append("Limited replication/reproducibility evidence")
        if "code" not in blob_lower:
            gaps.append("Few papers advertise code availability")
        if "data" not in blob_lower and "dataset" not in blob_lower:
            gaps.append("Data availability not consistently discussed")
        if "real-world" not in blob_lower and "clinical" not in blob_lower and "deployment" not in blob_lower:
            gaps.append("Limited real-world validation")

        # Future work suggestions
        future_work: List[str] = []
        if any(t in themes for t in ["Benchmarking and datasets"]):
            future_work.append("Create stronger, standardized benchmarks and datasets")
        if any(t in themes for t in ["Transfer/generalization"]):
            future_work.append("Evaluate generalization across domains and distributions")
        future_work.append("Improve transparency: share code, data, and evaluation scripts")
        future_work.append("Conduct preregistered or larger, well-powered studies")

        # Short summary
        total = len(mapped)
        span_years = [p.year for p in papers if p.year]
        span = f"{min(span_years)}–{max(span_years)}" if span_years else "unspecified years"
        summary = (
            f"Found {total} related works ({span}). Prominent themes: "
            + ", ".join(themes[:4]) + ". "
            + ("Common gaps: " + ", ".join(gaps[:3]) + "." if gaps else "")
        )

        insights = {
            "themes": themes,
            "gaps": gaps,
            "future_work": future_work,
            "summary": summary,
        }
    except Exception:
        insights = {"themes": [], "gaps": [], "future_work": [], "summary": ""}

    return {"related": mapped[:search_k], "insights": insights}
