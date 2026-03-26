# API Reference

## Core

### `sounddiff.core.diff(path_a, path_b) -> DiffResult`

Compare two audio files and return a structured diff.

```python
from sounddiff.core import diff

result = diff("old.wav", "new.wav")
print(result.loudness.lufs_delta)  # +1.4
print(result.temporal.overall_correlation)  # 0.98
```

## Types

All result types are frozen dataclasses in `sounddiff.types`.

### `DiffResult`

Top-level result containing all analysis outputs:

- `metadata: MetadataComparison` - file metadata comparison
- `loudness: LoudnessComparison` - LUFS, peak, LRA
- `spectral: SpectralComparison` - frequency band energy
- `temporal: TemporalComparison` - correlation and segments
- `detection: DetectionResult` - clipping and silence
- `warnings: list[str]` - any warnings (e.g., sample rate mismatch)

### `LoudnessComparison`

- `file_a: LoudnessResult` - measurements for first file
- `file_b: LoudnessResult` - measurements for second file
- `lufs_delta: float` - LUFS difference (property)
- `peak_delta: float` - true peak difference (property)
- `lra_delta: float` - loudness range difference (property)

### `SpectralComparison`

- `bands: list[SpectralBand]` - per-band comparison

### `TemporalComparison`

- `segments: list[Segment]` - detected segments
- `overall_correlation: float` - overall waveform correlation

### `DetectionResult`

- `clips: list[ClipEvent]` - detected clipping events
- `silence_regions_a: list[SilenceRegion]` - silence in file A
- `silence_regions_b: list[SilenceRegion]` - silence in file B

## Report

### `sounddiff.report.render(result, fmt, output_path=None) -> str`

Render a DiffResult in the specified format.

```python
from sounddiff.report import render
from sounddiff.types import OutputFormat

output = render(result, OutputFormat.JSON)
output = render(result, OutputFormat.HTML, output_path="report.html")
```
