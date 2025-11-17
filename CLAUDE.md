# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**par-term-emu-tui-rust** is a modern terminal emulator TUI built with Textual and par-term-emu-core-rust (a Rust terminal emulation backend). This is a Python TUI application that wraps high-performance Rust terminal emulation with rich UI features.

**Key Stack:**
- Python 3.12+ (requires 3.14 for development)
- Textual 6.6.0+ (TUI framework)
- par-term-emu-core-rust 0.2.3+ (Rust backend - local dependency in ../par-term-emu-core-rust)
- uv for package management

## Development Commands

### Setup
```bash
# Initial setup
uv sync                    # Install all dependencies

# Pre-commit hooks
make pre-commit-install    # Install git hooks
make pre-commit-run        # Run hooks manually
```

### Running the Application
```bash
make run                   # Run TUI (clears debug logs first)
make themes                # List available themes

# Direct execution
uv run par-term-emu-tui-rust
uv run ptr                 # Alias
```

### Code Quality (CRITICAL - must pass before commits)
```bash
make checkall              # Run ALL checks (format, lint, typecheck) - USE THIS
make lint                  # Ruff format + check + pyright
make fmt                   # Ruff format only

# Individual tools
uv run ruff format .
uv run ruff check --fix .
uv run pyright .
```

### Testing
```bash
uv run pytest              # Run all tests (10s timeout per test)
uv run pytest tests/test_foo.py          # Run specific test file
uv run pytest tests/test_foo.py::test_bar # Run specific test
```

**IMPORTANT:** When tests fail, investigate if the issue is:
1. A real bug in the code (fix the code)
2. A test implementation problem (fix the test)

Don't blindly make tests pass - understand what they're testing.

### Debugging
```bash
make debug                 # Run with DEBUG_LEVEL=2 (info)
make debug-verbose         # Run with DEBUG_LEVEL=3 (debug)
make debug-trace           # Run with DEBUG_LEVEL=4 (trace - HUGE logs!)
make debug-tail            # Tail debug logs in real-time
make debug-view            # View debug logs with less
make debug-clear           # Clear debug log files

# Debug logs written to:
# - /tmp/par_term_emu_core_rust_debug_rust.log
# - /tmp/par_term_emu_core_rust_debug_python.log
```

**WARNING:** Never run the TUI application yourself - it will corrupt your terminal session. Always rely on the user to test TUI behavior.

### Textual Development Tools
```bash
uv run textual keys        # Show key name helper
uv run textual borders     # Show border styles
uv run textual colors      # Show color palette
```

## Architecture

### High-Level Structure

```
Application Layer (TerminalApp in app.py)
    ↓ composes
Terminal Widget Layer (TerminalWidget in terminal_widget/terminal_widget.py)
    ↓ wraps
Rust Backend (PtyTerminal from par-term-emu-core-rust)
    ↓ manages
PTY + Shell Process
```

### Key Components

**Main Application (`app.py`):**
- TerminalApp: Top-level Textual App
- Composes: Header, TerminalWidget, StatusBar, FlashLine, Footer
- Handles: App-level bindings, screenshots, auto-quit, config loading
- Message handlers: DirectoryChanged, TitleChanged, Flash

**Terminal Widget (`terminal_widget/terminal_widget.py`):**
- Core widget wrapping PtyTerminal (Rust backend)
- 1480 lines - the heart of the application
- Manages: PTY lifecycle, polling, rendering, input, mouse, selection
- Uses manager composition pattern (see below)

**Manager Pattern (in `terminal_widget/`):**
- `rendering.py`: Renderer - Line-by-line rendering with atomic snapshots
- `selection.py`: SelectionManager - Text selection state and operations
- `clipboard.py`: ClipboardManager - Cross-platform clipboard operations
- `screenshot.py`: ScreenshotManager - Screenshot capture to multiple formats
- `theme_manager.py`: Apply themes to terminal

**Configuration (`config.py`):**
- TuiConfig dataclass with 30+ configuration options
- XDG-compliant storage: `~/.config/par-term-emu-tui-rust/config.yaml`
- Loads with defaults, saves user preferences

**Themes (`themes.py`):**
- 11 built-in themes (dark-background, solarized-dark, tango-dark, etc.)
- Custom themes in `~/.config/par-term-emu-tui-rust/themes/`
- Theme dataclass: palette (16 colors), bg, fg, cursor, selection, links, etc.

**Messages (`messages.py`):**
- Custom Textual message types for inter-widget communication
- Flash (notifications), DirectoryChanged (OSC 7), TitleChanged (OSC 0/1/2)

### Threading Model (CRITICAL)

**PTY Reader Thread (Rust):**
- Runs in background reading PTY output
- Updates atomic counter (`update_generation`)
- Never touches UI directly

**Textual Event Loop (Main Python Thread):**
- `_poll_updates()` runs every 16ms via set_interval()
- Checks generation counter, schedules debounced refresh (5ms delay)
- All rendering happens here
- All event handlers (mouse, keyboard) run here

**Key Design Patterns:**
1. **Atomic Snapshot Pattern**: Create frame snapshot before rendering to prevent mid-frame screen switches
2. **Generation Tracking**: Atomic counter to detect changes without polling entire screen
3. **Debounced Refresh**: Batch rapid updates into single render cycle
4. **Manager Composition**: Feature isolation in separate manager classes
5. **Reactive Attributes**: Textual reactive system for terminal_cols/terminal_rows

### Critical Files to Understand

**For rendering bugs:**
- `terminal_widget/rendering.py` - Renderer.prepare_frame(), render_line()
- `terminal_widget/terminal_widget.py` - _poll_updates(), _do_refresh()

**For selection/clipboard:**
- `terminal_widget/selection.py` - SelectionManager
- `terminal_widget/clipboard.py` - ClipboardManager

**For configuration:**
- `config.py` - TuiConfig dataclass
- See docs/CONFIG_REFERENCE.md for all options

**For themes:**
- `themes.py` - Theme definitions
- `terminal_widget/theme_manager.py` - apply_theme()

## Dependency: par-term-emu-core-rust

This project depends on a **local Rust package** at `../par-term-emu-core-rust`:

```toml
[tool.uv.sources]
par-term-emu-core-rust = { path = "../par-term-emu-core-rust" }
```

**Important implications:**
- Changes to par-term-emu-core-rust require rebuilding that package
- PtyTerminal API is defined in the Rust package
- Debug logs for Rust code go to `/tmp/par_term_emu_core_rust_debug_rust.log`

## Code Standards

### Python Standards (enforced by ruff + pyright)
- Python 3.14 syntax
- Type annotations required (all functions, methods)
- Google-style docstrings
- Built-in generics: `list`, `dict`, not `List`, `Dict`
- Union operator: `str | None`, not `Optional[str]`
- Line length: 120 characters
- File I/O: Always specify `encoding='utf-8'`
- Path operations: Use `pathlib.Path`

### Ruff Configuration
- Target: Python 3.14
- Line length: 120
- Extensive rule selection (see pyproject.toml lines 93-150)
- Ignores: COM812, PLR*, TRY300/301, etc.

### Pyright Configuration
- Type checking: standard mode
- Python version: 3.14
- Includes: `src/`
- Excludes: `debug_scripts/`, `.venv/`, etc.

### Testing
- Default timeout: 10 seconds per test
- Test paths: `tests/`
- Use pytest-timeout

## Common Development Tasks

### Adding a New Feature
1. Check if it requires config changes (add to TuiConfig in config.py)
2. Determine which manager it belongs to (or create new manager)
3. Add message types if needed (messages.py)
4. Update key bindings if needed (BINDINGS in terminal_widget.py or app.py)
5. Update documentation (docs/ folder)
6. Run `make checkall` before committing

### Debugging Rendering Issues
1. Enable debug logging: `make debug-verbose`
2. Check logs in /tmp/par_term_emu_core_rust_debug_*.log
3. Key methods to investigate:
   - Renderer.prepare_frame() - atomic snapshot creation
   - Renderer.render_line() - line rendering
   - TerminalWidget._poll_updates() - update detection
   - TerminalWidget._do_refresh() - refresh execution

### Debugging Selection/Clipboard
1. Check SelectionManager state (start, end, selecting)
2. Verify frame_snapshot is being passed correctly
3. Check ClipboardManager.copy_to_clipboard() success/failure
4. On Linux, verify xclip/xsel for PRIMARY selection

### Testing the TUI
**NEVER run the TUI directly in Claude Code** - it will corrupt the terminal.
Instead:
- Use `--auto-quit` flag for automated testing
- Use `--screenshot` with `--auto-quit` to capture output
- Ask user to test interactively

Example automated test:
```bash
uv run par-term-emu-tui-rust --auto-quit 2 --screenshot 1
```

## Documentation

Comprehensive documentation in `docs/`:
- **ARCHITECTURE.md**: Detailed system design (1319 lines - THE reference)
- **CONFIG_REFERENCE.md**: All configuration options
- **DEBUG.md**: Debugging guide
- **FEATURES.md**: Feature descriptions
- **KEY_BINDINGS.md**: Keyboard shortcuts
- **QUICK_START.md**: Getting started
- **USAGE.md**: Command-line usage
- **TROUBLESHOOTING.md**: Common issues

**When making changes:**
- Update relevant docs in docs/
- Follow DOCUMENTATION_STYLE_GUIDE.md
- Keep ARCHITECTURE.md in sync with code

## Important Constraints

1. **Never run the TUI yourself** - it corrupts terminal sessions
2. **Always run `make checkall`** before committing
3. **Understand test failures** - don't blindly fix tests, investigate bugs
4. **Respect threading model** - all UI updates in event loop only
5. **Use atomic snapshots** - prevents rendering corruption
6. **Local Rust dependency** - changes require rebuilding par-term-emu-core-rust
7. **XDG compliance** - config in ~/.config/par-term-emu-tui-rust/

## Entry Points

**CLI entry points defined in pyproject.toml:**
```toml
[project.scripts]
par-term-emu-tui-rust = "par_term_emu_tui_rust.app:main"
ptr = "par_term_emu_tui_rust.app:main"
```

**Main function:** `src/par_term_emu_tui_rust/app.py:main()`
- Parses CLI arguments
- Loads config
- Creates TerminalApp
- Runs Textual app

## Git Workflow

Pre-commit hooks (via pre-commit package):
- Runs ruff format
- Runs ruff check
- Runs pyright
- Runs pytest

**If hooks modify files:**
```bash
git add -A              # Restage modified files
git commit -m "message" # Commit again
```

## Quick Reference Card

```bash
# Development cycle
uv sync                 # Install deps
make checkall           # Quality checks
make run                # Test locally (if safe)
make debug-verbose      # Debug with logs

# Before committing
make checkall           # MUST pass
uv run pytest           # MUST pass

# Common debugging
make debug-tail         # Watch logs
uv run textual keys     # Key name helper
```

## Related Resources

- [Textual Documentation](https://textual.textualize.io/)
- [par-term-emu-core-rust](https://github.com/paulrobello/par-term-emu-core-rust)
- [XDG Base Directory Spec](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- Never run the tui, ask the user to run it
- the sister project par-term-emu-core-rust is located locally in ../par-term-emu-core-rust and on github in https://github.com/paulrobello/par-term-emu-core-rust
- *IMPORTANT* NEVER RUN THE TUI IT WILL CORRUPT YOUR TERMINAL, ASK THE USER TO RUN IT!
