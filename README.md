# sounddiff

[![CI](https://github.com/systemblueteam/sounddiff/actions/workflows/ci.yml/badge.svg)](https://github.com/systemblueteam/sounddiff/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/sounddiff)](https://pypi.org/project/sounddiff/)
[![Python](https://img.shields.io/pypi/pyversions/sounddiff)](https://pypi.org/project/sounddiff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![CodeRabbit Reviews](https://img.shields.io/coderabbit/prs/github/systemblueteam/sounddiff?utm_source=oss&utm_medium=github&utm_campaign=systemblueteam%2Fsounddiff&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)](https://coderabbit.ai)

Structured audio comparison for producers and developers. Think `git diff`, but for audio.

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

Supports wav, flac, ogg, and aiff out of the box. For mp3 and aac, install [ffmpeg](https://ffmpeg.org/).

## Quick start

Compare two files:

```sh
sounddiff old-mix.wav new-mix.wav
```

Get JSON output for CI pipelines:

```sh
sounddiff old.wav new.wav --format json
```

Generate an HTML report:

```sh
sounddiff old.wav new.wav --format html -o report.html
```

## Output formats

- **Terminal** (default): colored, human-readable diff using [rich](https://github.com/Textualize/rich)
- **JSON**: machine-readable, pipe it wherever you need
- **HTML**: self-contained report you can share or archive

## Documentation

See the [docs/](docs/) directory for detailed guides:

- [Installation](docs/install.md)
- [Usage](docs/usage.md)
- [API Reference](docs/api.md)
- [Architecture](docs/architecture.md)

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

Check the [issue board](https://github.com/systemblueteam/sounddiff/issues) for open work. Issues labeled `good first issue` are a solid starting point.

## Security

Report vulnerabilities to <dev@systemblue.io>. See [SECURITY.md](.github/SECURITY.md).

## License

MIT
