from __future__ import annotations

from ..models import Paper, Summary, Critique, CritiqueIssue


def critique_paper(paper: Paper, summary: Summary) -> Critique:
    issues = []
    # Overclaiming: check for strong claims without sufficient evidence
    claim_text = (summary.tldr or "") + "\n" + (paper.abstract or "")
    claim_lower = claim_text.lower()
    
    # Strong claim words
    strong_claims = ["state-of-the-art", "first", "unprecedented", "revolutionary", 
                     "breakthrough", "novel", "groundbreaking", "superior", "best"]
    
    # Evidence indicators
    evidence_indicators = ["compared to", "baseline", "benchmark", "evaluation", 
                          "experiment", "results show", "performance", "accuracy"]
    
    has_strong_claims = any(claim in claim_lower for claim in strong_claims)
    has_evidence = any(evidence in claim_lower for evidence in evidence_indicators)
    
    # Flag overclaiming if strong claims are made but evidence is weak
    if has_strong_claims and not has_evidence:
        issues.append(
            CritiqueIssue(
                tag="overclaiming",
                severity="medium",
                rationale="Makes strong claims but lacks clear experimental evidence or comparisons.",
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
    # Missing baselines: check for comparison indicators
    # Check summary fields and paper content for baseline/comparison mentions
    baseline_text = (summary.results or "") + "\n" + (summary.methods or "") + "\n" + (paper.abstract or "")
    baseline_lower = baseline_text.lower()
    
    baseline_indicators = [
        "baseline", "baselines", "compared to", "comparison", "benchmark",
        "state-of-the-art", "sota", "previous work", "existing methods",
        "prior work", "literature", "related work", "evaluation against",
        "performance compared", "improvement over", "better than"
    ]
    
    has_baselines = any(indicator in baseline_lower for indicator in baseline_indicators)
    
    if not has_baselines:
        issues.append(
            CritiqueIssue(
                tag="missing_baselines",
                severity="low",
                rationale="No clear comparison against established baselines or previous work found.",
            )
        )
    # Reproducibility: check for code/data availability indicators
    # Check summary fields first
    summary_text = (summary.methods or "") + "\n" + (summary.limitations or "") + "\n" + (summary.results or "")
    summary_lower = summary_text.lower()
    
    # Check paper content for reproducibility indicators
    paper_text = (paper.abstract or "") + "\n" + (paper.title or "")
    paper_lower = paper_text.lower()
    
    # Look for positive reproducibility indicators
    reproducibility_indicators = [
        "github", "gitlab", "bitbucket", "code repository", "source code",
        "data availability", "reproducible", "open-source", "open source",
        "code available", "implementation available", "supplementary code",
        "replication package", "data and code", "materials available",
        "https://github.com", "https://gitlab.com", "https://bitbucket.org",
        "zenodo", "figshare", "osf.io", "open data", "publicly available"
    ]
    
    has_reproducibility = any(indicator in summary_lower or indicator in paper_lower 
                             for indicator in reproducibility_indicators)
    
    if not has_reproducibility:
        issues.append(
            CritiqueIssue(
                tag="reproducibility",
                severity="medium",
                rationale="No mention of code/data availability or reproducibility indicators found.",
            )
        )
    else:
        # Add positive flag for good reproducibility
        issues.append(
            CritiqueIssue(
                tag="good_reproducibility",
                severity="positive",
                rationale="Code/data availability mentioned - good reproducibility practices.",
            )
        )
    note = None
    return Critique(issues=issues, overall_note=note)
