# Usage

## Basic comparison

```sh
sounddiff old-mix.wav new-mix.wav
```

This prints a colored terminal report showing loudness, spectral, temporal, and issue analysis.

## Output formats

### Terminal (default)

Human-readable, colored output:

```sh
sounddiff a.wav b.wav
```

### JSON

Machine-readable output for piping to other tools or CI:

```sh
sounddiff a.wav b.wav --format json
```

### HTML

Self-contained HTML report:

```sh
sounddiff a.wav b.wav --format html -o report.html
```

## Options

| Flag | Description |
|------|-------------|
| `--format` | Output format: `terminal`, `json`, `html` |
| `-o, --output` | Write output to file (useful with `--format html`) |
| `--verbose` | Show additional detail |
| `--no-color` | Disable colored terminal output |
| `--version` | Show version |
| `--help` | Show help |

## Supported formats

Without ffmpeg: WAV, FLAC, OGG, AIFF

With ffmpeg: MP3, AAC, M4A, WMA, OPUS

## CI usage

Use JSON output and parse the results in your CI pipeline:

```sh
sounddiff reference.wav output.wav --format json | jq '.loudness.lufs_delta'
```

See `examples/ci_regression_test.py` for a complete CI example with threshold-based pass/fail.
