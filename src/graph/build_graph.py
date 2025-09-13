from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from langgraph.graph import StateGraph, END

try:
	from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore
except Exception:  # pragma: no cover
	SqliteSaver = None  # type: ignore

from ..models import Paper, MiniReview, Summary, ReviewResult, ReviewArtifacts
from ..models import ReviewRequest
from ..agents.search_agent import run_search
from ..agents.summarize_agent import summarize_paper
from ..agents.critic_agent import critique_paper
from ..agents.comparator_agent import build_comparative_matrix, synthesize
from ..utils.text import slugify
from ..utils.logging import get_logger
from ..graph.state import ReviewState
from ..exporters.markdown import export_markdown
from ..exporters.json_export import export_json
from ..exporters.tabular import export_csv

logger = get_logger(__name__)


def search_node(state: ReviewState) -> ReviewState:
	topic = state["topic"]
	filters = state["filters"]
	papers = run_search(topic, filters)
	return {"raw_papers": papers}


def summarize_node(state: ReviewState) -> ReviewState:
	papers: List[Paper] = state["raw_papers"]
	reviews: List[MiniReview] = []
	for p in papers:
		s = summarize_paper(p)
		c = critique_paper(p, s)
		reviews.append(MiniReview(paper_id=p.id, summary=s, critique=c))
	return {"reviews": reviews}


def compare_node(state: ReviewState) -> ReviewState:
	papers: List[Paper] = state["raw_papers"]
	reviews: List[MiniReview] = state["reviews"]
	matrix = build_comparative_matrix(papers, reviews)
	syn = synthesize(papers, reviews)

	slug = slugify(state["topic"]) or "review"
	out_dir = Path("outputs")
	md_path = out_dir / f"review_{slug}.md"
	json_path = out_dir / f"review_{slug}.json"
	csv_path = out_dir / f"papers_{slug}.csv"

	result = ReviewResult(
		topic=state["topic"],
		filters=state["filters"],
		raw_papers=papers,
		reviews=reviews,
		matrix=matrix,
		synthesis=syn,
		artifacts=ReviewArtifacts(
			markdown_path=str(md_path), json_path=str(json_path), csv_path=str(csv_path)
		),
	)

	export_markdown(result, md_path)
	export_json(result, json_path)
	export_csv(papers, csv_path)

	return {"report_md": str(md_path), "report_json": str(json_path)}


def build_graph(checkpoint_path: Optional[str] = None):
	sg = StateGraph(ReviewState)
	sg.add_node("search_node", search_node)
	sg.add_node("summarize_node", summarize_node)
	sg.add_node("compare_node", compare_node)

	sg.set_entry_point("search_node")
	sg.add_edge("search_node", "summarize_node")
	sg.add_edge("summarize_node", "compare_node")
	sg.add_edge("compare_node", END)

	if SqliteSaver:
		Path(".checkpoints").mkdir(parents=True, exist_ok=True)
		memory = SqliteSaver.from_conn_string(checkpoint_path or ".checkpoints/litrev.sqlite")  # type: ignore
		return sg.compile(checkpointer=memory)
	return sg.compile()
