# dependabot-rescue

`dependabot-rescue` is an open-source agent for maintainers who are buried under failing dependency update PRs.

The project starts with a simple goal: when a Dependabot or Renovate PR turns red, generate a useful rescue report instead of forcing a maintainer to manually read every CI log from scratch.

## Status

This repository is under active development. The current milestone is a focused MVP for:

- GitHub-hosted repositories
- Dependabot and Renovate pull requests
- Python and JavaScript/TypeScript projects
- CI failure classification and rescue report generation

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

## Development

Implementation is intentionally starting small and standard-library-first so contributors can run it easily.

Target command:

```bash
python -m dependabot_rescue.cli analyze --event-path event.json --log-file ci.log
```

## Roadmap

- v0.1: local CLI + report generator + core heuristics
- v0.2: GitHub Action wrapper + richer package ecosystem support
- v0.3: guided patch suggestions and optional PR comment mode

## License

[MIT](./LICENSE)
