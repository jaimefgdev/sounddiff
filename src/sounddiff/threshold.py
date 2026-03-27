"""Threshold checking for CI mode."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sounddiff.types import DiffResult

VALID_KEYS = frozenset({"loudness", "peak", "lra", "duration", "correlation", "spectral"})


def parse_thresholds(raw: str) -> dict[str, float]:
    """Parse a comma-separated threshold string into a dict.

    Args:
        raw: String like "loudness=0.5,peak=0.3".

    Returns:
        Dict mapping threshold names to float values.

    Raises:
        ValueError: If the format is invalid or a key is unrecognized.
    """
    thresholds: dict[str, float] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if "=" not in pair:
            raise ValueError(f"Invalid threshold format: '{pair}'. Expected key=value.")
        key, _, value = pair.partition("=")
        key = key.strip()
        value = value.strip()
        if key not in VALID_KEYS:
            raise ValueError(
                f"Unknown threshold key: '{key}'. Valid keys: {', '.join(sorted(VALID_KEYS))}"
            )
        try:
            thresholds[key] = float(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid threshold value for '{key}': '{value}'. Must be a number."
            ) from e
    return thresholds


def check_thresholds(result: DiffResult, thresholds: dict[str, float]) -> list[str]:
    """Check analysis results against thresholds.

    Args:
        result: The diff result to check.
        thresholds: Dict of threshold names to maximum allowed values.
            For most keys, the absolute delta must be <= the threshold.
            For 'correlation', the overall correlation must be >= the threshold.

    Returns:
        List of human-readable failure messages. Empty means all passed.
    """
    failures: list[str] = []

    if "loudness" in thresholds:
        actual = abs(result.loudness.lufs_delta)
        limit = thresholds["loudness"]
        if actual > limit:
            failures.append(f"loudness: {actual:.2f} dB delta exceeds {limit:.2f} dB")

    if "peak" in thresholds:
        actual = abs(result.loudness.peak_delta)
        limit = thresholds["peak"]
        if actual > limit:
            failures.append(f"peak: {actual:.2f} dBTP delta exceeds {limit:.2f} dBTP")

    if "lra" in thresholds:
        actual = abs(result.loudness.lra_delta)
        limit = thresholds["lra"]
        if actual > limit:
            failures.append(f"lra: {actual:.2f} LU delta exceeds {limit:.2f} LU")

    if "duration" in thresholds:
        actual = abs(result.metadata.duration_delta)
        limit = thresholds["duration"]
        if actual > limit:
            failures.append(f"duration: {actual:.3f}s delta exceeds {limit:.3f}s")

    if "correlation" in thresholds:
        actual = result.temporal.overall_correlation
        limit = thresholds["correlation"]
        if actual < limit:
            failures.append(f"correlation: {actual:.4f} is below minimum {limit:.4f}")

    if "spectral" in thresholds:
        limit = thresholds["spectral"]
        max_delta = max(abs(band.delta_db) for band in result.spectral.bands)
        if max_delta > limit:
            worst_band = max(result.spectral.bands, key=lambda b: abs(b.delta_db))
            failures.append(
                f"spectral: {max_delta:.2f} dB delta in {worst_band.name} "
                f"band exceeds {limit:.2f} dB"
            )

    return failures
