# dependabot-rescue

`dependabot-rescue` is an open-source agent for maintainers who are buried under failing dependency update PRs.

The project starts with a simple goal: when a Dependabot or Renovate PR turns red, generate a useful rescue report instead of forcing a maintainer to manually read every CI log from scratch.

## Status

Version `0.1.0` is ready. As of April 18, 2026, the current MVP includes:

- GitHub-hosted repositories
- Dependabot and Renovate pull requests
- Python and JavaScript/TypeScript projects
- CI failure classification and rescue report generation
- Markdown and JSON report output
- Local CLI execution from event payloads or manual PR fields
- Unit tests and GitHub Actions CI

## Why this exists

Dependency update PRs are easy when the update is harmless and hard when the update breaks tests, imports, build steps, or runtime assumptions. The painful part is usually not opening the PR. The painful part is figuring out why it broke and what to do next.

`dependabot-rescue` aims to:

- extract dependency update context from PR metadata
- classify CI failures from logs
- explain likely breakage causes in plain English
- suggest the smallest next patch or migration step

## MVP Plan

- Parse Dependabot and Renovate PR metadata
- Parse CI logs from one or more jobs
- Classify common dependency-update failure modes
- Generate Markdown and JSON rescue reports
- Ship a small CLI that works locally and in CI
- Add tests and a GitHub Actions validation workflow

Planning and design documents:

- [Project Plan](./docs/plan.md)
- [Design Doc](./docs/design.md)

## Non-goals for v0.1

- Full autonomous code repair across every ecosystem
- GitHub App hosting and OAuth setup
- Deep package-manager-specific changelog scraping
- Automatic PR commenting without an explicit token or workflow

## Quick Start

Install locally:

```bash
python -m pip install -e .
```

Analyze a GitHub event payload plus one or more CI logs:

```bash
dep_rescue analyze --event-path event.json --log-file ci.log
```

Analyze without a GitHub event file:

```bash
dep_rescue analyze \
  --title "Bump requests from 2.31.0 to 2.32.0" \
  --author "dependabot[bot]" \
  --branch "dependabot/pip/requests-2.32.0" \
  --log-file ci.log
```

Write machine-readable JSON output:

```bash
dep_rescue analyze --event-path event.json --log-file ci.log --format json --output report.json
```

## Current Capabilities

- infer whether a PR came from Dependabot or Renovate
- extract package/version updates from common PR title, branch, and body formats
- classify CI logs into dependency conflict, lockfile drift, import error, removed API, runtime mismatch, compile failure, test failure, or unknown
- generate action-oriented rescue reports with evidence snippets

## Local Testing

Run the test suite with:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Roadmap

- v0.1: local CLI + report generator + core heuristics
- v0.2: GitHub Action wrapper + richer package ecosystem support
- v0.3: guided patch suggestions and optional PR comment mode

## License

[MIT](./LICENSE)
