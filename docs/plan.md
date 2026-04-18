# Project Plan

## Objective

Build a public, OSS-friendly maintainer tool that helps developers recover faster from failing Dependabot and Renovate pull requests.

## User Problem

Maintainers already receive update PRs. The hard part begins when those PRs fail CI and someone must manually inspect logs, infer which update caused the break, and decide whether the fix is a pin, a code migration, a lockfile refresh, or a test update.

## User Promise

Given a dependency update PR and CI logs, `dependabot-rescue` should produce a concise rescue report that answers:

- which dependency changed
- what likely failed
- how confident the tool is
- what the maintainer should try next

## Primary Users

- solo maintainers
- OSS library maintainers
- small engineering teams using Dependabot
- teams using Renovate but lacking dedicated dependency tooling

## MVP Scope

### In scope

- Dependabot and Renovate metadata parsing
- Heuristic extraction of updated package names and versions
- CI log parsing for common Python and JS/TS failure patterns
- Rescue report generation in Markdown and JSON
- Local CLI
- Unit tests and GitHub Actions CI

### Out of scope

- Hosted GitHub App
- Automatic commit generation for every failure mode
- Multi-language AST refactoring
- Full release-note summarization from arbitrary remote sources

## Milestones

## Milestone 1: Project foundation

- Create public repository
- Add README, plan, and design documents
- Add package scaffold and issue templates

## Milestone 2: Analysis core

- Add PR metadata models
- Add update extraction logic
- Add CI failure classification
- Add Markdown/JSON report rendering

## Milestone 3: CLI and CI

- Add command-line entrypoint
- Add example fixtures
- Add unit tests
- Add GitHub Actions workflow

## Milestone 4: Hardening

- Run end-to-end fixture tests
- File issues for gaps found during testing
- Fix issues in separate commits
- Cut the first tagged release

## Acceptance Criteria for v0.1.0

- A user can run one command against an event payload and CI log files
- The tool identifies whether a PR is from Dependabot or Renovate
- The tool extracts at least one dependency update when present
- The tool classifies at least one likely failure category from the logs
- The report includes actionable next steps
- Tests pass in CI
- Docs explain how to use, extend, and contribute

## Risks

- CI logs vary wildly across ecosystems and providers
- PR bodies are inconsistent
- Heuristics may overfit to common patterns and miss edge cases

## Risk Mitigation

- Keep the classifier category-based instead of overclaiming exact fixes
- Make confidence explicit
- Preserve raw evidence in the report
- Build fixtures from realistic examples

## Release Strategy

- Ship v0.1.0 once the core CLI, tests, and docs are solid
- Keep release scope narrow and honest
- Prefer reliability over breadth in the first release
