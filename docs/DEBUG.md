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
- [Tips and Best Practices](#tips-and-best-practices)
- [Performance Impact](#performance-impact)
- [Troubleshooting the Debug System](#troubleshooting-the-debug-system)
- [Advanced Usage](#advanced-usage)
- [FAQ](#faq)
- [Which Log Should I Check?](#which-log-should-i-check)
- [Related Files](#related-files)
- [See Also](#see-also)

## Overview

The debugging system provides extensive logging capabilities across both Rust and Python components, controlled by a single `DEBUG_LEVEL` environment variable. Rust and Python components write to **separate log files** to avoid interfering with TUI applications:

- **Rust core**: `/tmp/par_term_emu_core_rust_debug_rust.log` - Terminal emulation, VT parsing, PTY operations
- **Python TUI**: `/tmp/par_term_emu_core_rust_debug_python.log` - Widget lifecycle, rendering, event handling

This separation makes it easier to identify whether issues originate in the core terminal emulation layer (Rust) or the TUI presentation layer (Python).

## Quick Start

```bash
# Set debug level (0-4)
export DEBUG_LEVEL=3

# Run your application
python -m par_term_emu_tui_rust

# View debug output in real-time (both logs)
tail -f /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_core_rust_debug_python.log

# Or view individually
tail -f /tmp/par_term_emu_core_rust_debug_rust.log   # Rust core only
tail -f /tmp/par_term_emu_core_rust_debug_python.log # Python TUI only

# Or after the fact
less /tmp/par_term_emu_core_rust_debug_rust.log
less /tmp/par_term_emu_core_rust_debug_python.log
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
python -m par_term_emu_tui_rust
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
python -m par_term_emu_tui_rust
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
python -m par_term_emu_tui_rust
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
grep CORRUPTION /tmp/par_term_emu_core_rust_debug_python.log

# Find screen switches (Rust log - core terminal operations)
grep SCREEN_SWITCH /tmp/par_term_emu_core_rust_debug_rust.log

# Find device queries (Rust log - VT sequence handling)
grep DEVICE_QUERY /tmp/par_term_emu_core_rust_debug_rust.log

# Find render warnings (Python log - TUI rendering)
grep "WARNING" /tmp/par_term_emu_core_rust_debug_python.log

# Get context around a specific time (both logs)
grep -A 10 -B 10 "CORRUPTION" /tmp/par_term_emu_core_rust_debug_rust.log
grep -A 10 -B 10 "CORRUPTION" /tmp/par_term_emu_core_rust_debug_python.log
```

## Running the TUI with Debug Mode

Set the `DEBUG_LEVEL` environment variable before running the TUI:

```bash
# Run TUI with debug level 2 (info)
DEBUG_LEVEL=2 python -m par_term_emu_tui_rust

# Run TUI with debug level 3 (debug)
DEBUG_LEVEL=3 python -m par_term_emu_tui_rust

# Run TUI with debug level 4 (trace) - WARNING: huge logs
DEBUG_LEVEL=4 python -m par_term_emu_tui_rust

# Clear the debug log files
rm -f /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_core_rust_debug_python.log

# Show the debug logs in real-time
tail -f /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_core_rust_debug_python.log

# Show the debug logs in less
less /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_core_rust_debug_python.log
```

## Tips and Best Practices

### 1. Start with Lower Levels
Begin with `DEBUG_LEVEL=2` and increase only if needed. Higher levels generate massive amounts of data.

### 2. Clear the Log Between Runs
```bash
# Clear both logs
rm -f /tmp/par_term_emu_core_rust_debug_*.log

# Or use make target
make debug-clear
```

### 3. Use Grep Effectively
```bash
# Find specific categories in Rust log (VT sequences, core operations)
grep "\[VT_INPUT\]" /tmp/par_term_emu_core_rust_debug_rust.log
grep "\[CSI\]" /tmp/par_term_emu_core_rust_debug_rust.log
grep "\[SCREEN_SWITCH\]" /tmp/par_term_emu_core_rust_debug_rust.log

# Find specific categories in Python log (rendering, widgets)
grep "\[RENDER\]" /tmp/par_term_emu_core_rust_debug_python.log
grep "\[LIFECYCLE\]" /tmp/par_term_emu_core_rust_debug_python.log

# Check both for corruption
grep "\[CORRUPTION\]" /tmp/par_term_emu_core_rust_debug_*.log

# Find time ranges (timestamps are in seconds since epoch)
awk '$2 >= 1234567890.0 && $2 <= 1234567900.0' /tmp/par_term_emu_core_rust_debug_rust.log
awk '$2 >= 1234567890.0 && $2 <= 1234567900.0' /tmp/par_term_emu_core_rust_debug_python.log

# Count event types in each log
echo "Rust events:"
grep -o "\[.*\]" /tmp/par_term_emu_core_rust_debug_rust.log | sort | uniq -c
echo "Python events:"
grep -o "\[.*\]" /tmp/par_term_emu_core_rust_debug_python.log | sort | uniq -c
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
python -m par_term_emu_tui_rust
# Exit cleanly
mv /tmp/par_term_emu_core_rust_debug_rust.log /tmp/good_run_rust.log
mv /tmp/par_term_emu_core_rust_debug_python.log /tmp/good_run_python.log

# Bad run (reproduce corruption)
python -m par_term_emu_tui_rust
mv /tmp/par_term_emu_core_rust_debug_rust.log /tmp/bad_run_rust.log
mv /tmp/par_term_emu_core_rust_debug_python.log /tmp/bad_run_python.log

# Compare
diff /tmp/good_run_rust.log /tmp/bad_run_rust.log
diff /tmp/good_run_python.log /tmp/bad_run_python.log
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

### Debug log file not being created

```bash
# Check permissions for both log files
ls -la /tmp/par_term_emu_core_rust_debug_rust.log
ls -la /tmp/par_term_emu_core_rust_debug_python.log

# Check environment variable
echo $DEBUG_LEVEL

# Verify it's set before running
DEBUG_LEVEL=3 python -c "import os; print(os.environ.get('DEBUG_LEVEL'))"
```

### No output in debug log

- Ensure `DEBUG_LEVEL` is set and exported
- Check that it's a valid value (0-4)
- Verify the application is actually running

### Log file growing too large

```bash
# Truncate the logs
> /tmp/par_term_emu_core_rust_debug_rust.log
> /tmp/par_term_emu_core_rust_debug_python.log

# Or delete and recreate
rm /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_core_rust_debug_python.log

# Or use make target
rm -f /tmp/par_term_emu_core_rust_debug_*.log
```

### Can't read log file (TUI corrupted)

Debug output goes to files specifically so you can read them from another terminal:

```bash
# In a separate terminal window/pane
tail -f /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_core_rust_debug_python.log

# Or use make target
tail -f /tmp/par_term_emu_core_rust_debug_*.log
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
grep "\[RENDER\]" /tmp/par_term_emu_core_rust_debug_python.log | \
    awk '{print $2, $4, $5, $6}' | \
    head -10

# Merge and sort by timestamp to see interleaved events
sort -t'[' -k2 -n /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_core_rust_debug_python.log | \
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
A: Yes, edit the file paths in:
  - Rust: `src/debug.rs` in the par-term-emu-core-rust package (uses `std::env::temp_dir()` to get platform-specific temp directory)
  - Python: `python/par_term_emu_core_rust/debug.py` in the par-term-emu-core-rust package (uses `tempfile.gettempdir()`)

**Q: Why are there two separate log files?**
A: Separating Rust (core terminal emulation) and Python (TUI widget) logs makes it easier to identify whether issues originate in the terminal emulation layer or the presentation layer. It also avoids race conditions when both components write simultaneously.

## Which Log Should I Check?

Understanding where to look for different types of issues:

| Issue Type | Check This Log | Look For |
|------------|----------------|----------|
| **VT sequence corruption** | Rust (`_rust.log`) | `[VT_INPUT]`, `[CSI]`, `[OSC]` patterns |
| **Screen buffer issues** | Rust (`_rust.log`) | `[SCREEN_SWITCH]`, `[GRID_OP]`, `[SCROLL]` |
| **Device query problems** | Rust (`_rust.log`) | `[DEVICE_QUERY]` responses |
| **PTY communication** | Rust (`_rust.log`) | `[PTY_READ]`, `[PTY_WRITE]` operations |
| **Rendering corruption** | Python (`_python.log`) | `[CORRUPTION]`, `[RENDER]`, `[SNAPSHOT]` |
| **Widget lifecycle** | Python (`_python.log`) | `[LIFECYCLE]` mount/unmount/resize |
| **Generation tracking** | Both logs | `[GENERATION]` counter changes |
| **Timing issues** | Both logs (merged sort) | Correlate timestamps between logs |

## Related Files

### Rust Debug Infrastructure
All Rust debug infrastructure is in the **par-term-emu-core-rust** package (located at `../par-term-emu-core-rust`):
- **`src/debug.rs`** - Core debug logging system (outputs to `_rust.log`)
- **`src/terminal/mod.rs`** - VT sequence logging via `Perform` trait
- **`src/pty_session.rs`** - PTY operation logging
- **`src/grid.rs`** - Grid snapshot methods (`debug_snapshot()`)

### Python Debug Infrastructure
- **`python/par_term_emu_core_rust/debug.py`** (in par-term-emu-core-rust package) - Python debug logging system (outputs to `_python.log`)
- **`src/par_term_emu_tui_rust/terminal_widget/`** - TUI widget modules with lifecycle and rendering logging

### TUI Application
- **`src/par_term_emu_tui_rust/`** - TUI application package

## See Also

- **[CONFIG_REFERENCE.md](CONFIG_REFERENCE.md)** - TUI configuration options
- **[README.md](../README.md)** - TUI application overview
