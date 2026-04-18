"""Dependency update extraction from normalized PR metadata."""

from __future__ import annotations

import re

from dependabot_rescue.models import DependencyUpdate, PullRequestContext

_DEPENDABOT_TITLE_PATTERNS = (
    re.compile(
        r"^Bump (?P<package>.+?) from (?P<from_version>\S+) to (?P<to_version>\S+)"
        r"(?: in (?P<manifest_path>\S+))?$",
        re.IGNORECASE,
    ),
)

_RENOVATE_TITLE_PATTERNS = (
    re.compile(
        r"^(?:chore|fix|build|ci)?(?:\(.+?\))?:?\s*update dependency "
        r"(?P<package>.+?) to (?P<to_version>v?\S+)$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(?:chore|fix|build|ci)?(?:\(.+?\))?:?\s*update (?P<package>.+?) to "
        r"(?P<to_version>v?\S+)$",
        re.IGNORECASE,
    ),
)

_BODY_BULLET_PATTERN = re.compile(
    r"[-*]\s+`?(?P<package>[@/\w.\-]+)`?\s+(?P<from_version>[0-9A-Za-z_.\-]+)\s*->\s*"
    r"`?(?P<to_version>[0-9A-Za-z_.\-]+)`?",
    re.IGNORECASE,
)

_ECOSYSTEM_BY_BRANCH = {
    "npm_and_yarn": "npm",
    "npm": "npm",
    "pip": "pip",
    "github_actions": "github-actions",
    "docker": "docker",
    "maven": "maven",
    "gradle": "gradle",
    "bundler": "bundler",
    "gomod": "gomod",
}


def extract_updates(context: PullRequestContext) -> list[DependencyUpdate]:
    """Extract dependency update candidates from a pull request context."""

    candidates: list[DependencyUpdate] = []
    candidates.extend(_extract_from_title(context))
    candidates.extend(_extract_from_body(context))
    candidates.extend(_extract_from_branch(context))
    return _dedupe_updates(candidates)


def _extract_from_title(context: PullRequestContext) -> list[DependencyUpdate]:
    patterns = (
        _DEPENDABOT_TITLE_PATTERNS
        if context.tool == "dependabot"
        else _RENOVATE_TITLE_PATTERNS
    )
    matches: list[DependencyUpdate] = []
    for pattern in patterns:
        matched = pattern.match(context.title)
        if not matched:
            continue

        groups = matched.groupdict()
        matches.append(
            DependencyUpdate(
                package=groups["package"].strip(),
                from_version=_clean_version(groups.get("from_version")),
                to_version=_clean_version(groups["to_version"]),
                ecosystem=_extract_ecosystem_from_branch(context.branch),
                manifest_path=groups.get("manifest_path"),
                confidence=0.95,
                evidence=(context.title,),
            )
        )
    return matches


def _extract_from_body(context: PullRequestContext) -> list[DependencyUpdate]:
    matches: list[DependencyUpdate] = []
    for body_match in _BODY_BULLET_PATTERN.finditer(context.body):
        groups = body_match.groupdict()
        matches.append(
            DependencyUpdate(
                package=groups["package"].strip(),
                from_version=_clean_version(groups["from_version"]),
                to_version=_clean_version(groups["to_version"]),
                ecosystem=_extract_ecosystem_from_branch(context.branch),
                confidence=0.7,
                evidence=(body_match.group(0),),
            )
        )
    return matches


def _extract_from_branch(context: PullRequestContext) -> list[DependencyUpdate]:
    branch = context.branch.strip("/")
    if not branch:
        return []

    segments = branch.split("/")
    tool = segments[0].lower()
    if tool not in {"dependabot", "renovate"}:
        return []

    if tool == "dependabot" and len(segments) >= 3:
        ecosystem = _ECOSYSTEM_BY_BRANCH.get(segments[1].lower())
        package_segment = segments[-1]
        package, version = _split_package_and_version(package_segment)
        if package and version:
            return [
                DependencyUpdate(
                    package=package,
                    to_version=version,
                    ecosystem=ecosystem,
                    confidence=0.55,
                    evidence=(context.branch,),
                )
            ]

    if tool == "renovate":
        match = re.search(
            r"(?P<package>[@/\w.\-]+)-(?P<to_version>\d[\w.\-]*)$",
            segments[-1],
            re.IGNORECASE,
        )
        if match:
            return [
                DependencyUpdate(
                    package=match.group("package"),
                    to_version=_clean_version(match.group("to_version")),
                    confidence=0.45,
                    evidence=(context.branch,),
                )
            ]

    return []


def _extract_ecosystem_from_branch(branch: str) -> str | None:
    segments = branch.strip("/").split("/")
    if len(segments) < 2:
        return None
    return _ECOSYSTEM_BY_BRANCH.get(segments[1].lower())


def _split_package_and_version(value: str) -> tuple[str | None, str | None]:
    if "-" not in value:
        return None, None

    package, version = value.rsplit("-", 1)
    if not package or not version:
        return None, None
    return package, _clean_version(version)


def _clean_version(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().removeprefix("v")


def _dedupe_updates(candidates: list[DependencyUpdate]) -> list[DependencyUpdate]:
    deduped: dict[tuple[str, str], DependencyUpdate] = {}
    for candidate in candidates:
        key = (candidate.package.lower(), candidate.to_version)
        existing = deduped.get(key)
        if existing is None or candidate.confidence > existing.confidence:
            deduped[key] = candidate
    return list(deduped.values())
