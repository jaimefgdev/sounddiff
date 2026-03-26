# sounddiff

[![CI](https://github.com/systemblueteam/sounddiff/actions/workflows/ci.yml/badge.svg)](https://github.com/systemblueteam/sounddiff/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/sounddiff)](https://pypi.org/project/sounddiff/)
[![Python](https://img.shields.io/pypi/pyversions/sounddiff)](https://pypi.org/project/sounddiff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![CodeRabbit Reviews](https://img.shields.io/coderabbit/prs/github/systemblueteam/sounddiff?utm_source=oss&utm_medium=github&utm_campaign=systemblueteam%2Fsounddiff&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)](https://coderabbit.ai)

Compare two audio files. Get a clear report on what changed: loudness, EQ balance, timing, edits, silence, and clipping. Terminal output, JSON for CI, or a self-contained HTML report.

## What it does

```text
$ sounddiff mix-v3.wav mix-v4.wav

sounddiff: mix-v3.wav vs mix-v4.wav

Duration     3:42.108 → 3:42.108  (no change)
Sample Rate  48000 Hz → 48000 Hz  (no change)
Channels     stereo   → stereo    (no change)

Loudness (integrated)
  LUFS       -14.2    → -12.8     (+1.4 dB)
  Peak dBTP  -1.1     → -0.3      (+0.8 dB)
  LRA         8.2     →  6.4      (-1.8 LU)

Spectral
  Low  (20-250 Hz)    +0.8 dB avg
  Mid  (250-4k Hz)    +0.3 dB avg
  High (4k-20k Hz)    +1.9 dB avg

Segments
  0:00-1:12   similar (correlation: 0.97)
  1:12-1:14   ADDED (new content, 2.1s)
  1:14-3:42   similar (correlation: 0.98, shifted +2.1s)

Issues
  ⚠ Clipping detected in mix-v4.wav at 2:31.4 (3 samples)
```

## Install

```sh
pip install sounddiff
```

Requires Python 3.10 or later. Supports wav, flac, ogg, and aiff out of the box. For mp3 and aac, install [ffmpeg](https://ffmpeg.org/).

## Quick start

Compare two audio files:

```sh
sounddiff old-mix.wav new-mix.wav
```

Get JSON output for scripts and CI pipelines:

```sh
sounddiff old.wav new.wav --format json
```

Generate a self-contained HTML report to share with your team:

```sh
sounddiff old.wav new.wav --format html -o report.html
```

## What it analyzes

| Category | What it measures |
|----------|-----------------|
| **Loudness** | Integrated LUFS, true peak (dBTP), loudness range (LRA) |
| **Spectral** | Energy per frequency band (low, mid, high) with dB deltas |
| **Temporal** | Segment-level similarity via cross-correlation |
| **Detection** | Clipping events, silence regions |
| **Metadata** | Duration, sample rate, channels, bit depth |

## Output formats

- **Terminal** (default): colored, human-readable diff using [rich](https://github.com/Textualize/rich)
- **JSON**: machine-readable, pipe it to [jq](https://jqlang.github.io/jq/) or parse it in your CI pipeline
- **HTML**: self-contained report you can share, archive, or open in any browser

## Documentation

- [Installation](docs/install.md) - system dependencies, shell completions, ffmpeg setup
- [Usage](docs/usage.md) - all CLI options with examples
- [API Reference](docs/api.md) - use sounddiff as a Python library
- [Architecture](docs/architecture.md) - how the codebase is organized

## Contributing

We welcome contributions from anyone. Whether it's fixing a typo, improving error messages, or adding a new analysis module, we'd love your help.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and workflow.

Check the [issue board](https://github.com/systemblueteam/sounddiff/issues) for open work. Issues labeled [`good first issue`](https://github.com/systemblueteam/sounddiff/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) are a great place to start if you're new to the project.

## Security

Report vulnerabilities to <dev@systemblue.io>. See [SECURITY.md](.github/SECURITY.md).

## License

[MIT](LICENSE) - use it however you want.
