"""Audio file loading and format detection."""

from __future__ import annotations

import atexit
import contextlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np  # noqa: TC002 (used at runtime in return type)
import soundfile as sf

from sounddiff.types import AudioMetadata

# Formats supported natively via libsndfile
NATIVE_FORMATS = {".wav", ".flac", ".ogg", ".aiff", ".aif"}

# Formats that require ffmpeg
FFMPEG_FORMATS = {".mp3", ".aac", ".m4a", ".wma", ".opus"}

# Mapping for original format display names in metadata
FORMAT_DISPLAY_NAMES: dict[str, str] = {
    ".mp3": "MP3",
    ".aac": "AAC",
    ".m4a": "AAC",
    ".wma": "WMA",
    ".opus": "Opus",
}


def _remove_if_exists(path: str) -> None:
    """Remove a file if it exists, silently ignoring missing files."""
    with contextlib.suppress(FileNotFoundError):
        os.remove(path)


def load_audio(path: str | Path) -> tuple[np.ndarray, AudioMetadata]:
    """Load an audio file and return the signal and metadata.

    Args:
        path: Path to the audio file.

    Returns:
        Tuple of (audio signal as float64 ndarray, metadata).
        Signal is always 2D: (frames, channels). Mono files get shape (frames, 1).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the format is unsupported or requires ffmpeg.
        RuntimeError: If the file cannot be read.
    """
    original_filepath = Path(path)
    read_filepath = original_filepath

    if not original_filepath.exists():
        raise FileNotFoundError(f"File not found: {original_filepath}")

    suffix = original_filepath.suffix.lower()

    if suffix in FFMPEG_FORMATS:
        if not shutil.which("ffmpeg"):
            raise ValueError(
                f"Format '{suffix}' requires ffmpeg, but it is not installed on your system. "
                "Please install ffmpeg to analyze compressed audio files."
            )

        # Create a temporary WAV file for ffmpeg to write into
        fd, temp_wav_path = tempfile.mkstemp(suffix=".wav", prefix="sounddiff_")
        os.close(fd)

        # Schedule cleanup on exit so we never leave temp files behind
        atexit.register(_remove_if_exists, temp_wav_path)

        try:
            # Transcode silently to WAV, dropping video streams (like album art) with -vn
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(original_filepath),
                    "-vn",
                    "-loglevel",
                    "error",
                    temp_wav_path,
                ],
                check=True,
                capture_output=True,
            )
            # We will read from the temp file, but keep the original path for metadata
            read_filepath = Path(temp_wav_path)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"FFmpeg failed to transcode '{path}': {e.stderr.decode('utf-8', errors='replace').strip()}"
            ) from e

    if suffix not in NATIVE_FORMATS and suffix not in FFMPEG_FORMATS:
        raise ValueError(
            f"Unsupported audio format: '{suffix}'. "
            f"Supported: {', '.join(sorted(NATIVE_FORMATS | FFMPEG_FORMATS))}"
        )

    try:
        info = sf.info(str(read_filepath))
        data, sample_rate = sf.read(str(read_filepath), dtype="float64", always_2d=True)
    except RuntimeError as e:
        raise RuntimeError(f"Cannot read audio file: {original_filepath} ({e})") from e

    if original_filepath != read_filepath:
        ext = original_filepath.suffix.lower()
        display_format = FORMAT_DISPLAY_NAMES.get(ext, ext.lstrip(".").upper())
    else:
        display_format = info.format

    try:
        file_size: int | None = original_filepath.stat().st_size
    except OSError:
        file_size = None

    metadata = AudioMetadata(
        path=str(original_filepath),
        duration=len(data) / sample_rate,
        sample_rate=sample_rate,
        channels=data.shape[1],
        bit_depth=_subtype_to_bits(info.subtype),
        format_name=display_format,
        frames=len(data),
        file_size=file_size,
    )

    return data, metadata


def _subtype_to_bits(subtype: str) -> int | None:
    """Convert soundfile subtype string to bit depth."""
    mapping: dict[str, int] = {
        "PCM_16": 16,
        "PCM_24": 24,
        "PCM_32": 32,
        "PCM_S8": 8,
        "PCM_U8": 8,
        "FLOAT": 32,
        "DOUBLE": 64,
    }
    return mapping.get(subtype)


def format_file_size(size: int | None) -> str:
    """Format a file size in bytes as a human-readable string."""
    if size is None:
        return "unknown"
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def format_duration(seconds: float) -> str:
    """Format a duration in seconds as M:SS.mmm."""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"


def format_channels(n: int) -> str:
    """Format channel count as a human-readable string."""
    if n == 1:
        return "mono"
    if n == 2:
        return "stereo"
    return f"{n}ch"