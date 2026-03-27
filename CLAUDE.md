# sounddiff

Structured audio comparison CLI. Python 3.10+, src layout, hatchling build.

Published on PyPI: `pip install sounddiff`

## Build & Test

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python scripts/generate_test_audio.py
pytest
ruff check . && ruff format --check . && mypy src
```

## Architecture

```
src/sounddiff/
  types.py       # Dataclasses for all results
  formats.py     # Audio I/O via soundfile
  loudness.py    # LUFS, true peak, LRA (pyloudnorm)
  spectral.py    # Band energy comparison (numpy FFT)
  temporal.py    # Cross-correlation, segment detection
  detection.py   # Clipping, silence detection
  core.py        # Pipeline orchestration
  cli.py         # Click CLI entry point
  report.py      # Output formatters (terminal/JSON/HTML)
```

## Conventions

- **Ruff** for linting and formatting. No black, isort, or flake8.
- **mypy strict mode.** Type hints everywhere.
- **Google-style docstrings** on all public functions.
- **Conventional commits.** `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`.
- **One concern per PR.** Small, focused diffs. Squash merge.
- **pytest + hypothesis** for testing. Property-based tests for DSP functions.
- **Test audio is generated, not committed.** Run `scripts/generate_test_audio.py`.
- **No `# type: ignore` without a comment.**

## CI & Release

- CI: lint + test on Python 3.10 and 3.13, Ubuntu only. No macOS matrix (no platform-specific code).
- Releases are tag-based. `git tag v0.x.0 && git push --tags` triggers build, PyPI publish (trusted publisher), and GitHub Release.
- PyPI trusted publisher is configured. Never use API tokens for uploads.
- CodeRabbit reviews all PRs including `.github/` files.
- Sentry Seer reviews PRs. No Sentry release workflow (CLI tool, no deployed infra).

## Key dependencies

| Package | Purpose |
|---------|---------|
| soundfile | Audio I/O (wav, flac, ogg, aiff) |
| numpy | Array math, FFT, correlation |
| scipy | Signal processing, filtering |
| pyloudnorm | ITU-R BS.1770 LUFS measurement |
| click | CLI framework |
| rich | Terminal formatting |
| jinja2 | HTML report templates |

## Gotchas

- `pip` doesn't work system-wide on macOS. Use `pipx install sounddiff` for global CLI access, or work inside the venv.
- Spectral delta_db clamps energy to -100 dB floor before computing deltas. Without this, noise floor differences produce absurd values (+80 dB).
- Rich Console with `record=True` still writes to stdout. Must pass `file=io.StringIO()` to capture without printing.
- `--verbose` flag exists in the CLI but isn't wired to anything yet.
