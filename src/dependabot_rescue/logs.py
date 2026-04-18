"""CI log classification for dependency update failures."""

from __future__ import annotations

import re

from dependabot_rescue.models import DependencyUpdate, FailureSignal

_CATEGORY_PATTERNS: tuple[tuple[str, str, float, tuple[re.Pattern[str], ...]], ...] = (
    (
        "dependency_conflict",
        "The update likely failed during dependency resolution.",
        0.82,
        (
            re.compile(r"ResolutionImpossible", re.IGNORECASE),
            re.compile(r"ERESOLVE", re.IGNORECASE),
            re.compile(r"conflicting peer dependency", re.IGNORECASE),
            re.compile(r"version solving failed", re.IGNORECASE),
        ),
    ),
    (
        "lockfile_drift",
        "The manifest and lockfile appear to be out of sync.",
        0.88,
        (
            re.compile(r"lockfile.*out of date", re.IGNORECASE),
            re.compile(r"package-lock\.json.*not up to date", re.IGNORECASE),
            re.compile(r"poetry\.lock.*not consistent", re.IGNORECASE),
            re.compile(r"Cargo\.lock.*needs to be updated", re.IGNORECASE),
        ),
    ),
    (
        "import_error",
        "The updated package likely changed import or module availability.",
        0.8,
        (
            re.compile(r"ModuleNotFoundError:", re.IGNORECASE),
            re.compile(r"ImportError:", re.IGNORECASE),
            re.compile(r"Cannot find module", re.IGNORECASE),
        ),
    ),
    (
        "removed_api",
        "The update likely removed or changed an API your code still calls.",
        0.78,
        (
            re.compile(r"cannot import name", re.IGNORECASE),
            re.compile(r"has no attribute", re.IGNORECASE),
            re.compile(r"has no exported member", re.IGNORECASE),
            re.compile(r"unexpected keyword argument", re.IGNORECASE),
        ),
    ),
    (
        "runtime_mismatch",
        "The dependency update appears incompatible with the current runtime.",
        0.8,
        (
            re.compile(r"requires Python\s*[>=<~!]", re.IGNORECASE),
            re.compile(r"not compatible with your version of node", re.IGNORECASE),
            re.compile(r"Unsupported engine", re.IGNORECASE),
            re.compile(r"requires node", re.IGNORECASE),
        ),
    ),
    (
        "compile_failure",
        "The update appears to have triggered a compilation or type-check error.",
        0.68,
        (
            re.compile(r"cannot find symbol", re.IGNORECASE),
            re.compile(r"\bTS\d{4}\b", re.IGNORECASE),
            re.compile(r"Compilation failed", re.IGNORECASE),
            re.compile(r"error\[E\d+\]", re.IGNORECASE),
        ),
    ),
    (
        "test_failure",
        "The dependency update appears to have changed behavior that tests assert on.",
        0.58,
        (
            re.compile(r"AssertionError", re.IGNORECASE),
            re.compile(r"FAILED\s+\S+", re.IGNORECASE),
            re.compile(r"\b\d+\s+failed\b", re.IGNORECASE),
        ),
    ),
)


def classify_logs(log_texts: list[str], updates: list[DependencyUpdate]) -> list[FailureSignal]:
    """Classify CI logs into likely dependency-update failure categories."""

    buckets: dict[str, list[str]] = {}
    category_meta: dict[str, tuple[str, float]] = {}
    related_packages: dict[str, str | None] = {}
    known_packages = {update.package.lower(): update.package for update in updates}

    for log_text in log_texts:
        for line in log_text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            for category, summary, base_confidence, patterns in _CATEGORY_PATTERNS:
                if not any(pattern.search(stripped) for pattern in patterns):
                    continue
                buckets.setdefault(category, []).append(stripped)
                category_meta[category] = (summary, base_confidence)
                if category not in related_packages:
                    related_packages[category] = _find_related_package(stripped, known_packages)

    signals: list[FailureSignal] = []
    for category, evidence in buckets.items():
        summary, base_confidence = category_meta[category]
        bonus = min(0.12, 0.02 * max(0, len(evidence) - 1))
        signals.append(
            FailureSignal(
                category=category,
                summary=summary,
                confidence=round(min(0.99, base_confidence + bonus), 2),
                evidence=tuple(evidence[:3]),
                related_package=related_packages.get(category),
            )
        )

    if signals:
        return sorted(signals, key=lambda signal: signal.confidence, reverse=True)

    return [
        FailureSignal(
            category="unknown",
            summary="No known dependency-related failure pattern was detected in the provided logs.",
            confidence=0.2,
            evidence=(),
        )
    ]


def _find_related_package(line: str, known_packages: dict[str, str]) -> str | None:
    line_lower = line.lower()
    for package_lower, original_name in known_packages.items():
        if package_lower in line_lower:
            return original_name
    return None
