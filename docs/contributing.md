# Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) in the project root for the full guide.

Quick version:

1. Fork, clone, `pip install -e ".[dev]"`, `pre-commit install`
2. Create a branch: `feat/42-description`
3. Make changes, write tests, run `ruff check . && mypy src && pytest`
4. Open a PR against `main`

We use conventional commits, ruff for formatting, and mypy in strict mode.
