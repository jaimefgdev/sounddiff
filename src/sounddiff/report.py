"""Output formatting: terminal, JSON, and HTML reports."""

from __future__ import annotations

import io
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from sounddiff.formats import format_channels, format_duration
from sounddiff.types import DiffResult, OutputFormat, SegmentKind


def render(
    result: DiffResult,
    fmt: OutputFormat,
    output_path: str | None = None,
    no_color: bool = False,
    verbose: bool = False,
) -> str:
    """Render a DiffResult in the specified format.

    Args:
        result: The comparison result to render.
        fmt: Output format (terminal, json, html).
        output_path: Optional path to write the output file (for HTML).
        no_color: Disable colored terminal output.
        verbose: Show additional detail.

    Returns:
        The rendered output as a string.
    """
    if fmt == OutputFormat.JSON:
        return render_json(result)
    elif fmt == OutputFormat.HTML:
        html = render_html(result)
        if output_path:
            Path(output_path).write_text(html)
        return html
    else:
        return render_terminal(result, no_color=no_color, verbose=verbose)


def render_terminal(result: DiffResult, no_color: bool = False, verbose: bool = False) -> str:
    """Render a colored terminal report using rich."""
    console = Console(record=True, width=90, file=io.StringIO(), no_color=no_color)
    meta = result.metadata

    file_a = Path(meta.file_a.path).name
    file_b = Path(meta.file_b.path).name

    # Header
    console.print()
    console.print(Rule(f"[bold]sounddiff[/bold]  {file_a} [dim]\u2192[/dim]  {file_b}"))
    console.print()

    # Warnings
    for warning in result.warnings:
        console.print(f"  [yellow]! {warning}[/yellow]")
    if result.warnings:
        console.print()

    # Sections
    _print_metadata_section(console, meta)
    _print_loudness_section(console, result)
    _print_spectral_section(console, result)
    _print_segments_section(console, result)
    _print_issues_section(console, result)

    # Verdict
    _print_verdict(console, result)

    return console.export_text()


def _dim(s: str, should_dim: bool) -> str:
    """Wrap text in dim markup when unchanged."""
    return f"[dim]{s}[/dim]" if should_dim else s


def _print_metadata_section(console: Console, meta: Any) -> None:
    """Print the metadata comparison section."""
    dur_a = format_duration(meta.file_a.duration)
    dur_b = format_duration(meta.file_b.duration)
    dur_note = "" if meta.same_duration else f"[yellow]({meta.duration_delta:+.3f}s)[/yellow]"

    sr_a = f"{meta.file_a.sample_rate} Hz"
    sr_b = f"{meta.file_b.sample_rate} Hz"
    sr_note = "" if meta.same_sample_rate else "[red]MISMATCH[/red]"

    ch_a = format_channels(meta.file_a.channels)
    ch_b = format_channels(meta.file_b.channels)
    ch_note = "" if meta.same_channels else "[red]MISMATCH[/red]"

    table = Table.grid(padding=(0, 2))
    table.add_column(min_width=12)
    table.add_column(min_width=12, justify="right")
    table.add_column(width=2, justify="center")
    table.add_column(min_width=12)
    table.add_column(min_width=16)

    table.add_row(
        _dim("Duration", meta.same_duration),
        _dim(dur_a, meta.same_duration),
        _dim("\u2192", meta.same_duration),
        _dim(dur_b, meta.same_duration),
        dur_note,
    )
    table.add_row(
        _dim("Sample Rate", meta.same_sample_rate),
        _dim(sr_a, meta.same_sample_rate),
        _dim("\u2192", meta.same_sample_rate),
        _dim(sr_b, meta.same_sample_rate),
        sr_note,
    )
    table.add_row(
        _dim("Channels", meta.same_channels),
        _dim(ch_a, meta.same_channels),
        _dim("\u2192", meta.same_channels),
        _dim(ch_b, meta.same_channels),
        ch_note,
    )

    console.print(Panel(table, title="[bold]Metadata[/bold]", border_style="dim"))
    console.print()


def _print_loudness_section(console: Console, result: DiffResult) -> None:
    """Print the loudness comparison section."""
    loud = result.loudness

    table = Table.grid(padding=(0, 2))
    table.add_column(min_width=12)
    table.add_column(min_width=8, justify="right")
    table.add_column(width=2, justify="center")
    table.add_column(min_width=8, justify="right")
    table.add_column(min_width=14)

    delta_color = "red" if loud.lufs_delta > 0 else "green" if loud.lufs_delta < 0 else "white"
    table.add_row(
        "LUFS",
        f"{loud.file_a.lufs:.1f}",
        "\u2192",
        f"{loud.file_b.lufs:.1f}",
        f"[{delta_color}]({loud.lufs_delta:+.1f} dB)[/{delta_color}]",
    )

    peak_color = "red" if loud.peak_delta > 0 else "green" if loud.peak_delta < 0 else "white"
    table.add_row(
        "Peak dBTP",
        f"{loud.file_a.true_peak_dbtp:.1f}",
        "\u2192",
        f"{loud.file_b.true_peak_dbtp:.1f}",
        f"[{peak_color}]({loud.peak_delta:+.1f} dB)[/{peak_color}]",
    )

    lra_color = "yellow" if abs(loud.lra_delta) > 2 else "dim"
    table.add_row(
        "LRA",
        f"{loud.file_a.loudness_range:.1f}",
        "\u2192",
        f"{loud.file_b.loudness_range:.1f}",
        f"[{lra_color}]({loud.lra_delta:+.1f} LU)[/{lra_color}]",
    )

    console.print(Panel(table, title="[bold]Loudness[/bold]", border_style="dim"))
    console.print()


def _print_spectral_section(console: Console, result: DiffResult) -> None:
    """Print the spectral comparison section."""
    table = Table.grid(padding=(0, 2))
    table.add_column(min_width=8)
    table.add_column(min_width=18)
    table.add_column(min_width=16)

    for band in result.spectral.bands:
        hz_label = _format_hz_range(band.low_hz, band.high_hz)
        delta = band.delta_db
        color = "red" if delta > 1 else "green" if delta < -1 else "dim"
        table.add_row(
            band.name,
            f"[dim]{hz_label}[/dim]",
            f"[{color}]{delta:+.1f} dB avg[/{color}]",
        )

    console.print(Panel(table, title="[bold]Spectral[/bold]", border_style="dim"))
    console.print()


def _print_segments_section(console: Console, result: DiffResult) -> None:
    """Print the segment comparison section."""
    table = Table.grid(padding=(0, 2))
    table.add_column(min_width=16)
    table.add_column(min_width=12)
    table.add_column()

    for seg in result.temporal.segments:
        start = format_duration(seg.start_time)
        end = format_duration(seg.end_time)
        time_range = f"{start}\u2013{end}"

        if seg.kind == SegmentKind.SIMILAR:
            corr_str = f"correlation {seg.correlation:.2f}" if seg.correlation else ""
            shift_str = f", shifted {seg.time_shift:+.1f}s" if seg.time_shift else ""
            kind_str = "[dim]similar[/dim]"
            details = f"[dim]{corr_str}{shift_str}[/dim]"
        elif seg.kind == SegmentKind.ADDED:
            kind_str = "[cyan]added[/cyan]"
            details = f"[dim]new content, {seg.duration:.1f}s[/dim]"
        elif seg.kind == SegmentKind.REMOVED:
            kind_str = "[red]removed[/red]"
            details = f"[dim]{seg.duration:.1f}s[/dim]"
        elif seg.kind == SegmentKind.CHANGED:
            kind_str = "[yellow]changed[/yellow]"
            details = f"[dim]correlation {seg.correlation:.2f}[/dim]" if seg.correlation else ""
        else:
            kind_str = seg.kind.value
            details = ""

        table.add_row(f"[dim]{time_range}[/dim]", kind_str, details)

    console.print(Panel(table, title="[bold]Segments[/bold]", border_style="dim"))
    console.print()


def _print_issues_section(console: Console, result: DiffResult) -> None:
    """Print the issues section (clipping, silence)."""
    issues = result.detection
    if not issues.clips:
        return

    table = Table.grid(padding=(0, 2))
    table.add_column(min_width=10)
    table.add_column(min_width=12)
    table.add_column()

    for clip in issues.clips:
        ts = format_duration(clip.timestamp)
        ch = f"ch{clip.channel}" if clip.channel > 0 else ""
        table.add_row(
            "[red]Clipping[/red]",
            f"[dim]{clip.file_label}[/dim]",
            f"[dim]{ts}  {ch}  ({clip.sample_count} samples)[/dim]",
        )

    console.print(Panel(table, title="[bold]Issues[/bold]", border_style="red dim"))
    console.print()


def _print_verdict(console: Console, result: DiffResult) -> None:
    """Print a summary verdict at the end of the report."""
    loud = result.loudness
    spectral_max = max((abs(b.delta_db) for b in result.spectral.bands), default=0.0)
    has_clips = bool(result.detection.clips)
    has_changed = any(s.kind == SegmentKind.CHANGED for s in result.temporal.segments)
    has_added_removed = any(
        s.kind in (SegmentKind.ADDED, SegmentKind.REMOVED) for s in result.temporal.segments
    )
    lufs_delta = abs(loud.lufs_delta)

    if lufs_delta > 3 or spectral_max > 5 or has_added_removed or has_clips:
        verdict = "Major differences found."
        color = "red"
    elif lufs_delta > 1 or spectral_max > 2 or has_changed:
        verdict = "Significant differences found."
        color = "yellow"
    elif lufs_delta > 0.3 or spectral_max > 1:
        verdict = "Minor differences detected."
        color = "yellow"
    else:
        verdict = "Files are nearly identical."
        color = "green"

    console.print(Panel(f"[{color}]{verdict}[/{color}]", border_style=color))


def _format_hz_range(low: float, high: float) -> str:
    """Format a frequency range for display."""

    def fmt(hz: float) -> str:
        if hz >= 1000:
            return f"{hz / 1000:.0f}k"
        return f"{hz:.0f}"

    return f"{fmt(low)}-{fmt(high)} Hz"


def render_json(result: DiffResult) -> str:
    """Render the result as JSON."""
    data = _result_to_dict(result)
    return json.dumps(data, indent=2)


def _result_to_dict(result: DiffResult) -> dict[str, Any]:
    """Convert a DiffResult to a JSON-serializable dict."""
    d = asdict(result)
    # Convert enum values to strings
    for seg in d.get("temporal", {}).get("segments", []):
        if "kind" in seg:
            seg["kind"] = seg["kind"].value if hasattr(seg["kind"], "value") else str(seg["kind"])
    return d


def render_html(result: DiffResult) -> str:
    """Render the result as a self-contained HTML report."""
    try:
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parent.parent.parent / "templates"
        if template_dir.exists():
            env = Environment(loader=FileSystemLoader(str(template_dir)))
            template = env.get_template("report.html.j2")
            return template.render(result=result, format_duration=format_duration)
    except (ImportError, Exception):
        pass

    # Fallback: minimal HTML without jinja2
    return _render_html_fallback(result)


def _render_html_fallback(result: DiffResult) -> str:
    """Render a minimal HTML report without jinja2 templates."""
    meta = result.metadata
    file_a = Path(meta.file_a.path).name
    file_b = Path(meta.file_b.path).name

    json_data = render_json(result)

    def _css_class(delta: float) -> str:
        return "positive" if delta > 0 else "negative"

    spectral_rows = ""
    for b in result.spectral.bands:
        hz = _format_hz_range(b.low_hz, b.high_hz)
        cls = _css_class(b.delta_db)
        spectral_rows += (
            f'<tr><td>{b.name} ({hz})</td><td class="{cls}">{b.delta_db:+.1f} dB</td></tr>'
        )

    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>sounddiff: {file_a} vs {file_b}</title>\n"
        "<style>\n"
        "body { font-family: system-ui, -apple-system, sans-serif; max-width: 800px;"
        " margin: 2rem auto; padding: 0 1rem; background: #1a1a2e; color: #e0e0e0; }\n"
        "h1 { color: #fff; font-size: 1.5rem; }\n"
        "h2 { color: #8be9fd; font-size: 1.1rem; margin-top: 2rem; }\n"
        "table { border-collapse: collapse; width: 100%; margin: 0.5rem 0; }\n"
        "td, th { padding: 0.4rem 0.8rem; text-align: left;"
        " border-bottom: 1px solid #333; }\n"
        ".positive { color: #ff5555; }\n"
        ".negative { color: #50fa7b; }\n"
        "pre { background: #16213e; padding: 1rem; border-radius: 4px;"
        " overflow-x: auto; font-size: 0.85rem; }\n"
        "</style>\n</head>\n<body>\n"
        f"<h1>sounddiff: {file_a} vs {file_b}</h1>\n\n"
        "<h2>Loudness</h2>\n<table>\n"
        f"<tr><td>LUFS</td><td>{result.loudness.file_a.lufs:.1f}</td>"
        f"<td>{result.loudness.file_b.lufs:.1f}</td>"
        f'<td class="{_css_class(result.loudness.lufs_delta)}">'
        f"{result.loudness.lufs_delta:+.1f} dB</td></tr>\n"
        f"<tr><td>Peak dBTP</td><td>{result.loudness.file_a.true_peak_dbtp:.1f}</td>"
        f"<td>{result.loudness.file_b.true_peak_dbtp:.1f}</td>"
        f'<td class="{_css_class(result.loudness.peak_delta)}">'
        f"{result.loudness.peak_delta:+.1f} dB</td></tr>\n"
        f"<tr><td>LRA</td><td>{result.loudness.file_a.loudness_range:.1f}</td>"
        f"<td>{result.loudness.file_b.loudness_range:.1f}</td>"
        f"<td>{result.loudness.lra_delta:+.1f} LU</td></tr>\n"
        "</table>\n\n"
        "<h2>Spectral</h2>\n<table>\n"
        f"{spectral_rows}\n"
        "</table>\n\n"
        f"<h2>Raw Data (JSON)</h2>\n<pre>{json_data}</pre>\n\n"
        "</body>\n</html>"
    )
