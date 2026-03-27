# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-26

### Added

- Integrated LUFS comparison (ITU-R BS.1770 via pyloudnorm)
- True peak measurement (dBTP)
- Loudness range (LRA) comparison per EBU R128
- Spectral band energy comparison (low/mid/high, configurable bands)
- Waveform cross-correlation for segment similarity scoring
- Segment change detection: added, removed, shifted, or changed sections
- Clipping detection with timestamp, channel, and sample count
- Silence detection with configurable threshold and minimum duration
- Audio file loading via soundfile (WAV, FLAC, OGG, AIFF)
- CLI with click: `sounddiff <file1> <file2>`
- Terminal output with rich (colored, grouped by category)
- JSON output for scripts and CI pipelines
- HTML report output (self-contained, jinja2 templates)
- `--no-color` flag for plain terminal output
- `--version` flag
- Sample rate mismatch warnings
- Duration difference display in metadata section
- Test suite with 60 tests (pytest + hypothesis)
- CI pipeline (Python 3.13 on Ubuntu)
- Documentation (install, usage, API reference, architecture)

### Fixed

- Terminal output no longer prints twice
- Spectral band delta no longer shows absurd values for near-zero energy bands

[0.1.0]: https://github.com/systemblueteam/sounddiff/releases/tag/v0.1.0
