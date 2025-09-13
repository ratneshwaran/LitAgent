import typer
from typing import Optional

from ..models import Filters
from ..graph.run_graph import run_review

app = typer.Typer(help="Literature Review Agent CLI")


@app.command()
def run(
    topic: str = typer.Argument(..., help="Topic to review"),
    start_year: Optional[int] = typer.Option(None, help="Start year"),
    end_year: Optional[int] = typer.Option(None, help="End year"),
    include: Optional[str] = typer.Option(None, help="Comma-separated include keywords"),
    exclude: Optional[str] = typer.Option(None, help="Comma-separated exclude keywords"),
    venues: Optional[str] = typer.Option(None, help="Comma-separated venues"),
    limit: int = typer.Option(20, help="Max number of papers"),
    provider: str = typer.Option("openai", help="LLM provider: openai or anthropic"),
):
    filters = Filters(
        start_year=start_year,
        end_year=end_year,
        include_keywords=[s.strip() for s in (include.split(",") if include else []) if s.strip()],
        exclude_keywords=[s.strip() for s in (exclude.split(",") if exclude else []) if s.strip()],
        venues=[s.strip() for s in (venues.split(",") if venues else []) if s.strip()],
        limit=limit,
    )
    md_path, json_path = run_review(topic, filters)
    typer.echo(f"Markdown: {md_path}")
    typer.echo(f"JSON: {json_path}")


def main():
    app()


if __name__ == "__main__":
    main()
