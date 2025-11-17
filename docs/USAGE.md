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

> **📝 Note:** Default shell is `$SHELL` environment variable or `/bin/bash` if not set.

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

Options:
  -d, --debug                  Enable debug logging to debug_logs/
  -s, --shell SHELL            Shell to execute (default: $SHELL on Unix, PowerShell/cmd.exe on Windows)
  -c, --command CMD            Command to inject after 1 second delay
  -q, --auto-quit SECONDS      Automatically quit after specified seconds
  --screenshot SECONDS         Take screenshot after specified seconds
  --open-screenshot            Open screenshot with default viewer after capture
  --init-config                Create default config.yaml and exit
  --export-theme NAME          Export current theme as NAME and exit
  --apply-theme NAME           Apply built-in theme NAME and exit
  --list-themes                List available themes and exit
  --apply-theme-from FILE      Apply theme from YAML file and exit
  --theme NAME                 Use theme for this session (overrides config)
  -h, --help                   Show this help message and exit
```

### Debug Options

**Enable debug logging:**
```bash
# Create timestamped debug log
par-term-emu-tui-rust --debug

# Log location: debug_logs/terminal_debug_YYYYMMDD_HHMMSS.log
```

**View debug output:**
```bash
# Tail debug log in real-time
tail -f debug_logs/terminal_debug_*.log

# Search for specific events
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
theme: "iterm2-dark"

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
url_modifier: "none"

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
```

> **📝 Note:** See [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md) for detailed documentation of each setting.

## Theme Management

### List Available Themes

```bash
# Display all built-in themes
par-term-emu-tui-rust --list-themes
```

**Available themes:**
- `dark-background` - Classic dark terminal
- `high-contrast` - High contrast for accessibility
- `iterm2-dark` - iTerm2 Dark (default)
- `light-background` - Classic light terminal
- `pastel-dark` - Soft pastel on dark
- `regular` - Balanced colors
- `smoooooth` - Smooth, muted colors
- `solarized` - Original Solarized
- `solarized-dark` - Solarized Dark variant
- `solarized-light` - Solarized Light variant
- `tango-dark` - Tango Dark
- `tango-light` - Tango Light

### Apply Themes

**Temporary theme (session only):**
```bash
# Override config for this session
par-term-emu-tui-rust --theme solarized-dark
```

**Permanent theme:**
```bash
# Update config.yaml with new theme
par-term-emu-tui-rust --apply-theme solarized-dark

# Verify change
grep "theme:" ~/.config/par-term-emu-tui-rust/config.yaml
```

### Custom Themes

**Export current theme:**
```bash
# Export theme to YAML file
par-term-emu-tui-rust --export-theme my-custom-theme

# Creates: my-custom-theme.yaml
```

**Edit theme file:**
```yaml
# my-custom-theme.yaml
name: "my-custom-theme"
colors:
  # 16 ANSI colors
  black: [0, 0, 0]
  red: [205, 49, 49]
  green: [13, 188, 121]
  # ... more colors ...

  # Special colors
  background: [30, 30, 30]
  foreground: [229, 229, 229]
  cursor: [229, 229, 229]
  selection: [54, 54, 54]
  link: [100, 150, 255]
```

**Apply custom theme:**
```bash
# Load theme from file
par-term-emu-tui-rust --apply-theme-from my-custom-theme.yaml
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

themes=("dark-background" "solarized-dark" "high-contrast")

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
tail -f debug_logs/debug_*.log

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
# 1. Export base theme
par-term-emu-tui-rust --export-theme my-theme

# 2. Edit colors
$EDITOR my-theme.yaml

# 3. Apply and test
par-term-emu-tui-rust --apply-theme-from my-theme.yaml

# 4. If satisfied, make permanent
par-term-emu-tui-rust --apply-theme-from my-theme.yaml
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
    --theme solarized-dark \
    --command "neofetch" \
    --screenshot 3 \
    --auto-quit 5

# Show directory tree
par-term-emu-tui-rust \
    --theme tango-dark \
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

- [Quick Start Guide](QUICK_START.md) - Get started in 5 minutes
- [Installation Guide](INSTALLATION.md) - Install and setup
- [Features](FEATURES.md) - Complete feature list
- [Key Bindings](KEY_BINDINGS.md) - Keyboard and mouse reference
- [Configuration Reference](CONFIG_REFERENCE.md) - All configuration options
- [Screenshots Guide](SCREENSHOTS.md) - Screenshot functionality
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
