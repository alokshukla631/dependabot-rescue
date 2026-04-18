# Contributing

Thanks for taking a look at `dependabot-rescue`.

## Local Setup

```bash
python -m pip install -e .
```

## Running Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Contribution Guidelines

- keep changes focused and reviewable
- prefer deterministic heuristics over opaque behavior
- add or update fixtures when changing extraction or log classification
- include tests for new parsing rules and regressions
- keep README and docs aligned with the shipped behavior

## Reporting Bugs

Please use the bug report issue template and include:

- the PR title or event payload shape
- the failing CI log snippet
- expected vs actual rescue output
