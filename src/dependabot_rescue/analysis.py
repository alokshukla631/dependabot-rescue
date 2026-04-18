"""High-level orchestration for dependency update rescue analysis."""

from __future__ import annotations

from dependabot_rescue.logs import classify_logs
from dependabot_rescue.models import PullRequestContext, RescueReport
from dependabot_rescue.reporting import build_report
from dependabot_rescue.updates import extract_updates


def analyze_pull_request(context: PullRequestContext, log_texts: list[str]) -> RescueReport:
    """Run the full analysis pipeline for a pull request."""

    updates = extract_updates(context)
    signals = classify_logs(log_texts, updates)
    return build_report(context=context, updates=updates, signals=signals)
