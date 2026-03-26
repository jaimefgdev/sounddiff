# Architecture

## Module layout

```
sounddiff/
  types.py       Data types (frozen dataclasses)
  formats.py     Audio I/O (soundfile wrapper)
  loudness.py    LUFS, true peak, LRA (pyloudnorm)
  spectral.py    Band energy comparison (numpy FFT)
  temporal.py    Cross-correlation, segment detection (scipy)
  detection.py   Clipping, silence detection
  core.py        Pipeline orchestration
  cli.py         Click CLI entry point
  report.py      Output formatters
```

## Data flow

```
CLI (click)
  -> core.diff(path_a, path_b)
    -> formats.load_audio(path) x2
    -> loudness.compare_loudness(...)
    -> spectral.compare_spectral(...)
    -> temporal.compare_temporal(...)
    -> detection.compare_detection(...)
    -> DiffResult
  -> report.render(result, format)
  -> stdout or file
```

## Design decisions

**Frozen dataclasses for all results.** Results are immutable after creation. Properties compute derived values (deltas) on access. This keeps the data model simple and testable.

**Each analysis module is independent.** Loudness, spectral, temporal, and detection modules don't import from each other. The core module orchestrates them. This makes it easy to add new analysis modules or run specific analyses in isolation.

**Mono mixing happens at the analysis layer.** The formats module always returns multi-channel data. Each analysis module decides how to handle channels (most mix to mono for analysis, detection preserves per-channel information).

**No global state.** Every function takes its inputs as arguments and returns its outputs. No module-level caches or singletons.
