"""Tests for threshold parsing and checking."""

from __future__ import annotations

import pytest

from sounddiff.threshold import VALID_KEYS, check_thresholds, parse_thresholds
from sounddiff.types import (
    AudioMetadata,
    DetectionResult,
    DiffResult,
    LoudnessComparison,
    LoudnessResult,
    MetadataComparison,
    SpectralBand,
    SpectralComparison,
    TemporalComparison,
)


def _make_result(
    lufs_a: float = -14.0,
    lufs_b: float = -14.0,
    peak_a: float = -1.0,
    peak_b: float = -1.0,
    lra_a: float = 6.0,
    lra_b: float = 6.0,
    duration_a: float = 10.0,
    duration_b: float = 10.0,
    correlation: float = 1.0,
    band_delta: float = 0.0,
) -> DiffResult:
    """Build a minimal DiffResult for threshold testing."""
    meta_a = AudioMetadata(
        path="a.wav",
        duration=duration_a,
        sample_rate=48000,
        channels=2,
        bit_depth=24,
        format_name="WAV",
        frames=int(duration_a * 48000),
    )
    meta_b = AudioMetadata(
        path="b.wav",
        duration=duration_b,
        sample_rate=48000,
        channels=2,
        bit_depth=24,
        format_name="WAV",
        frames=int(duration_b * 48000),
    )
    return DiffResult(
        metadata=MetadataComparison(file_a=meta_a, file_b=meta_b),
        loudness=LoudnessComparison(
            file_a=LoudnessResult(lufs=lufs_a, true_peak_dbtp=peak_a, loudness_range=lra_a),
            file_b=LoudnessResult(lufs=lufs_b, true_peak_dbtp=peak_b, loudness_range=lra_b),
        ),
        spectral=SpectralComparison(
            bands=[
                SpectralBand(
                    name="mid",
                    low_hz=250.0,
                    high_hz=4000.0,
                    energy_db_a=-20.0,
                    energy_db_b=-20.0 + band_delta,
                ),
            ]
        ),
        temporal=TemporalComparison(segments=[], overall_correlation=correlation),
        detection=DetectionResult(clips=[], silence_regions_a=[], silence_regions_b=[]),
    )


class TestParseThresholds:
    def test_single_key(self) -> None:
        assert parse_thresholds("loudness=0.5") == {"loudness": 0.5}

    def test_multiple_keys(self) -> None:
        result = parse_thresholds("loudness=0.5,peak=0.3")
        assert result == {"loudness": 0.5, "peak": 0.3}

    def test_all_valid_keys(self) -> None:
        raw = ",".join(f"{k}=1.0" for k in sorted(VALID_KEYS))
        result = parse_thresholds(raw)
        assert set(result.keys()) == VALID_KEYS

    def test_whitespace_tolerance(self) -> None:
        result = parse_thresholds(" loudness = 0.5 , peak = 0.3 ")
        assert result == {"loudness": 0.5, "peak": 0.3}

    def test_invalid_key(self) -> None:
        with pytest.raises(ValueError, match="Unknown threshold key"):
            parse_thresholds("bogus=1.0")

    def test_invalid_format_no_equals(self) -> None:
        with pytest.raises(ValueError, match="Invalid threshold format"):
            parse_thresholds("loudness")

    def test_invalid_value(self) -> None:
        with pytest.raises(ValueError, match="Must be a number"):
            parse_thresholds("loudness=abc")


class TestCheckThresholds:
    def test_all_pass(self) -> None:
        result = _make_result()
        failures = check_thresholds(result, {"loudness": 0.5, "peak": 0.3})
        assert failures == []

    def test_loudness_exceeds(self) -> None:
        result = _make_result(lufs_a=-14.0, lufs_b=-12.0)
        failures = check_thresholds(result, {"loudness": 0.5})
        assert len(failures) == 1
        assert "loudness" in failures[0]
        assert "2.00 dB" in failures[0]

    def test_peak_exceeds(self) -> None:
        result = _make_result(peak_a=-1.0, peak_b=0.0)
        failures = check_thresholds(result, {"peak": 0.5})
        assert len(failures) == 1
        assert "peak" in failures[0]

    def test_lra_exceeds(self) -> None:
        result = _make_result(lra_a=6.0, lra_b=9.0)
        failures = check_thresholds(result, {"lra": 1.0})
        assert len(failures) == 1
        assert "lra" in failures[0]

    def test_duration_exceeds(self) -> None:
        result = _make_result(duration_a=10.0, duration_b=10.5)
        failures = check_thresholds(result, {"duration": 0.01})
        assert len(failures) == 1
        assert "duration" in failures[0]

    def test_correlation_below(self) -> None:
        result = _make_result(correlation=0.85)
        failures = check_thresholds(result, {"correlation": 0.95})
        assert len(failures) == 1
        assert "correlation" in failures[0]
        assert "below" in failures[0]

    def test_correlation_passes(self) -> None:
        result = _make_result(correlation=0.99)
        failures = check_thresholds(result, {"correlation": 0.95})
        assert failures == []

    def test_spectral_exceeds(self) -> None:
        result = _make_result(band_delta=5.0)
        failures = check_thresholds(result, {"spectral": 3.0})
        assert len(failures) == 1
        assert "spectral" in failures[0]
        assert "mid" in failures[0]

    def test_multiple_failures(self) -> None:
        result = _make_result(lufs_a=-14.0, lufs_b=-12.0, peak_a=-1.0, peak_b=0.0)
        failures = check_thresholds(result, {"loudness": 0.5, "peak": 0.5})
        assert len(failures) == 2

    def test_exact_threshold_passes(self) -> None:
        result = _make_result(lufs_a=-14.0, lufs_b=-13.5)
        failures = check_thresholds(result, {"loudness": 0.5})
        assert failures == []
