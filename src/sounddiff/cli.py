"""CLI entry point for sounddiff."""

from __future__ import annotations

import sys

import click
from rich.console import Console

from sounddiff import __version__
from sounddiff.core import diff
from sounddiff.report import render
from sounddiff.threshold import check_thresholds, parse_thresholds
from sounddiff.types import OutputFormat

# Exit codes
EXIT_OK = 0
EXIT_THRESHOLD_EXCEEDED = 1
EXIT_ERROR = 2


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
@click.option(
    "--ci",
    is_flag=True,
    default=False,
    help="CI mode: exit with code 1 if thresholds are exceeded.",
)
@click.option(
    "--threshold",
    "threshold_str",
    type=str,
    default=None,
    help=(
        "Comma-separated thresholds: loudness=0.5,peak=0.3,lra=1.0,"
        "duration=0.01,correlation=0.99,spectral=3.0. "
        "Requires --ci."
    ),
)
@click.version_option(version=__version__, prog_name="sounddiff")
def main(
    file_a: str,
    file_b: str,
    output_format: str,
    output_path: str | None,
    verbose: bool,
    no_color: bool,
    ci: bool,
    threshold_str: str | None,
) -> None:
    """Compare two audio files and report what changed.

    sounddiff FILE_A FILE_B

    Compares FILE_A (reference) against FILE_B (comparison) and reports
    differences in loudness, spectral content, timing, and potential issues.
    """
    if threshold_str and not ci:
        click.echo("Error: --threshold requires --ci", err=True)
        sys.exit(EXIT_ERROR)

    if ci and not threshold_str:
        click.echo("Error: --ci requires --threshold", err=True)
        sys.exit(EXIT_ERROR)

    try:
        thresholds = parse_thresholds(threshold_str) if threshold_str else {}
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(EXIT_ERROR)

    try:
        console = Console(no_color=no_color)
        with console.status("[dim]Analyzing...[/dim]"):
            result = diff(file_a, file_b)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(EXIT_ERROR)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(EXIT_ERROR)
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(EXIT_ERROR)

    fmt = OutputFormat(output_format)
    output = render(result, fmt, output_path, no_color=no_color, verbose=verbose)

    if output_path and fmt == OutputFormat.HTML:
        click.echo(f"Report written to {output_path}")
    else:
        click.echo(output)

    if ci and thresholds:
        failures = check_thresholds(result, thresholds)
        if failures:
            click.echo("", err=True)
            click.echo("Threshold check FAILED:", err=True)
            for failure in failures:
                click.echo(f"  {failure}", err=True)
            sys.exit(EXIT_THRESHOLD_EXCEEDED)
