"""CLI entry point for sounddiff."""

from __future__ import annotations

import pathlib
import sys

import click
import soundfile as sf
from rich.console import Console
from rich.progress import Progress

from sounddiff import __version__
from sounddiff.core import diff
from sounddiff.formats import FFMPEG_FORMATS
from sounddiff.report import render
from sounddiff.types import OutputFormat

_PROGRESS_THRESHOLD = 30


@click.command()
@click.argument("file_a", type=click.Path(exists=True))
@click.argument("file_b", type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["terminal", "json", "html"]),
    default="terminal",
    help="Output format.",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(),
    default=None,
    help="Write output to a file (useful with --format html).",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Show additional detail.",
)
@click.option(
    "--no-color",
    is_flag=True,
    default=False,
    help="Disable colored terminal output.",
)
@click.version_option(version=__version__, prog_name="sounddiff")
def main(
    file_a: str,
    file_b: str,
    output_format: str,
    output_path: str | None,
    verbose: bool,
    no_color: bool,
) -> None:
    """Compare two audio files and report what changed.

    sounddiff FILE_A FILE_B

    Compares FILE_A (reference) against FILE_B (comparison) and reports
    differences in loudness, spectral content, timing, and potential issues.
    """
    # Best-effort duration probe: if sf.info() fails for either file,
    # skip the progress bar and let diff() raise the proper error message.
    show_progress = False
    try:
        # Skip the probe for ffmpeg-backed formats; sf.info() can't read them
        # and diff() will handle any format errors with a clear message.
        if (
            pathlib.Path(file_a).suffix.lower() not in FFMPEG_FORMATS
            and pathlib.Path(file_b).suffix.lower() not in FFMPEG_FORMATS
        ):
            info_a = sf.info(file_a)
            info_b = sf.info(file_b)
            longest = max(
                info_a.frames / info_a.samplerate,
                info_b.frames / info_b.samplerate,
            )
            show_progress = longest > _PROGRESS_THRESHOLD
    except Exception:
        pass

    try:
        if show_progress:
            with Progress(
                transient=True,
                console=Console(no_color=no_color),
            ) as progress:
                progress.add_task("Analyzing audio files...", total=None)
                result = diff(file_a, file_b)
        else:
            result = diff(file_a, file_b)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    fmt = OutputFormat(output_format)
    output = render(result, fmt, output_path, no_color=no_color)

    if output_path and fmt == OutputFormat.HTML:
        click.echo(f"Report written to {output_path}")
    else:
        click.echo(output)
