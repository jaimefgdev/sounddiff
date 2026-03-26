# Contributing to sounddiff

Thanks for wanting to help. Whether you're fixing a bug, adding a feature, or improving the docs, every contribution matters.

## Setup

Getting a dev environment running takes about two minutes:

1. Fork and clone the repo
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Install pre-commit hooks: `pre-commit install`
5. Generate test audio: `python scripts/generate_test_audio.py`
6. Run tests: `pytest`

If all tests pass, you're ready to go.

## Finding something to work on

Check the [issue board](https://github.com/systemblueteam/sounddiff/issues). Issues labeled [`good first issue`](https://github.com/systemblueteam/sounddiff/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) are scoped for newcomers and have enough context to get started without deep knowledge of DSP. If you want to work on something, leave a comment so nobody duplicates effort.

Have an idea that isn't on the board? Open an issue first. A quick conversation saves everyone time.

## Making changes

1. Create a branch: `git checkout -b feat/42-your-description`
2. Make your changes. Write tests for new behavior.
3. Run the full check: `ruff check . && ruff format --check . && mypy src && pytest`
4. Commit with conventional commits: `feat: add stereo field analysis`
5. Push and open a PR against `main`

## PR expectations

- One concern per PR. Keep it focused.
- Reference the issue in your PR body: `Closes #42`
- CI must pass before review.
- [CodeRabbit](https://coderabbit.ai) reviews every PR automatically. Address its feedback or explain why you disagree.
- Maintainers will review within a few days. If it's been a week, ping us. No hard feelings.

## Code style

Ruff handles formatting and linting. If ruff is happy, we're happy. Beyond that:

- Type hints on all public functions. `mypy` runs in strict mode.
- Docstrings on public functions (Google style).
- No `# type: ignore` without a comment explaining why.

You don't need to worry about formatting manually. The pre-commit hooks handle it on every commit.

## Tests

Every new feature needs tests. Every bug fix needs a regression test. We use [hypothesis](https://hypothesis.readthedocs.io/) for property-based testing on DSP functions.

Test audio is generated deterministically by `scripts/generate_test_audio.py`, not committed to the repo. This keeps the repo lean and tests reproducible.

If you're not sure how to test something, ask in the issue. We'd rather help you write a good test than skip testing.

## Branch naming

Include the issue number when there is one:

- `feat/42-segment-detection`
- `fix/17-clipping-threshold`
- `docs/8-usage-guide`
- `chore/12-ci-update`

## Commits

We use [conventional commits](https://www.conventionalcommits.org/):

```text
feat: add spectral band comparison
fix: handle mono files in loudness calculation
docs: add installation guide
test: add property tests for temporal alignment
chore: update CI to Python 3.13
refactor: extract segment detection into its own module
```

## Questions?

Open an issue. We're happy to help.
