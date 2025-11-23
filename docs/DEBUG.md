# Debugging par-term-emu-tui-rust

This document describes the comprehensive debugging infrastructure for par-term-emu-tui-rust, designed to help diagnose issues like the TUI rendering corruption.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Debug Levels](#debug-levels)
- [Debug Levels Explained](#debug-levels-explained)
- [What Gets Logged](#what-gets-logged)
  - [Rust Side (Core Terminal Emulation)](#rust-side-core-terminal-emulation)
  - [Python Side (TUI Widget)](#python-side-tui-widget)
- [Using Debug Snapshots from Python](#using-debug-snapshots-from-python)
- [Debugging the TUI Corruption Issue](#debugging-the-tui-corruption-issue)
- [Running the TUI with Debug Mode](#running-the-tui-with-debug-mode)
  - [Using Makefile (Recommended)](#using-makefile-recommended)
  - [Manual Execution](#manual-execution)
  - [Managing Debug Logs](#managing-debug-logs)
- [Tips and Best Practices](#tips-and-best-practices)
- [Performance Impact](#performance-impact)
- [Troubleshooting the Debug System](#troubleshooting-the-debug-system)
- [Advanced Usage](#advanced-usage)
- [FAQ](#faq)
- [Which Log Should I Check?](#which-log-should-i-check)
- [Related Files](#related-files)
- [Makefile Debug Targets](#makefile-debug-targets)
- [See Also](#see-also)

## Overview

The debugging system provides extensive logging capabilities across Rust and Python components. There are **three separate log sources**:

1. **Rust core debug logs**: `/tmp/par_term_emu_core_rust_debug_rust.log` (Unix/macOS) or `%TEMP%\par_term_emu_core_rust_debug_rust.log` (Windows)
   - Terminal emulation, VT parsing, PTY operations
   - Controlled by `DEBUG_LEVEL` environment variable (0-4)
   - From par-term-emu-core-rust Rust backend

2. **Python core debug logs**: `/tmp/par_term_emu_debug_python.log` (Unix/macOS) or `%TEMP%\par_term_emu_debug_python.log` (Windows)
   - Core Python bindings debug output
   - Controlled by `DEBUG_LEVEL` environment variable (0-4)
   - From par-term-emu-core-rust Python module

3. **Python TUI application logs**: `debug_logs/terminal_debug_YYYYMMDD_HHMMSS.log`
   - TUI application logic, widget lifecycle, user interactions
   - Enabled via `--debug` CLI flag
   - Created in current working directory
   - Timestamped for multiple debugging sessions

This three-layer separation makes it easier to identify whether issues originate in:
- The core terminal emulation layer (Rust)
- The Python bindings layer (Python core)
- The TUI application layer (Python TUI)

## Quick Start

```bash
# Set debug level (0-4) and run application with debug mode enabled
export DEBUG_LEVEL=3
uv run par-term-emu-tui-rust --debug

# Or use Makefile shortcuts (recommended)
make debug          # DEBUG_LEVEL=2 (info)
make debug-verbose  # DEBUG_LEVEL=3 (debug)
make debug-trace    # DEBUG_LEVEL=4 (trace)

# View debug output in real-time (all three log sources)
tail -f /tmp/par_term_emu_core_rust_debug_rust.log \
        /tmp/par_term_emu_debug_python.log \
        debug_logs/terminal_debug_*.log

# Or view individually
tail -f /tmp/par_term_emu_core_rust_debug_rust.log    # Rust core only
tail -f /tmp/par_term_emu_debug_python.log  # Python core only
tail -f debug_logs/terminal_debug_*.log                # Python TUI application only

# Or after the fact
less /tmp/par_term_emu_core_rust_debug_rust.log
less /tmp/par_term_emu_debug_python.log
less debug_logs/terminal_debug_*.log

# Or use Makefile shortcuts
make debug-tail  # Tail Rust and Python core logs
make debug-view  # View Rust and Python core logs with less
```

## Debug Levels

The `DEBUG_LEVEL` environment variable controls verbosity:

| Level | Name  | Description | What's Logged |
|-------|-------|-------------|---------------|
| 0     | OFF   | No debugging (default) | Nothing |
| 1     | ERROR | Errors only | Critical issues, corruption detection |
| 2     | INFO  | Informational | Screen switches, device queries, widget lifecycle |
| 3     | DEBUG | Detailed debugging | VT sequences, generation tracking, render calls |
| 4     | TRACE | Maximum verbosity | Every operation, full content, buffer snapshots |

## Debug Levels Explained

### Level 1: ERROR
Logs only critical issues:
- Screen corruption detection (escape sequence fragments in output)
- Fatal errors in PTY operations
- Unexpected state transitions

**Use when:** You want minimal logging and only care about actual problems.

### Level 2: INFO
Adds informational logging:
- Screen buffer switches (primary ↔ alternate)
- Device query requests and responses
- Widget lifecycle events (mount, unmount, resize)
- Mode changes (mouse tracking, bracketed paste, etc.)

**Use when:** Investigating screen switching issues or device query handling.

### Level 3: DEBUG
Adds detailed operation logging:
- All VT sequences (CSI, OSC, ESC)
- Control character execution (LF, CR, HT, etc.)
- Generation counter changes
- Render calls with generation numbers
- Terminal state snapshots
- PTY read/write operations

**Use when:** Debugging rendering issues or tracking down where corruption originates.

### Level 4: TRACE
Maximum verbosity logging:
- Every character printed with position
- Cursor movements
- Grid operations (scroll, insert, delete)
- Full buffer snapshots
- Rendered line content
- Every get_line_cells() call

**Use when:** You need a complete trace of all operations. **Warning:** Generates massive log files!

## What Gets Logged

### Rust Side (Core Terminal Emulation)

#### VT Sequence Processing
```text
[timestamp] [DEBUG] [VT_INPUT] len=27 hex=[1b 5b 33 31 6d ...] ascii=[..[31m...]
[timestamp] [DEBUG] [CSI] CSI m  (params=[31])
[timestamp] [DEBUG] [OSC] OSC 0;Window Title
[timestamp] [DEBUG] [ESC] ESC 7
```

#### Screen Buffer Operations
```text
[timestamp] [INFO ] [SCREEN_SWITCH] switched to ALTERNATE screen (use_alt_screen)
[timestamp] [DEBUG] [SCROLL] up 1 lines in region [0..23]
[timestamp] [DEBUG] [GRID_OP] insert_lines: inserted 2 lines at row 5
```

#### Device Queries
```text
[timestamp] [INFO ] [DEVICE_QUERY] query='CSI 6 n' response=[1b 5b 31 3b 31 52]
```

#### PTY Operations
```text
[timestamp] [TRACE] [PTY_READ] read 1024 bytes from PTY
[timestamp] [DEBUG] [PTY_WRITE] wrote 3 bytes: [1b 5b 41]
```

#### Generation Tracking
```text
[timestamp] [DEBUG] [GENERATION] counter changed: 42 -> 43 (PTY read)
```

#### Buffer Snapshots
```text
--------------------------------------------------------------------------------
BUFFER SNAPSHOT: After corruption (80x24)
--------------------------------------------------------------------------------
Grid: 80x24 (scrollback: 15/10000)
────────────────────────────────────────────────────────────────────────────────
  0: |  ○,○,○;27m;18;18;18m                                                    |
  1: |┌─────────────────────────────────────────────────────────────────────────┐|
  2: |│ Application Output                                                      │|
...
```

### Python Side (TUI Widget)

#### Widget Lifecycle
```text
[timestamp] [INFO ] [LIFECYCLE] widget=terminal mount size=(80x24)
[timestamp] [INFO ] [LIFECYCLE] widget=terminal resize 80x24 -> 100x30
[timestamp] [INFO ] [LIFECYCLE] widget=terminal unmount
```

#### Render Operations
```text
[timestamp] [DEBUG] [RENDER] widget=terminal line=0 gen=156
[timestamp] [DEBUG] [RENDER] WARNING: rendering with stale gen (render=157, last=156)
[timestamp] [TRACE] [RENDER_CONTENT] widget=terminal line=0 content=[Hello World!]
```

#### Generation Tracking
```text
[timestamp] [DEBUG] [GENERATION] widget=terminal 155 -> 156 (CHANGED)
[timestamp] [TRACE] [POLL] refreshed widget terminal
```

#### Screen Corruption Detection
```text
[timestamp] [ERROR] [CORRUPTION] widget=terminal line=0 suspicious_content=[○,○,○;27m;18;18]
```

## Using Debug Snapshots from Python

The terminal exposes snapshot methods for manual investigation (these methods are available on both `Terminal` and `PtyTerminal` instances, but they do NOT write to the debug log files - they return strings for programmatic use):

### Taking Snapshots

```python
from par_term_emu_core_rust import Terminal

term = Terminal(80, 24)
term.process(b"Hello\n")

# Get a formatted view of the current buffer (returns string)
snapshot = term.debug_snapshot_buffer()
print(snapshot)

# Get primary buffer explicitly (returns string)
primary = term.debug_snapshot_primary()

# Get alternate buffer explicitly (returns string)
alt = term.debug_snapshot_alt()

# Get terminal state as a dictionary (returns dict)
info = term.debug_info()
print(info)
# {
#     'size': '80x24',
#     'cursor_pos': '(5,0)',
#     'cursor_visible': 'true',
#     'alt_screen_active': 'false',
#     'scrollback_len': '0',
#     'title': ''
# }
```

### Using with PtyTerminal

```python
from par_term_emu_core_rust import PtyTerminal

term = PtyTerminal(80, 24)
term.spawn_shell()

# Same snapshot methods available
snapshot = term.debug_snapshot_buffer()
info = term.debug_info()

# PtyTerminal adds extra info
print(info['pty_running'])  # 'true'
print(info['update_generation'])  # '42'
```

**Note**: These snapshot methods return data for programmatic inspection. To enable automatic debug logging to the log files, set the `DEBUG_LEVEL` environment variable as described in the Quick Start section.

## Debugging the TUI Corruption Issue

Based on the handoff.md, here's how to use the debug system to investigate:

### Step 1: Reproduce with Level 2 Logging

```bash
export DEBUG_LEVEL=2
uv run par-term-emu-tui-rust
# Inside TUI, run: python -m textual
# Wait for corruption to appear
```

This will show:
- Screen switches (primary ↔ alternate)
- Device query responses
- Widget lifecycle events

**Look for:** Unusual screen switch patterns or device query timing.

### Step 2: Enable Level 3 for Detailed Trace

```bash
export DEBUG_LEVEL=3
uv run par-term-emu-tui-rust
# Reproduce the corruption
```

This adds:
- All VT sequences being processed
- Render calls with generation numbers
- Stale generation warnings

**Look for:**
- Escape sequences that look malformed
- Render calls with mismatched generation numbers
- Unusual sequence patterns before corruption

### Step 3: Maximum Verbosity for Deep Dive

```bash
export DEBUG_LEVEL=4
uv run par-term-emu-tui-rust
# Reproduce (will generate large log file)
```

**Warning:** Level 4 creates massive log files. Use for short reproduction sessions only.

**Look for:**
- The exact sequence of operations leading to corruption
- Buffer content at the moment corruption appears
- Timing patterns in render calls

### Step 4: Analyze the Log

```bash
# Find corruption events (check both logs)
grep CORRUPTION /tmp/par_term_emu_core_rust_debug_rust.log
grep CORRUPTION /tmp/par_term_emu_debug_python.log

# Find screen switches (Rust log - core terminal operations)
grep SCREEN_SWITCH /tmp/par_term_emu_core_rust_debug_rust.log

# Find device queries (Rust log - VT sequence handling)
grep DEVICE_QUERY /tmp/par_term_emu_core_rust_debug_rust.log

# Find render warnings (Python log - TUI rendering)
grep "WARNING" /tmp/par_term_emu_debug_python.log

# Get context around a specific time (both logs)
grep -A 10 -B 10 "CORRUPTION" /tmp/par_term_emu_core_rust_debug_rust.log
grep -A 10 -B 10 "CORRUPTION" /tmp/par_term_emu_debug_python.log
```

## Running the TUI with Debug Mode

### Using Makefile (Recommended)

The Makefile provides convenient shortcuts for running with different debug levels:

```bash
# Run with DEBUG_LEVEL=2 (info) + TUI logging
make debug

# Run with DEBUG_LEVEL=3 (debug) + TUI logging
make debug-verbose

# Run with DEBUG_LEVEL=4 (trace) + TUI logging - WARNING: huge logs
make debug-trace

# Clear all debug logs before running
make debug-clear

# View debug logs in real-time (Rust + Python core only)
make debug-tail

# View debug logs with less (Rust + Python core only)
make debug-view
```

### Manual Execution

You can also run directly with environment variables and CLI flags:

```bash
# Run TUI with core debug level 2 (info) + TUI application logging
DEBUG_LEVEL=2 uv run par-term-emu-tui-rust --debug

# Run TUI with core debug level 3 (debug) + TUI application logging
DEBUG_LEVEL=3 uv run par-term-emu-tui-rust --debug

# Run TUI with core debug level 4 (trace) + TUI application logging - WARNING: huge logs
DEBUG_LEVEL=4 uv run par-term-emu-tui-rust --debug

# Run TUI with only application logging (no core debug logs)
uv run par-term-emu-tui-rust --debug

# Run TUI with only core debug logs (no application logging)
DEBUG_LEVEL=3 uv run par-term-emu-tui-rust
```

### Managing Debug Logs

```bash
# Clear core debug log files (Rust + Python)
rm -f /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_debug_python.log

# Clear TUI application logs
rm -rf debug_logs/

# Clear all debug logs
make debug-clear

# View core debug logs in real-time
tail -f /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_debug_python.log

# View TUI application logs in real-time
tail -f debug_logs/terminal_debug_*.log

# View core debug logs with less
less /tmp/par_term_emu_core_rust_debug_rust.log
less /tmp/par_term_emu_debug_python.log

# View TUI application logs with less
less debug_logs/terminal_debug_*.log
```

## Tips and Best Practices

### 1. Start with Lower Levels
Begin with `DEBUG_LEVEL=2` and increase only if needed. Higher levels generate massive amounts of data.

### 2. Clear Logs Between Runs
```bash
# Clear core logs (Rust + Python bindings)
rm -f /tmp/par_term_emu_core_rust_debug_*.log

# Clear TUI application logs
rm -rf debug_logs/

# Or use make target to clear core logs
make debug-clear

# Note: TUI application logs are timestamped, so each run creates a new file
# The debug-clear make target only clears core logs, not TUI logs
```

### 3. Use Grep Effectively
```bash
# Find specific categories in Rust log (VT sequences, core operations)
grep "\[VT_INPUT\]" /tmp/par_term_emu_core_rust_debug_rust.log
grep "\[CSI\]" /tmp/par_term_emu_core_rust_debug_rust.log
grep "\[SCREEN_SWITCH\]" /tmp/par_term_emu_core_rust_debug_rust.log

# Find specific categories in Python core log (rendering, widgets)
grep "\[RENDER\]" /tmp/par_term_emu_debug_python.log
grep "\[LIFECYCLE\]" /tmp/par_term_emu_debug_python.log

# Search TUI application logs (standard Python logging format)
grep "INFO" debug_logs/terminal_debug_*.log
grep "WARNING" debug_logs/terminal_debug_*.log
grep "ERROR" debug_logs/terminal_debug_*.log

# Check all logs for corruption
grep "\[CORRUPTION\]" /tmp/par_term_emu_core_rust_debug_*.log
grep "corruption" debug_logs/terminal_debug_*.log

# Find time ranges (timestamps are in seconds since epoch for core logs)
awk '$2 >= 1234567890.0 && $2 <= 1234567900.0' /tmp/par_term_emu_core_rust_debug_rust.log
awk '$2 >= 1234567890.0 && $2 <= 1234567900.0' /tmp/par_term_emu_debug_python.log

# Count event types in each log
echo "Rust core events:"
grep -o "\[.*\]" /tmp/par_term_emu_core_rust_debug_rust.log | sort | uniq -c
echo "Python core events:"
grep -o "\[.*\]" /tmp/par_term_emu_debug_python.log | sort | uniq -c
echo "TUI application log levels:"
grep -o "\[.*\]" debug_logs/terminal_debug_*.log | sort | uniq -c
```

### 4. Correlate with Behavior
When corruption appears:
1. Note the approximate time
2. Find that timestamp in the log
3. Look at events 1-2 seconds before
4. Check for unusual patterns

### 5. Compare Good vs Bad Runs
```bash
# Good run
export DEBUG_LEVEL=3
uv run par-term-emu-tui-rust --debug
# Exit cleanly
mv /tmp/par_term_emu_core_rust_debug_rust.log /tmp/good_run_rust.log
mv /tmp/par_term_emu_debug_python.log /tmp/good_run_python.log
cp debug_logs/terminal_debug_*.log /tmp/good_run_tui.log

# Bad run (reproduce corruption)
uv run par-term-emu-tui-rust --debug
mv /tmp/par_term_emu_core_rust_debug_rust.log /tmp/bad_run_rust.log
mv /tmp/par_term_emu_debug_python.log /tmp/bad_run_python.log
cp debug_logs/terminal_debug_*.log /tmp/bad_run_tui.log

# Compare
diff /tmp/good_run_rust.log /tmp/bad_run_rust.log
diff /tmp/good_run_python.log /tmp/bad_run_python.log
diff /tmp/good_run_tui.log /tmp/bad_run_tui.log
```

### 6. Use Buffer Snapshots Strategically
Use the snapshot methods to capture terminal state at key moments:

```python
# Before suspicious operation
snapshot_before = term.debug_snapshot_buffer()
print("Before operation:", snapshot_before)

# After suspicious operation
snapshot_after = term.debug_snapshot_buffer()
print("After operation:", snapshot_after)

# Compare manually or save to files for diff
with open("/tmp/before.txt", "w") as f:
    f.write(snapshot_before)
with open("/tmp/after.txt", "w") as f:
    f.write(snapshot_after)
# Then: diff /tmp/before.txt /tmp/after.txt
```

## Performance Impact

Debug logging has minimal impact at lower levels:

- **Level 0 (OFF):** No overhead
- **Level 1-2:** Negligible (< 1% CPU, < 1 MB/s)
- **Level 3:** Moderate (1-5% CPU, 5-10 MB/s)
- **Level 4:** Significant (5-10% CPU, 50-100 MB/s)

**Recommendation:** Use level 3 for most debugging. Only use level 4 for short, targeted investigations.

## Troubleshooting the Debug System

### Debug log files not being created

```bash
# Check permissions for core log files
ls -la /tmp/par_term_emu_core_rust_debug_rust.log
ls -la /tmp/par_term_emu_debug_python.log

# Check TUI application log directory
ls -la debug_logs/

# Check environment variable for core logging
echo $DEBUG_LEVEL

# Verify DEBUG_LEVEL is set before running
DEBUG_LEVEL=3 python -c "import os; print(os.environ.get('DEBUG_LEVEL'))"

# Check if --debug flag was used for TUI application logging
# TUI logs only appear when --debug flag is passed
```

### No output in debug logs

**For core logs** (Rust/Python bindings):
- Ensure `DEBUG_LEVEL` is set and exported
- Check that it's a valid value (0-4)
- Level 0 disables all debug logging
- Verify the application is actually running

**For TUI application logs**:
- Ensure `--debug` flag was passed to the application
- Check that `debug_logs/` directory was created
- Verify permissions on the `debug_logs/` directory

### Log files growing too large

```bash
# Truncate the core logs
> /tmp/par_term_emu_core_rust_debug_rust.log
> /tmp/par_term_emu_debug_python.log

# Or delete core logs
rm -f /tmp/par_term_emu_core_rust_debug_*.log

# Or use make target (core logs only)
make debug-clear

# Clean up old TUI application logs
rm -rf debug_logs/

# Keep only the most recent TUI log
cd debug_logs && ls -t | tail -n +2 | xargs rm -f
```

### Can't read log files (TUI corrupted)

Debug output goes to files specifically so you can read them from another terminal:

```bash
# In a separate terminal window/pane - view core logs
tail -f /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_debug_python.log

# View TUI application logs
tail -f debug_logs/terminal_debug_*.log

# Or use make target for core logs
make debug-tail

# View all logs together
tail -f /tmp/par_term_emu_core_rust_debug_*.log debug_logs/terminal_debug_*.log
```

## Advanced Usage

### Filtering Specific Categories

You can modify `src/debug.rs` to add your own categories or disable specific ones.

### Custom Debug Points

Add your own debug logging if extending the codebase:

**Rust (in core library code):**
```rust
use crate::debug;
debug::log(debug::DebugLevel::Info, "MY_CATEGORY", "Something happened");
// Or use convenience macros:
debug_info!("MY_CATEGORY", "Info message: {}", value);
debug_log!("MY_CATEGORY", "Debug message: {}", value);
```

**Python (in TUI widget code):**
```python
# Internal use only - these are imported within the par_term_emu_tui_rust package
from par_term_emu_core_rust.debug import debug_log, debug_info
debug_log("MY_CATEGORY", "Something interesting happened")
debug_info("MY_CATEGORY", "Informational message")
```

**Note**: The Python debug module is from the par-term-emu-core-rust package and is primarily for internal use within the par-term-emu-tui-rust package. User applications should rely on the automatic debug logging triggered by `DEBUG_LEVEL`.

### Time-Based Analysis

Use the timestamps to create timelines and correlate events between Rust and Python:

```bash
# Extract timestamps and events from both logs
echo "Rust events:"
grep "\[VT_INPUT\]" /tmp/par_term_emu_core_rust_debug_rust.log | \
    awk '{print $2, $4, $5, $6}' | \
    head -10

echo "Python events:"
grep "\[RENDER\]" /tmp/par_term_emu_debug_python.log | \
    awk '{print $2, $4, $5, $6}' | \
    head -10

# Merge and sort by timestamp to see interleaved events
sort -t'[' -k2 -n /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_debug_python.log | \
    grep -E '\[(VT_INPUT|RENDER|CORRUPTION)\]' | \
    head -30
```

## FAQ

**Q: Will debug logging affect the timing of the bug?**
A: At levels 1-3, the overhead is minimal. If you're concerned, start with level 2.

**Q: Can I leave debug logging on in production?**
A: Level 0 (default) has zero overhead. Levels 1-2 could be left on if needed, but typically you'd only enable debugging when investigating issues.

**Q: What if the corruption doesn't reproduce with debugging on?**
A: This would be valuable information! It might suggest a timing-sensitive issue. Try level 2 (minimal overhead) first.

**Q: How do I debug the Python side without the Rust side?**
A: Set `DEBUG_LEVEL` and use the Python debug module directly. The Rust side will respect the same environment variable.

**Q: Can I change the debug output location?**
A: For core logs (Rust/Python bindings), edit the file paths in the par-term-emu-core-rust package:
  - Rust: `src/debug.rs` (hardcoded to `/tmp` on Unix/macOS, uses `std::env::temp_dir()` on Windows)
  - Python: `python/par_term_emu_core_rust/debug.py` (uses `tempfile.gettempdir()` for platform-specific temp directory)

For TUI application logs, they are always created in `debug_logs/` subdirectory of the current working directory. To change this, edit `setup_debug_logging()` in `src/par_term_emu_tui_rust/app.py`.

**Q: Why are there three separate log files?**
A: The three-layer separation serves different purposes:
  - **Rust core log**: Terminal emulation, VT parsing, PTY operations (lowest level)
  - **Python core log**: Python bindings and widget integration (middle level)
  - **TUI application log**: Application logic, user interactions, high-level flow (highest level)

This separation makes it easier to identify which layer issues originate from and avoids race conditions when components write simultaneously.

## Which Log Should I Check?

Understanding where to look for different types of issues:

| Issue Type | Check This Log | Look For |
|------------|----------------|----------|
| **VT sequence corruption** | Rust core (`_rust.log`) | `[VT_INPUT]`, `[CSI]`, `[OSC]` patterns |
| **Screen buffer issues** | Rust core (`_rust.log`) | `[SCREEN_SWITCH]`, `[GRID_OP]`, `[SCROLL]` |
| **Device query problems** | Rust core (`_rust.log`) | `[DEVICE_QUERY]` responses |
| **PTY communication** | Rust core (`_rust.log`) | `[PTY_READ]`, `[PTY_WRITE]` operations |
| **Rendering corruption** | Python core (`_python.log`) | `[CORRUPTION]`, `[RENDER]`, `[SNAPSHOT]` |
| **Widget lifecycle** | Python core (`_python.log`) | `[LIFECYCLE]` mount/unmount/resize |
| **Application flow** | TUI app (`terminal_debug_*.log`) | INFO/WARNING/ERROR messages |
| **Configuration issues** | TUI app (`terminal_debug_*.log`) | Config loading, validation errors |
| **Screenshot capture** | TUI app (`terminal_debug_*.log`) | Screenshot save paths, errors |
| **User interactions** | TUI app (`terminal_debug_*.log`) | Key bindings, mouse events |
| **Generation tracking** | Core logs (Rust + Python) | `[GENERATION]` counter changes |
| **Timing issues** | All logs (merged sort) | Correlate timestamps across logs |

## Related Files

### Rust Debug Infrastructure
All Rust debug infrastructure is in the **par-term-emu-core-rust** package (located at `../par-term-emu-core-rust`):
- **`src/debug.rs`** - Core debug logging system (outputs to `_rust.log`)
- **`src/terminal/mod.rs`** - VT sequence logging via `Perform` trait
- **`src/pty_session.rs`** - PTY operation logging
- **`src/grid.rs`** - Grid snapshot methods (`debug_snapshot()`)

### Python Debug Infrastructure

**Core Python bindings** (in par-term-emu-core-rust package):
- **`python/par_term_emu_core_rust/debug.py`** - Python core debug logging system (outputs to `_python.log`)

**TUI Application** (in this repository):
- **`src/par_term_emu_tui_rust/app.py`** - Main application with `setup_debug_logging()` function
  - Creates `debug_logs/` directory
  - Generates timestamped log files: `terminal_debug_YYYYMMDD_HHMMSS.log`
  - Configures Python standard logging module
  - Activated via `--debug` CLI flag
- **`src/par_term_emu_tui_rust/terminal_widget/`** - TUI widget modules with lifecycle and rendering logging
- **`src/par_term_emu_tui_rust/dialogs/config_screen.py`** - Configuration dialog with backup logging

## Makefile Debug Targets

The project Makefile provides convenient targets for debugging:

| Target | Description | Environment | Output |
|--------|-------------|-------------|--------|
| `make debug` | Run with INFO level logging | `DEBUG_LEVEL=2` + `--debug` flag | All three log files |
| `make debug-verbose` | Run with DEBUG level logging | `DEBUG_LEVEL=3` + `--debug` flag | All three log files |
| `make debug-trace` | Run with TRACE level logging | `DEBUG_LEVEL=4` + `--debug` flag | All three log files (HUGE!) |
| `make debug-clear` | Clear core debug logs | N/A | Removes Rust and Python core log files |
| `make debug-tail` | Tail core logs in real-time | N/A | Shows Rust + Python core logs |
| `make debug-view` | View core logs with less | N/A | Opens Rust + Python core logs |

**Note**: The `debug-copy-logs` target is mentioned in the Makefile help but not yet implemented.

**Note**:
- The `make debug-clear` target only clears core logs, not TUI application logs
- TUI application logs are timestamped, so each run creates a new file in `debug_logs/`
- All `make debug*` targets automatically run `make debug-clear` first to start with clean logs

## See Also

- **[CONFIG_REFERENCE.md](CONFIG_REFERENCE.md)** - TUI configuration options
- **[Makefile](../Makefile)** - Build and debug targets
- **[README.md](../README.md)** - Project overview and quick start
- **[CLAUDE.md](../CLAUDE.md)** - Development guidelines including debug workflows
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design details
