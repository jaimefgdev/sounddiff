"""Tests for audio file loading and format detection."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from sounddiff.formats import format_channels, format_duration, format_file_size, load_audio

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestLoadAudio:
    def test_loads_stereo_wav(self) -> None:
        data, meta = load_audio(FIXTURES_DIR / "sine_a.wav")
        assert data.shape[1] == 2
        assert meta.channels == 2
        assert meta.sample_rate == 48000
        assert meta.format_name == "WAV"

    def test_loads_mono_wav(self) -> None:
        data, meta = load_audio(FIXTURES_DIR / "mono.wav")
        assert data.shape[1] == 1
        assert meta.channels == 1

    def test_returns_float64(self) -> None:
        data, _ = load_audio(FIXTURES_DIR / "sine_a.wav")
        assert data.dtype == np.float64

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_audio("nonexistent.wav")

    def test_unsupported_format(self, tmp_path: Path) -> None:
        fake = tmp_path / "test.xyz"
        fake.write_text("not audio")
        with pytest.raises(ValueError, match="Unsupported"):
            load_audio(fake)

    def test_mp3_without_ffmpeg(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        fake = tmp_path / "test.mp3"
        fake.write_text("not really mp3")
        with pytest.raises(ValueError, match="ffmpeg"):
            load_audio(fake)

    def test_duration_is_positive(self) -> None:
        _, meta = load_audio(FIXTURES_DIR / "sine_a.wav")
        assert meta.duration > 0

    def test_frames_matches_data_length(self) -> None:
        data, meta = load_audio(FIXTURES_DIR / "sine_a.wav")
        assert meta.frames == len(data)

    def test_file_size_is_populated(self) -> None:
        _, meta = load_audio(FIXTURES_DIR / "sine_a.wav")
        assert meta.file_size is not None
        assert meta.file_size > 0


class TestFormatFileSize:
    def test_bytes(self) -> None:
        assert format_file_size(512) == "512 B"

    def test_kilobytes(self) -> None:
        assert format_file_size(2048) == "2.0 KB"

    def test_megabytes(self) -> None:
        assert format_file_size(5 * 1024 * 1024) == "5.0 MB"

    def test_none(self) -> None:
        assert format_file_size(None) == "unknown"


class TestFormatDuration:
    def test_zero(self) -> None:
        assert format_duration(0) == "0:00.000"

    def test_seconds_only(self) -> None:
        assert format_duration(5.123) == "0:05.123"

    def test_minutes_and_seconds(self) -> None:
        assert format_duration(125.5) == "2:05.500"

    def test_exact_minute(self) -> None:
        assert format_duration(60.0) == "1:00.000"


class TestFormatChannels:
    def test_mono(self) -> None:
        assert format_channels(1) == "mono"

    def test_stereo(self) -> None:
        assert format_channels(2) == "stereo"

    def test_multichannel(self) -> None:
        assert format_channels(6) == "6ch"
