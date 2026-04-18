"""Input loading and pull request context normalization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dependabot_rescue.models import PullRequestContext


def load_event_payload(path: str | Path) -> dict[str, Any]:
    """Load a GitHub event JSON payload from disk."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def context_from_event_payload(payload: dict[str, Any]) -> PullRequestContext:
    """Build a normalized PR context from a GitHub event payload."""

    pr = payload.get("pull_request", payload)
    title = str(pr.get("title", "")).strip()
    body = str(pr.get("body", "")).strip()
    author = str(pr.get("user", {}).get("login", "")).strip()
    head = pr.get("head", {}) or {}
    base = pr.get("base", {}) or {}
    branch = str(head.get("ref", payload.get("ref", ""))).strip()
    base_branch = str(base.get("ref", "")).strip()
    labels = tuple(
        str(label.get("name", "")).strip()
        for label in pr.get("labels", [])
        if str(label.get("name", "")).strip()
    )

    return PullRequestContext(
        title=title,
        body=body,
        author=author,
        branch=branch,
        base_branch=base_branch,
        number=pr.get("number"),
        tool=infer_update_tool(author=author, branch=branch, title=title),
        labels=labels,
    )


def context_from_manual_fields(
    *,
    title: str,
    body: str = "",
    author: str = "",
    branch: str = "",
    base_branch: str = "",
    tool: str | None = None,
) -> PullRequestContext:
    """Build a normalized PR context from direct CLI inputs."""

    return PullRequestContext(
        title=title.strip(),
        body=body.strip(),
        author=author.strip(),
        branch=branch.strip(),
        base_branch=base_branch.strip(),
        tool=(tool or infer_update_tool(author=author, branch=branch, title=title)).strip() or "unknown",
    )


def infer_update_tool(author: str, branch: str, title: str) -> str:
    """Infer whether the PR came from Dependabot, Renovate, or neither."""

    author_lower = author.lower()
    branch_lower = branch.lower()
    title_lower = title.lower()

    if "dependabot" in author_lower or branch_lower.startswith("dependabot/"):
        return "dependabot"
    if "renovate" in author_lower or branch_lower.startswith("renovate/"):
        return "renovate"
    if title_lower.startswith("bump "):
        return "dependabot"
    if "update dependency" in title_lower or "lock file maintenance" in title_lower:
        return "renovate"
    return "unknown"
