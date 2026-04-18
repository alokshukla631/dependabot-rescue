# Design Doc

## Overview

`dependabot-rescue` is a local-first analysis tool that takes pull request metadata plus CI logs and returns a structured rescue report.

The first version is optimized for reliability and explainability rather than fully autonomous fixing.

## Design Goals

- easy to run locally and in GitHub Actions
- standard-library-first implementation
- explicit evidence and confidence in every report
- clean extension points for new ecosystems and classifiers

## High-Level Flow

1. Load GitHub event or raw PR metadata
2. Normalize the PR source into a shared pull request model
3. Extract dependency updates from branch name, title, body, and file hints
4. Parse CI logs and classify failure signals
5. Generate a rescue report in Markdown and JSON

## Core Modules

## `models.py`

Defines immutable domain objects:

- pull request metadata
- dependency updates
- failure signals
- rescue findings
- rescue report

## `providers.py`

Normalizes GitHub event payloads and lightweight local inputs into a common `PullRequestContext`.

## `updates.py`

Extracts package names, source and target versions, ecosystem hints, and dependency tool hints from titles, branch names, and PR bodies.

## `logs.py`

Scans CI logs line-by-line for recognizable failure patterns such as:

- missing module/import errors
- removed symbol or API usage
- lockfile drift
- version conflicts
- unsupported runtime versions
- test failures following successful install

## `reporting.py`

Builds:

- a machine-readable JSON report
- a human-readable Markdown report with evidence snippets and suggested next actions

## `cli.py`

Provides the user-facing command:

```bash
python -m dependabot_rescue.cli analyze --event-path event.json --log-file ci.log
```

## Architecture Notes

### Why heuristics first

Heuristics are inspectable, easy to test, and practical for the first release. They also avoid turning the tool into a black box that sounds confident without showing evidence.

### Confidence model

Each finding carries a confidence score. Confidence is driven by:

- number of matching signals
- specificity of the pattern
- whether the update extraction and failure signal point at the same package/ecosystem

### Report philosophy

The tool should not pretend it fixed a problem if it only found a clue. Reports must separate:

- evidence
- inference
- recommended next step

## Planned File Layout

```text
src/dependabot_rescue/
  __init__.py
  cli.py
  models.py
  providers.py
  updates.py
  logs.py
  reporting.py
tests/
  fixtures/
  test_updates.py
  test_logs.py
  test_cli.py
```

## Testing Strategy

- unit tests for metadata extraction
- unit tests for log classification
- snapshot-like assertions for Markdown report generation
- CLI integration tests using fixture files

## Future Extensions

- package-manager-specific changelog adapters
- automated patch recommendation templates
- GitHub PR comment mode
- optional LLM summarization on top of deterministic evidence extraction
