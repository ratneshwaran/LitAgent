from __future__ import annotations

from ..models import Paper, Summary, Critique, CritiqueIssue


def critique_paper(paper: Paper, summary: Summary) -> Critique:
    issues = []
    # Overclaiming: TL;DR with strong language and weak evidence
    tldr = (summary.tldr or "").lower()
    if any(w in tldr for w in ["state-of-the-art", "first", "unprecedented", "revolutionary"]):
        issues.append(
            CritiqueIssue(
                tag="overclaiming",
                severity="medium",
                rationale="Claims strong superiority; check against baselines in paper.",
            )
        )
    # Weak sample: no numbers or small n
    if summary.results and any(x in summary.results.lower() for x in ["n=", "sample size"]):
        import re

        m = re.search(r"n\s*=\s*(\d+)", summary.results.lower())
        if m:
            n = int(m.group(1))
            if n < 30:
                issues.append(
                    CritiqueIssue(
                        tag="weak_sample",
                        severity="high" if n < 15 else "medium",
                        rationale=f"Small sample size n={n} may limit generalization.",
                    )
                )
    # Missing baselines: if not mentioned explicitly
    if not summary.results or "baseline" not in (summary.results.lower()):
        issues.append(
            CritiqueIssue(
                tag="missing_baselines",
                severity="low",
                rationale="Results do not clearly compare against established baselines.",
            )
        )
    # Reproducibility: lack of code/data mentions
    lower = (summary.methods or "") + "\n" + (summary.limitations or "")
    lower = lower.lower()
    if not any(k in lower for k in ["code", "data availability", "reproducible", "open-source"]):
        issues.append(
            CritiqueIssue(
                tag="reproducibility",
                severity="medium",
                rationale="No mention of code/data availability or reproducibility.",
            )
        )
    note = None
    return Critique(issues=issues, overall_note=note)
