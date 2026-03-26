"""CLI entry point for sounddiff."""

from __future__ import annotations

import sys

import click

from sounddiff import __version__
from sounddiff.core import diff
from sounddiff.report import render
from sounddiff.types import OutputFormat


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
    try:
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
