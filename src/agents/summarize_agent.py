from __future__ import annotations

from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..models import Paper, Summary, Quote
from ..config import get_settings


PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an expert scientific summarizer. Extract TL;DR, methods, results, limitations, citations. Include up to 3 short grounded quotes from the abstract or main text if available. Respond in strict JSON with keys: tldr, methods, results, limitations, citations, grounding_score, quotes=[{text, section}]."),
    ("human", "Paper Title: {title}\nAbstract: {abstract}\nIf you cannot find specific details, be concise and conservative.")
])


def _get_llm():
    s = get_settings()
    if s.llm_provider == "anthropic":
        return ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
    else:
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _heuristic_summary(paper: Paper) -> Summary:
    abstract = (paper.abstract or "").strip()
    tldr = abstract[:280] + ("..." if len(abstract) > 280 else "")
    quotes: List[Quote] = []
    if abstract:
        snippet = abstract.split(".")[:2]
        q = ". ".join(s.strip() for s in snippet if s.strip())
        if q:
            quotes.append(Quote(text=q[:200], section="abstract"))
    return Summary(
        tldr=tldr or paper.title,
        methods=None,
        results=None,
        limitations=None,
        citations=None,
        grounding_score=0.2 if quotes else 0.0,
        quotes=quotes[:3],
    )


def summarize_paper(paper: Paper) -> Summary:
    abstract = paper.abstract or ""
    if not abstract:
        return _heuristic_summary(paper)
    llm = _get_llm()
    chain = PROMPT | llm
    try:
        msg = chain.invoke({"title": paper.title, "abstract": abstract})
        content = msg.content if hasattr(msg, "content") else str(msg)
        import json

        data = json.loads(content)
        quotes = [Quote(**q) for q in (data.get("quotes") or [])][:3]
        return Summary(
            tldr=data.get("tldr", ""),
            methods=data.get("methods"),
            results=data.get("results"),
            limitations=data.get("limitations"),
            citations=data.get("citations"),
            grounding_score=float(data.get("grounding_score", 0.0)),
            quotes=quotes,
        )
    except Exception:
        return _heuristic_summary(paper)
