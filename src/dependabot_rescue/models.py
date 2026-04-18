"""Domain models for dependabot-rescue."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PullRequestContext:
    """Normalized pull request data used by the analysis pipeline."""

    title: str
    body: str = ""
    author: str = ""
    branch: str = ""
    base_branch: str = ""
    number: int | None = None
    tool: str = "unknown"
    labels: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DependencyUpdate:
    """A dependency version change inferred from PR metadata."""

    package: str
    to_version: str
    from_version: str | None = None
    ecosystem: str | None = None
    manifest_path: str | None = None
    confidence: float = 0.0
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FailureSignal:
    """A single CI failure signal inferred from logs."""

    category: str
    summary: str
    confidence: float
    evidence: tuple[str, ...] = ()
    related_package: str | None = None


@dataclass(frozen=True, slots=True)
class RescueAction:
    """A recommended next step for the maintainer."""

    title: str
    rationale: str


@dataclass(frozen=True, slots=True)
class RescueReport:
    """The final analysis report."""

    context: PullRequestContext
    updates: tuple[DependencyUpdate, ...] = ()
    signals: tuple[FailureSignal, ...] = ()
    actions: tuple[RescueAction, ...] = ()
    summary: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)
