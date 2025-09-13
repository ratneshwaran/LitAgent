# Literature Review Agent

LangGraph-powered multi-agent system for automated literature reviews across arXiv and PubMed, with Crossref enrichment. Generates a structured Markdown report, JSON export, and CSV table.

## Features
- SearchAgent: query arXiv + PubMed; Crossref enrich/fallback
- SummarizerAgent: TL;DR, methods, results, limitations, citations; ≤3 grounding quotes with grounding_score
- CriticAgent: flags overclaiming vs abstract, weak samples, missing baselines, reproducibility issues
- ComparatorAgent: comparative matrix, synthesis, gaps, future work
- Orchestrated via LangGraph with SqliteSaver checkpoints
- CLI (Typer) and REST API (FastAPI)
- Frontend (React + Vite + Tailwind) to run and view reviews

## Installation
```bash
uv pip install -e .[dev]
cp .env.example .env
```

## CLI Usage
```bash
uv run litrev run "foundation models for single-cell annotation" \
  --start-year 2020 --end-year 2025 --include "zero-shot" --limit 25 \
  --venues "Nature,Bioinformatics,Cell" --provider openai
```

## API Usage
- Start: `uvicorn literature-review-agent.api.main:app --reload`
- POST `/run` with JSON payload
- GET `/result/{job_id}` for JSON/Markdown
- GET `/jobs` for job list
- GET `/download/{job_id}/{kind}` for md/json/csv

## Frontend
```bash
cd frontend
npm install
npm run dev
# open http://localhost:5173 (ensure API at http://localhost:8000)
```
You can set `VITE_BACKEND_URL` in a `.env` file inside `frontend/` if your API runs elsewhere.

## Outputs
- `outputs/review_<slug>.md` – Markdown report
- `outputs/review_<slug>.json` – Structured JSON
- `outputs/papers_<slug>.csv` – Tabular data

## Development
- Python 3.11+
- Run tests: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run black .`
- Type-check: `uv run mypy .`

## License
MIT
