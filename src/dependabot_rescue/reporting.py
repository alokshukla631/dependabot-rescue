"""Rescue report construction and rendering."""

from __future__ import annotations

import json
from dataclasses import asdict

from dependabot_rescue.models import (
    DependencyUpdate,
    FailureSignal,
    PullRequestContext,
    RescueAction,
    RescueReport,
)


def build_report(
    context: PullRequestContext,
    updates: list[DependencyUpdate],
    signals: list[FailureSignal],
) -> RescueReport:
    """Build a rescue report from the extracted evidence."""

    actions = tuple(recommend_actions(signals))
    summary = _build_summary(context, updates, signals)
    notes = _build_notes(context, updates, signals)
    return RescueReport(
        context=context,
        updates=tuple(updates),
        signals=tuple(signals),
        actions=actions,
        summary=summary,
        notes=notes,
    )


def recommend_actions(signals: list[FailureSignal]) -> list[RescueAction]:
    """Map failure signals to recommended maintainer actions."""

    if not signals:
        return [
            RescueAction(
                title="Inspect raw CI logs",
                rationale="No failure signal was detected, so the next step is a manual review of the failing job output.",
            )
        ]

    actions: list[RescueAction] = []
    seen_categories: set[str] = set()
    seen_titles: set[str] = set()
    for signal in signals:
        if signal.category in seen_categories:
            continue
        seen_categories.add(signal.category)
        action = _action_for_signal(signal)
        if action.title in seen_titles:
            continue
        seen_titles.add(action.title)
        actions.append(action)
    return actions


def report_to_markdown(report: RescueReport) -> str:
    """Render the rescue report as Markdown."""

    lines = [
        "# Rescue Report",
        "",
        f"**Summary:** {report.summary}",
        "",
        "## Pull Request",
        "",
        f"- Title: {report.context.title or '(missing)'}",
        f"- Tool: {report.context.tool}",
        f"- Author: {report.context.author or '(unknown)'}",
        f"- Branch: {report.context.branch or '(unknown)'}",
    ]

    if report.updates:
        lines.extend(["", "## Dependency Updates", ""])
        for update in report.updates:
            version_part = f"{update.from_version} -> {update.to_version}" if update.from_version else update.to_version
            details = [f"- `{update.package}` {version_part}"]
            if update.ecosystem:
                details.append(f"(ecosystem: {update.ecosystem})")
            lines.append(" ".join(details))
    else:
        lines.extend(["", "## Dependency Updates", "", "- No dependency updates were extracted from PR metadata."])

    lines.extend(["", "## Failure Signals", ""])
    for signal in report.signals:
        related = f" Related package: `{signal.related_package}`." if signal.related_package else ""
        lines.append(
            f"- `{signal.category}` ({signal.confidence:.2f}): {signal.summary}{related}"
        )
        for evidence in signal.evidence:
            lines.append(f"  - Evidence: `{evidence}`")

    lines.extend(["", "## Recommended Next Steps", ""])
    for action in report.actions:
        lines.append(f"- **{action.title}:** {action.rationale}")

    if report.notes:
        lines.extend(["", "## Notes", ""])
        for note in report.notes:
            lines.append(f"- {note}")

    return "\n".join(lines)


def report_to_json(report: RescueReport) -> str:
    """Render the rescue report as formatted JSON."""

    return json.dumps(asdict(report), indent=2)


def _build_summary(
    context: PullRequestContext,
    updates: list[DependencyUpdate],
    signals: list[FailureSignal],
) -> str:
    if updates and signals and signals[0].category != "unknown":
        lead_update = updates[0]
        lead_signal = signals[0]
        return (
            f"{context.tool.capitalize()} PR likely broke after updating `{lead_update.package}` "
            f"to `{lead_update.to_version}`; strongest signal: `{lead_signal.category}`."
        )
    if updates:
        return f"Detected {len(updates)} dependency update(s), but no strong failure signal yet."
    return "Could not confidently extract dependency updates from the PR metadata."


def _build_notes(
    context: PullRequestContext,
    updates: list[DependencyUpdate],
    signals: list[FailureSignal],
) -> tuple[str, ...]:
    notes: list[str] = []
    if context.tool == "unknown":
        notes.append("The PR source tool could not be inferred confidently.")
    if not updates:
        notes.append("Consider passing the full PR body or a richer event payload for better extraction.")
    if signals and signals[0].category == "unknown":
        notes.append("Add more complete CI logs to improve failure classification.")
    return tuple(notes)


def _action_for_signal(signal: FailureSignal) -> RescueAction:
    if signal.category == "dependency_conflict":
        return RescueAction(
            title="Refresh dependency constraints",
            rationale="Re-resolve the dependency graph, inspect peer or version constraints, and check whether the updated package requires companion upgrades.",
        )
    if signal.category == "lockfile_drift":
        return RescueAction(
            title="Regenerate the lockfile",
            rationale="The manifest update and lockfile output disagree, so the next step is to run the package manager lockfile refresh in CI or locally.",
        )
    if signal.category in {"import_error", "removed_api", "compile_failure"}:
        return RescueAction(
            title="Review the migration surface",
            rationale="Search for imports or APIs from the updated package and compare them with the new version's release notes or migration guide.",
        )
    if signal.category == "runtime_mismatch":
        return RescueAction(
            title="Align runtime versions",
            rationale="Check CI and local runtime versions against the updated dependency's supported Python or Node range.",
        )
    if signal.category == "test_failure":
        return RescueAction(
            title="Inspect behavioral assertions",
            rationale="The package likely changed behavior without breaking imports, so compare test expectations with the new dependency behavior before pinning or patching.",
        )
    return RescueAction(
        title="Inspect raw CI evidence",
        rationale="The failure does not match a known category yet, so the next step is a targeted manual review of the failing job logs.",
    )
