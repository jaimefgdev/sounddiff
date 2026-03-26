# Contributing to sounddiff

Thanks for wanting to help. Here's how to get started.

## Setup

1. Fork and clone the repo
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Install pre-commit hooks: `pre-commit install`
5. Generate test audio: `python scripts/generate_test_audio.py`
6. Run tests: `pytest`

If all tests pass, you're ready.

## Finding something to work on

Check the [issue board](https://github.com/systemblueteam/sounddiff/issues). Issues labeled `good first issue` are a solid starting point. If you want to work on something, leave a comment so nobody duplicates effort.

## Making changes

1. Create a branch: `git checkout -b feat/42-your-description`
2. Make your changes. Write tests.
3. Run the full check: `ruff check . && ruff format --check . && mypy src && pytest`
4. Commit with conventional commits: `feat: add stereo field analysis`
5. Push and open a PR against `main`

## PR expectations

- One concern per PR. Keep it focused.
- Reference the issue: `Closes #42`
- CI must pass.
- Maintainers will review within a few days. If it's been a week, ping us. No hard feelings.

## Code style

Ruff handles formatting and linting. If ruff is happy, we're happy. Type hints on everything. Docstrings on public functions (Google style).

## Tests

Every new feature needs tests. Every bug fix needs a regression test. We use hypothesis for property-based testing on DSP functions. If you're not sure how to test something, ask in the issue.

## Branch naming

- `feat/42-segment-detection`
- `fix/17-clipping-threshold`
- `docs/8-usage-guide`
- `chore/12-ci-update`

## Commits

Conventional commits:

```
feat: add spectral band comparison
fix: handle mono files in loudness calculation
docs: add installation guide
test: add property tests for temporal alignment
chore: update CI to Python 3.13
refactor: extract segment detection into its own module
```

## Questions?

Open a discussion or ask in the issue. We don't bite.
