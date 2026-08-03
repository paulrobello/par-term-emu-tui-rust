# Usage Guide

Complete guide to running and using Par Term Emu TUI Rust, including command-line options, configuration, and common workflows.

## Table of Contents
- [Running the TUI](#running-the-tui)
- [Command-Line Options](#command-line-options)
- [Configuration File](#configuration-file)
- [Theme Management](#theme-management)
- [Testing and Automation](#testing-and-automation)
- [Common Workflows](#common-workflows)
- [Advanced Usage](#advanced-usage)
- [Related Documentation](#related-documentation)

## Running the TUI

### Basic Usage

Multiple ways to launch the TUI:

```bash
# Method 1: Using make (recommended)
make run

# Method 2: Using installed script
uv run par-term-emu-tui-rust

# Method 3: Short alias
uv run ptr

# Method 4: As Python module
uv run python -m par_term_emu_tui_rust

# Method 5: Direct script execution
uv run python src/par_term_emu_tui_rust/app.py
```

### With Custom Shell

Specify which shell to run:

```bash
# Use zsh
par-term-emu-tui-rust --shell /bin/zsh

# Use fish
par-term-emu-tui-rust --shell /usr/bin/fish

# Use bash explicitly
par-term-emu-tui-rust --shell /bin/bash
```

> **📝 Note:** Default shell is `$SHELL` environment variable on Unix, or PowerShell/cmd.exe on Windows.

### Execute Command

Inject a command after startup:

```bash
# Run command and continue interactive session
par-term-emu-tui-rust --command "ls -la"

# Show system info
par-term-emu-tui-rust --command "neofetch"

# Chain commands
par-term-emu-tui-rust --command "cd /tmp && ls"
```

> **📝 Note:** Command executes after 1-second delay to allow terminal initialization.

## Command-Line Options

### Complete Reference

```
Usage: par-term-emu-tui-rust [OPTIONS]
       par-term-emu-tui-rust install <component> [OPTIONS]

Options:
  -h, --help                             Show this help message and exit
  -d, --debug                            Enable debug logging to timestamped file in debug_logs/
  -s, --shell SHELL                      Shell to execute (default: $SHELL on Unix, PowerShell/cmd.exe on Windows)
  -c, --command COMMAND                  Command to inject into prompt after 1 second delay
  -q, --auto-quit SECONDS                Automatically quit after specified seconds
  --screenshot SECONDS                   Take screenshot of terminal buffer after specified seconds
  --open-screenshot                      Open screenshot with default system viewer after capture
  --init-config                          Create default config.yaml in the XDG config directory and exit
  --export-theme NAME                    Export the current theme as NAME and exit
  --apply-theme NAME                     Apply a built-in theme NAME to config.yaml and exit
  --list-themes                          List available built-in themes and exit
  --apply-theme-from FILE                Apply a theme from a YAML file path to config.yaml and exit
  --theme THEME                          Color theme to use for this session (overrides config file)
  --keyboard-protocol                    Enable KITTY keyboard protocol for embedded applications
  --no-keyboard-protocol                 Disable KITTY keyboard protocol (override config file)
  --keyboard-protocol-flags FLAGS        KITTY protocol flags: 1=disambiguate, 2=events, 4=alternate, 8=report_all, 16=text (combine by adding)
  --keyboard-protocol-auto-detect        Auto-detect and enable KITTY protocol when embedded apps request it
  --no-keyboard-protocol-auto-detect     Disable auto-detection (override config file)

Subcommands:
  install                                Install shell integration, terminfo, or fonts
                                        Run 'par-term-emu-tui-rust install --help' for details
```

### Debug Options

**Enable debug logging:**
```bash
# Create timestamped debug log
par-term-emu-tui-rust --debug

# Python TUI log location: debug_logs/terminal_debug_YYYYMMDD_HHMMSS.log
# Rust backend log location: System temp directory (platform-specific)
```

**View debug output:**
```bash
# Tail Python TUI debug log in real-time
tail -f debug_logs/terminal_debug_*.log

# Tail Rust backend debug logs (macOS/Linux)
# Note: Log location is in system temp directory
tail -f "$(python3 -c 'import tempfile; print(tempfile.gettempdir())')/par_term_emu_core_rust_debug_rust.log"

# Or use make command to tail all logs
make debug-tail

# Search for specific events in TUI logs
grep "ERROR" debug_logs/terminal_debug_*.log
```

### Configuration Options

**Initialize configuration:**
```bash
# Create default config file
par-term-emu-tui-rust --init-config

# Config location: ~/.config/par-term-emu-tui-rust/config.yaml
```

**Edit configuration:**
```bash
# Option 1: Use built-in config editor (recommended)
# While TUI is running, press Alt+Ctrl+Shift+C to open the config editor
# - Syntax highlighting and live validation
# - Auto-creates config file if it doesn't exist
# - Ctrl+S to save, Escape to cancel

# Option 2: Display current configuration
cat ~/.config/par-term-emu-tui-rust/config.yaml

# Option 3: Edit directly with your editor
$EDITOR ~/.config/par-term-emu-tui-rust/config.yaml
```

## Configuration File

### File Location

**Standard locations:**

| Platform | Path |
|----------|------|
| **Linux** | `~/.config/par-term-emu-tui-rust/config.yaml` |
| **macOS** | `~/.config/par-term-emu-tui-rust/config.yaml` |
| **Windows** | `%APPDATA%\par-term-emu-tui-rust\config.yaml` |

### Configuration Structure

```yaml
# ============================================================================
# Selection & Clipboard
# ============================================================================
auto_copy_selection: true
keep_selection_after_copy: true
expose_system_clipboard: true
copy_trailing_newline: false
word_characters: "/-+\\~_."
triple_click_selects_wrapped_lines: true

# ============================================================================
# Scrollback & Cursor
# ============================================================================
scrollback_lines: 10000
max_scrollback_lines: 100000
cursor_blink_enabled: false
cursor_blink_rate: 0.5
cursor_style: "blinking_block"

# ============================================================================
# Paste Enhancement
# ============================================================================
paste_chunk_size: 0
paste_chunk_delay_ms: 10
paste_warn_size: 100000

# ============================================================================
# Mouse & Focus
# ============================================================================
focus_follows_mouse: false
middle_click_paste: true
mouse_wheel_scroll_lines: 3

# ============================================================================
# Security & Advanced
# ============================================================================
disable_insecure_sequences: false
accept_osc7: true

# ============================================================================
# Theme & Colors
# ============================================================================
theme: "dark-background"
bold_brightening: false
minimum_contrast: 0.0
faint_text_alpha: 0.5

# ============================================================================
# Notifications
# ============================================================================
show_notifications: true
notification_timeout: 5

# ============================================================================
# Screenshot
# ============================================================================
screenshot_directory: null
screenshot_format: "png"
screenshot_minimum_contrast: null
open_screenshot_after_capture: false

# ============================================================================
# Shell Behavior
# ============================================================================
exit_on_shell_exit: true

# ============================================================================
# Hyperlinks & URLs
# ============================================================================
clickable_urls: true
link_color: [100, 150, 255]
url_modifier: "ctrl"
allowed_url_schemes: ["http", "https", "ftp", "ftps", "file", "mailto"]
warn_on_unknown_url_scheme: true

# ============================================================================
# Search & Highlighting
# ============================================================================
search_match_color: [255, 255, 0]

# ============================================================================
# UI Elements
# ============================================================================
show_status_bar: true

# ============================================================================
# Visual Bell
# ============================================================================
visual_bell_enabled: true

# ============================================================================
# Keyboard Protocol (KITTY)
# ============================================================================
keyboard_protocol_enabled: false
keyboard_protocol_flags: 1
keyboard_protocol_auto_detect: false
```

> **📝 Note:** See [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md) for detailed documentation of each setting.

## Theme Management

### List Available Themes

```bash
# Display all built-in themes
par-term-emu-tui-rust --list-themes
```

**Available themes:**
- `Dark Background` - Classic dark terminal (default)
- `High Contrast` - High contrast for accessibility
- `Light Background` - Classic light terminal
- `Pastel (Dark Background)` - Soft pastel colors on dark background
- `Regular` - Balanced colors for general use
- `Smoooooth` - Smooth, muted colors
- `Solarized` - Original Solarized theme
- `Solarized Dark` - Solarized Dark variant
- `Solarized Light` - Solarized Light variant
- `Tango Dark` - Tango colors on dark gray background
- `Tango Light` - Tango colors on light background
- `iTerm2 Dark` - iTerm2-style colors with pure black background

### Apply Themes

**Temporary theme (session only):**
```bash
# Override config for this session (use exact theme name with spaces/capitals)
par-term-emu-tui-rust --theme "Solarized Dark"
```

**Permanent theme:**
```bash
# Update config.yaml with new theme (use exact theme name)
par-term-emu-tui-rust --apply-theme "Solarized Dark"

# Verify change
grep "theme:" ~/.config/par-term-emu-tui-rust/config.yaml
```

### Custom Themes

**Export current theme:**
```bash
# Export theme to the XDG themes directory
par-term-emu-tui-rust --export-theme my-custom-theme

# Creates: ~/.config/par-term-emu-tui-rust/themes/my-custom-theme.yaml
```

**Edit theme file:**
```yaml
# ~/.config/par-term-emu-tui-rust/themes/my-custom-theme.yaml
name: "my-custom-theme"
palette:
  # 16 ANSI colors (0-15) as hex strings
  - "#000000"   # 0  black
  - "#bb0000"   # 1  red
  - "#00bb00"   # 2  green
  - "#bbbb00"   # 3  yellow
  - "#0000bb"   # 4  blue
  - "#bb00bb"   # 5  magenta
  - "#00bbbb"   # 6  cyan
  - "#bbbbbb"   # 7  white
  - "#555555"   # 8  bright black
  - "#ff5555"   # 9  bright red
  - "#55ff55"   # 10 bright green
  - "#ffff55"   # 11 bright yellow
  - "#5555ff"   # 12 bright blue
  - "#ff55ff"   # 13 bright magenta
  - "#55ffff"   # 14 bright cyan
  - "#ffffff"   # 15 bright white
background: "#1e1e1e"
foreground: "#e5e5e5"
cursor: "#e5e5e5"
cursor_text: "#000000"
selection: "#363636"
selection_text: "#ffffff"
link: "#6496ff"
bold: "#ffffff"
cursor_guide: "#a6e8ff"
underline: "#bbbbbb"
badge: "#ff0000"
match: "#ffff00"
```

> **📝 Note:** Every field is required. The cleanest way to create a custom theme is to export a built-in theme first, then edit the resulting file.

**Apply custom theme:**
```bash
# Load theme from file (path may be absolute or relative)
par-term-emu-tui-rust --apply-theme-from ~/.config/par-term-emu-tui-rust/themes/my-custom-theme.yaml
```

## Testing and Automation

### Automated Testing

**Auto-quit for CI/CD:**
```bash
# Quit after 10 seconds
par-term-emu-tui-rust --auto-quit 10
```

**Screenshot testing:**
```bash
# Take screenshot and quit
par-term-emu-tui-rust --screenshot 3 --auto-quit 5

# With custom command
par-term-emu-tui-rust --command "neofetch" --screenshot 2 --auto-quit 4
```

**Open screenshots automatically:**
```bash
# Capture and open for review
par-term-emu-tui-rust --screenshot 3 --open-screenshot --auto-quit 5
```

### Testing Workflow Example

```bash
#!/bin/bash
# test-themes.sh - Test all themes with screenshots

themes=("Dark Background" "Solarized Dark" "High Contrast")

for theme in "${themes[@]}"; do
    echo "Testing theme: $theme"
    par-term-emu-tui-rust \
        --theme "$theme" \
        --command "echo 'Testing $theme'" \
        --screenshot 2 \
        --auto-quit 4
done
```

## Common Workflows

### Development Workflow

```bash
# 1. Enable debug logging
par-term-emu-tui-rust --debug

# 2. Monitor logs in another terminal
tail -f debug_logs/terminal_debug_*.log

# Or for Rust backend logs (system temp directory):
tail -f "$(python3 -c 'import tempfile; print(tempfile.gettempdir())')/par_term_emu_core_rust_debug_rust.log"

# Or use make command for both:
make debug-tail

# 3. Test specific functionality
par-term-emu-tui-rust --command "test-command" --debug
```

### Screenshot Workflow

```bash
# 1. Configure preferred format and directory
cat >> ~/.config/par-term-emu-tui-rust/config.yaml <<EOF
screenshot_format: "svg"
# Use a dedicated directory; if not set, smart directory selection is used:
# 1. screenshot_directory (if set)
# 2. Shell CWD from OSC 7
# 3. XDG_PICTURES_DIR/Screenshots or ~/Pictures/Screenshots
# 4. Home directory
screenshot_directory: ~/Screenshots
EOF

# 2. Take manual screenshot
# Run TUI and press Ctrl+Shift+S

# 3. Or automated screenshot
par-term-emu-tui-rust --screenshot 5
```

### Theme Customization Workflow

```mermaid
graph LR
    Export[Export Theme]
    Edit[Edit Colors]
    Apply[Apply Custom Theme]
    Test[Test & Iterate]

    Export --> Edit
    Edit --> Apply
    Apply --> Test
    Test --> Edit

    style Export fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style Edit fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style Apply fill:#e65100,stroke:#ff9800,stroke-width:3px,color:#ffffff
    style Test fill:#880e4f,stroke:#c2185b,stroke-width:2px,color:#ffffff
```

```bash
# 1. Export base theme to ~/.config/par-term-emu-tui-rust/themes/my-theme.yaml
par-term-emu-tui-rust --export-theme my-theme

# 2. Edit colors
$EDITOR ~/.config/par-term-emu-tui-rust/themes/my-theme.yaml

# 3. Apply and test (loads from file, writes theme key to config.yaml)
par-term-emu-tui-rust --apply-theme-from ~/.config/par-term-emu-tui-rust/themes/my-theme.yaml

# 4. Once the theme key is in config.yaml, later sessions load it automatically
par-term-emu-tui-rust
```

## Advanced Usage

### Shell-Specific Configuration

**Per-shell settings:**
```bash
# Bash with specific command
par-term-emu-tui-rust --shell /bin/bash --command "source ~/.bash_profile"

# Zsh with oh-my-zsh
par-term-emu-tui-rust --shell /bin/zsh

# Fish with custom greeting
par-term-emu-tui-rust --shell /usr/bin/fish
```

### Keyboard Protocol Options

**KITTY keyboard protocol for enhanced key handling:**
```bash
# Enable KITTY keyboard protocol
par-term-emu-tui-rust --keyboard-protocol

# Enable with specific flags (disambiguate + events)
par-term-emu-tui-rust --keyboard-protocol-flags 3

# Auto-detect when apps request protocol
par-term-emu-tui-rust --keyboard-protocol-auto-detect

# Disable protocol (override config)
par-term-emu-tui-rust --no-keyboard-protocol
```

**KITTY protocol benefits:**
- Distinguishes Ctrl+I from Tab, Ctrl+M from Enter
- Reports key release events (if flags include 2)
- Enhanced key representations
- Better integration with modern terminal applications

### Environment Variables

**Override configuration:**
```bash
# Set TERM variable
TERM=xterm-256color par-term-emu-tui-rust

# Custom shell
SHELL=/bin/zsh par-term-emu-tui-rust

# Debugging
DEBUG=1 par-term-emu-tui-rust --debug
```

### Integration with Other Tools

**Terminal multiplexer:**
```bash
# Run tmux inside TUI
par-term-emu-tui-rust --shell /usr/bin/tmux

# Run screen
par-term-emu-tui-rust --shell /usr/bin/screen
```

**Remote sessions:**
```bash
# SSH session
par-term-emu-tui-rust --command "ssh user@host"

# Mosh (mobile shell)
par-term-emu-tui-rust --command "mosh user@host"
```

### Scripting Examples

**Automated demo script:**
```bash
#!/bin/bash
# demo.sh - Automated demo with screenshots

# Show system info
par-term-emu-tui-rust \
    --theme "Solarized Dark" \
    --command "neofetch" \
    --screenshot 3 \
    --auto-quit 5

# Show directory tree
par-term-emu-tui-rust \
    --theme "Tango Dark" \
    --command "tree -L 2" \
    --screenshot 3 \
    --auto-quit 5
```

**CI/CD testing:**
```bash
#!/bin/bash
# ci-test.sh - Verify TUI starts successfully

timeout 10 par-term-emu-tui-rust --auto-quit 5 || exit 1
echo "TUI test passed"
```

## Related Documentation

- [Quick Start Guide](QUICK_START.md) - Get started quickly
- [Features](FEATURES.md) - Complete feature list
- [Key Bindings](KEY_BINDINGS.md) - Keyboard and mouse reference
- [Configuration Reference](CONFIG_REFERENCE.md) - All configuration options
- [Keyboard Protocol](KEYBOARD_PROTOCOL.md) - KITTY keyboard protocol guide
- [Screenshots Guide](SCREENSHOTS.md) - Screenshot functionality
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
