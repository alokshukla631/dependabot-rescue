# Changelog

## v0.1.0 - 2026-04-18

Initial public release of `dependabot-rescue`.

### Added

- normalized pull request context parsing for Dependabot and Renovate
- dependency update extraction from PR titles, branches, and body bullets
- CI log classification for common dependency-update failure modes
- Markdown and JSON rescue report rendering
- local CLI for event-file and manual-input analysis
- unit tests, realistic fixtures, and GitHub Actions CI
- contributor guide and GitHub issue templates

### Fixed

- Renovate package extraction for `update dependency ...` PR titles
- Windows console entry point stability by switching the published script name to `dep_rescue`
- GitHub Actions workflow compatibility by upgrading to `actions/checkout@v6` and `actions/setup-python@v6`
