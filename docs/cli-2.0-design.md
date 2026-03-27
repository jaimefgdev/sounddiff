# CLI 2.0 Design

sounddiff should feel like a modern, capable CLI. Think `gh`, `uv`, Claude Code. Not a script that dumps data, but a tool with personality, rhythm, and feedback.

This document defines the full CLI experience: subcommands, visual language, voice, interaction model, and architecture.

## Principles

- **Interactive for humans, clean for machines.** Auto-detect which mode to use.
- **Opinionated but not lecturing.** State what changed, say if it matters, move on.
- **Plain language.** No jargon, no industry slang. If a non-engineer can't understand it, rewrite it.
- **Progressive disclosure.** Summary first, detail on request.
- **Every command earns its place.** No subcommands for the sake of subcommands.

## Subcommands

```
sounddiff compare <file_a> <file_b>    # The core flow (interactive report)
sounddiff inspect <file>                # Single-file analysis (loudness, metadata, issues)
sounddiff watch <file_a> <file_b>       # Re-compare on file change (v0.3.0)
sounddiff init                          # Create .sounddiffrc with defaults (v0.3.0)
sounddiff batch <directory|glob>        # Compare multiple file pairs (v0.3.0)
```

- `sounddiff` with no args shows a styled help screen with examples. Not Click's default dump.
- `sounddiff <file_a> <file_b>` (no subcommand) is an alias for `compare`. Backwards compatible.

## Visual Language

Every command follows the same rhythm:

### 1. Header

Styled brand line:

```
◉ sounddiff  comparing master_v2.wav → master_v1.wav
```

### 2. Spinner

Every analysis gets a spinner, even fast ones. Shows the tool is working.

### 3. Sections

Rich panels with borders. Dim labels, bright values. Changed values get color:
- Red for louder/worse
- Green for quieter/better
- Yellow for notable

### 4. Verdict

Every run ends with a one-line summary:

```
✓ You're good. These files sound the same.
⚠ The second file is louder and has more high end. Worth a second listen.
✗ These files are very different. Check the details below.
```

### 5. Interactive prompt

After the verdict, offer next steps:

```
What would you like to do?
  ▸ View spectral detail
    View segment timeline
    Export HTML report
    Done
```

Piped output or `--no-interactive` skips the prompt.

## Voice

sounddiff talks like a senior engineer reviewing your work. Warm, direct, helpful.

### Verdicts

- "You're good. These files sound the same."
- "The second file is louder and has more high end. Worth a second listen."
- "These files are very different. Check the details below."

### Tips (only when actionable)

- "Clipping detected. The audio is distorting at the loud parts."
- "These files use different sample rates. The comparison still works, but keep it in mind."

### Errors

- "Can't read master_v3.mp3. Make sure it's a valid audio file."
- "No files provided. Try: sounddiff compare original.wav edited.wav"

Plain language. No jargon. One sentence of context, not a lecture. `--verbose` is there for people who want more.

All copy lives in `voice.py`, not scattered through report code. Contributors improve the voice without touching analysis logic.

## Interaction Model

### Interactive mode (default when a human is at the terminal)

- Spinner during analysis
- Styled panels and verdict
- Arrow-key menu for next steps after results
- Selection prompts via `rich`

### CI mode (automatic when piped, or `--no-interactive`)

- No spinner, no prompts, no color
- Clean text output
- Exit codes: 0 = similar, 1 = different, 2 = error
- `--json` for machine parsing
- `--quiet` for just the exit code

Detection: `stdout.isatty()`. No config needed.

## Architecture

### New modules

| Module | Purpose |
|--------|---------|
| `voice.py` | Verdicts, tips, error messages. All copy lives here. |
| `interactive.py` | Prompts, menus, drill-down flows. Separated from rendering. |
| `config.py` | `.sounddiffrc` loading and defaults (v0.3.0). |

### Refactored modules

| Module | Change |
|--------|--------|
| `cli.py` | Becomes subcommand router. Click groups instead of single command. |
| `report.py` | Loses verdict/copy (moves to `voice.py`). Keeps panel layout and formatting. |

### New subcommands beyond compare

| Command | What it does |
|---------|-------------|
| `inspect` | Single-file analysis. Loudness, metadata, issues. |
| `watch` | Re-runs compare on file change (v0.3.0). |
| `init` | Creates `.sounddiffrc` with interactive prompts (v0.3.0). |
| `batch` | Directory/glob comparison with summary table (v0.3.0). |

## Milestones

### v0.2.0: The CLI 2.0 push

Ship the foundation that makes users go "oh, this is nice."

- Subcommand structure with `compare` as the north star
- Full visual overhaul: spinner, panels, verdict, interactive prompts
- `voice.py` module with plain-language copy
- Interactive/CI auto-switching
- Shell completions (bash/zsh/fish)
- `inspect` command (single-file, small and natural)
- Friendly no-args help screen

### v0.3.0: Power-user features

- `watch` mode
- `batch` comparison
- `init` and `.sounddiffrc` config
- Spectrogram visual diff
