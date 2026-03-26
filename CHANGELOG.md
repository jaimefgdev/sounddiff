# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project scaffolding with src layout and hatchling build system
- CI pipeline with Python 3.10-3.13 matrix on Linux and macOS
- Pre-commit hooks (ruff, mypy, gitleaks)
- Core analysis modules: loudness, spectral, temporal, detection
- CLI with click: `sounddiff <file1> <file2>`
- Output formats: terminal (rich), JSON, HTML
- Test infrastructure with pytest and hypothesis
