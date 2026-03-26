"""Generate deterministic test audio fixtures.

Creates WAV files in tests/fixtures/ for use in the test suite.
All audio is generated from fixed seeds so tests are reproducible.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"
SAMPLE_RATE = 48000


def main() -> None:
    """Generate all test audio fixtures."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    generate_sine_pair()
    generate_loudness_pair()
    generate_clipping()
    generate_silence()
    generate_different_lengths()
    generate_mono()

    print(f"Generated test fixtures in {FIXTURES_DIR}")


def generate_sine_pair() -> None:
    """Two identical 440Hz sine waves. Should show no differences."""
    duration = 2.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    sine = 0.5 * np.sin(2 * np.pi * 440 * t)
    stereo = np.column_stack([sine, sine])

    sf.write(str(FIXTURES_DIR / "sine_a.wav"), stereo, SAMPLE_RATE, subtype="PCM_16")
    sf.write(str(FIXTURES_DIR / "sine_b.wav"), stereo, SAMPLE_RATE, subtype="PCM_16")


def generate_loudness_pair() -> None:
    """Two sine waves with different amplitudes. Tests loudness comparison."""
    duration = 3.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

    # Quieter version
    quiet = 0.3 * np.sin(2 * np.pi * 440 * t)
    stereo_quiet = np.column_stack([quiet, quiet])

    # Louder version with some high-frequency content
    loud = 0.7 * np.sin(2 * np.pi * 440 * t) + 0.2 * np.sin(2 * np.pi * 8000 * t)
    stereo_loud = np.column_stack([loud, loud])

    sf.write(str(FIXTURES_DIR / "quiet.wav"), stereo_quiet, SAMPLE_RATE, subtype="PCM_16")
    sf.write(str(FIXTURES_DIR / "loud.wav"), stereo_loud, SAMPLE_RATE, subtype="PCM_16")


def generate_clipping() -> None:
    """A signal with intentional clipping. Tests clipping detection."""
    duration = 2.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

    # Clean signal
    clean = 0.5 * np.sin(2 * np.pi * 440 * t)

    # Clipped signal: amplify beyond 1.0 then clip
    clipped = 1.5 * np.sin(2 * np.pi * 440 * t)
    clipped = np.clip(clipped, -1.0, 1.0)

    stereo_clean = np.column_stack([clean, clean])
    stereo_clipped = np.column_stack([clipped, clipped])

    sf.write(str(FIXTURES_DIR / "clean.wav"), stereo_clean, SAMPLE_RATE, subtype="PCM_16")
    sf.write(str(FIXTURES_DIR / "clipped.wav"), stereo_clipped, SAMPLE_RATE, subtype="PCM_16")


def generate_silence() -> None:
    """A signal with a silent region inserted. Tests silence detection."""
    duration = 3.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

    # Continuous signal
    continuous = 0.5 * np.sin(2 * np.pi * 440 * t)

    # Signal with 0.5s of silence in the middle
    with_silence = continuous.copy()
    silence_start = int(1.0 * SAMPLE_RATE)
    silence_end = int(1.5 * SAMPLE_RATE)
    with_silence[silence_start:silence_end] = 0.0

    stereo_continuous = np.column_stack([continuous, continuous])
    stereo_silence = np.column_stack([with_silence, with_silence])

    sf.write(
        str(FIXTURES_DIR / "continuous.wav"), stereo_continuous, SAMPLE_RATE, subtype="PCM_16"
    )
    sf.write(str(FIXTURES_DIR / "with_silence.wav"), stereo_silence, SAMPLE_RATE, subtype="PCM_16")


def generate_different_lengths() -> None:
    """Two signals with different durations. Tests segment detection."""
    t_short = np.linspace(0, 2.0, int(SAMPLE_RATE * 2.0), endpoint=False)
    t_long = np.linspace(0, 3.0, int(SAMPLE_RATE * 3.0), endpoint=False)

    short = 0.5 * np.sin(2 * np.pi * 440 * t_short)
    long = 0.5 * np.sin(2 * np.pi * 440 * t_long)

    stereo_short = np.column_stack([short, short])
    stereo_long = np.column_stack([long, long])

    sf.write(str(FIXTURES_DIR / "short.wav"), stereo_short, SAMPLE_RATE, subtype="PCM_16")
    sf.write(str(FIXTURES_DIR / "long.wav"), stereo_long, SAMPLE_RATE, subtype="PCM_16")


def generate_mono() -> None:
    """A mono signal for testing channel handling."""
    duration = 2.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    mono = 0.5 * np.sin(2 * np.pi * 440 * t)

    sf.write(str(FIXTURES_DIR / "mono.wav"), mono, SAMPLE_RATE, subtype="PCM_16")


if __name__ == "__main__":
    main()
