# Troubleshooting Guide

Solutions to common issues and problems with Par Term Emu TUI Rust.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [Display Problems](#display-problems)
- [Performance Issues](#performance-issues)
- [Feature-Specific Issues](#feature-specific-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Debug Mode](#debug-mode)
- [Getting Help](#getting-help)
- [Related Documentation](#related-documentation)

## Installation Issues

### Python Version Error

**Problem:**
```
ERROR: Python 3.12 or higher required
```

**Solution:**
```bash
# Check Python version
python3 --version

# Use uv to manage Python versions (recommended)
uv python install 3.14
uv python pin 3.14

# Or install system Python 3.12+
# macOS (using Homebrew)
brew install python@3.14

# Linux (Ubuntu/Debian)
sudo apt-get install python3.14

# Linux (Fedora)
sudo dnf install python3.14
```

### UV Not Found

**Problem:**
```
bash: uv: command not found
```

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.cargo/bin:$PATH"

# Reload shell
exec $SHELL

# Verify installation
uv --version
```

### Module Not Found Error

**Problem:**
```
ModuleNotFoundError: No module named 'par_term_emu_tui_rust'
```

**Solution:**
```bash
# Reinstall dependencies
cd /path/to/par-term-emu-tui-rust
uv sync

# Verify installation
uv run par-term-emu-tui-rust --help
```

### Permission Denied

**Problem:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix executable permissions
chmod +x ~/.local/bin/par-term-emu-tui-rust

# For terminfo installation
par-term-emu-tui-rust install terminfo  # User install (no sudo)
sudo par-term-emu-tui-rust install terminfo --system  # System install
```

## Runtime Errors

### TUI Crashes on Startup

**Problem:** TUI exits immediately or shows error

**Diagnosis:**
```bash
# Enable debug logging (TUI application logs)
par-term-emu-tui-rust --debug

# Check TUI application debug log
cat debug_logs/terminal_debug_*.log

# Enable debug logging for core (Rust + Python bindings)
DEBUG_LEVEL=3 par-term-emu-tui-rust --debug

# Check core debug logs
cat /tmp/par_term_emu_core_rust_debug_rust.log
cat /tmp/par_term_emu_debug_python.log
```

**Common Causes:**
1. Missing dependencies
2. Configuration file syntax errors (see interactive recovery above)
3. Terminal compatibility issues
4. Rust backend library not found

**Solutions:**
```bash
# Reinstall dependencies
uv sync

# Reset configuration (interactive recovery will prompt)
rm ~/.config/par-term-emu-tui-rust/config.yaml

# Or manually create default config
par-term-emu-tui-rust --init-config

# Test with minimal config and auto-quit
par-term-emu-tui-rust --auto-quit 2

# Verify Rust backend is available
python3 -c "import par_term_emu_core_rust; print(par_term_emu_core_rust.__version__)"
```

### Shell Not Starting

**Problem:** Shell doesn't start or exits immediately

**Diagnosis:**
```bash
# Test shell directly
$SHELL --version

# Check shell path
which $SHELL
```

**Solution:**
```bash
# Specify shell explicitly
par-term-emu-tui-rust --shell /bin/bash

# Or use different shell
par-term-emu-tui-rust --shell /bin/zsh
```

### Configuration File Errors

**Problem:**
```
yaml.scanner.ScannerError: while scanning
Failed to parse config: invalid YAML syntax
```

**Interactive Recovery:**

When started in interactive mode (terminal with stdin/stdout), the TUI provides automatic recovery:

1. **Automatic Prompt** - You'll see recovery options:
   ```
   ❌ Error: Failed to parse config file: /path/to/config.yaml
      Failed to parse config file /path/to/config.yaml: ...

   Recovery options:
     1. Reset to default configuration
     2. Restore from most recent backup (config.yaml.backup.20250118_143022)
     3. Show all backup files
     4. Exit

   Select option [1]:
   ```

2. **Option 1: Reset to Defaults** - Creates fresh config with factory settings
3. **Option 2: Restore Most Recent** - Restores from latest backup automatically
4. **Option 3: View All Backups** - Shows all available backups with timestamps and sizes:
   ```
   Available backups:
     1. config.yaml.backup.20250118_143022 (534 bytes, modified 2025-01-18 14:30:22)
     2. config.yaml.backup.20250118_120015 (521 bytes, modified 2025-01-18 12:00:15)

   Select backup number (or Enter to go back):
   ```

**Non-Interactive Mode:**

When run without a TTY (scripts, automation), the TUI automatically uses default configuration without prompts.

**Manual Recovery:**
```bash
# Validate YAML syntax
python3 -c "import yaml, os; yaml.safe_load(open(os.path.expanduser('~/.config/par-term-emu-tui-rust/config.yaml'), encoding='utf-8'))"

# Manually restore specific backup
cp ~/.config/par-term-emu-tui-rust/config.yaml.backup.20250118_143022 \
   ~/.config/par-term-emu-tui-rust/config.yaml

# Recreate default config
mv ~/.config/par-term-emu-tui-rust/config.yaml \
   ~/.config/par-term-emu-tui-rust/config.yaml.backup.manual
par-term-emu-tui-rust --init-config
```

**Automatic Backups:**

Config backups are created automatically when saving configuration from the config screen (Ctrl+Alt+Shift+C):
- Timestamped format: `config.yaml.backup.YYYYMMDD_HHMMSS`
- Stored in `~/.config/par-term-emu-tui-rust/`
- Created before overwriting the existing config file
- Useful for recovery if changes cause issues

## Display Problems

### Colors Not Showing

**Problem:** Terminal appears monochrome or colors incorrect

**Diagnosis:**
```bash
# Check TERM variable
echo $TERM

# Test 256 color support
for i in {0..255}; do printf "\x1b[38;5;%dmcolor%-5d\x1b[0m" $i $i; if ! (( ($i + 1) % 16 )); then echo; fi; done

# Test true color (24-bit)
printf "\x1b[38;2;255;100;0mTRUECOLOR\x1b[0m\n"
```

**Solution:**
```bash
# The TUI sets TERM internally based on capabilities
# You generally don't need to set TERM manually

# Try different themes
par-term-emu-tui-rust --theme dark-background
par-term-emu-tui-rust --theme solarized-dark
par-term-emu-tui-rust --theme high-contrast

# List available themes
par-term-emu-tui-rust --list-themes

# Set theme in config
# Edit ~/.config/par-term-emu-tui-rust/config.yaml
theme: "dark-background"

# Adjust minimum contrast (0.0-1.0)
minimum_contrast: 0.0  # Disabled (default)
minimum_contrast: 0.5  # Moderate contrast (like iTerm2)
minimum_contrast: 1.0  # Maximum contrast
```

### Text Rendering Issues

**Problem:** Characters overlap, missing, or incorrect

**Solutions:**
```bash
# Install Hack font
par-term-emu-tui-rust install font

# Rebuild font cache (Linux)
fc-cache -f -v

# Restart terminal emulator
```

### Terminal Size Wrong

**Problem:** Display doesn't fit window

**Solution:**
```bash
# Force resize by adjusting window
# Most terminals: Cmd/Ctrl + [0/-/+]

# Check terminal size
stty size
```

### Garbled Output

**Problem:** Escape sequences visible or output corrupted

**Solution:**
```bash
# Reset terminal
reset

# Clear scrollback
clear

# Restart TUI
par-term-emu-tui-rust
```

## Performance Issues

### Slow Scrolling

**Problem:** Scrollback navigation is slow

**Solution:**
```yaml
# In config.yaml - reduce scrollback
scrollback_lines: 1000  # Default is 10000

# Unlimited scrollback (up to safety limit)
scrollback_lines: 0
max_scrollback_lines: 100000  # Safety limit when unlimited

# Recommended values
scrollback_lines: 5000   # Good balance
scrollback_lines: 10000  # Default
scrollback_lines: 50000  # Heavy users
```

### High CPU Usage

**Problem:** TUI consuming excessive CPU

**Diagnosis:**
```bash
# Monitor CPU usage
top -p $(pgrep -f par-term-emu-tui-rust)

# Check if rapid screen updates are occurring
# Common causes:
# - Applications with frequent updates (htop, btop, etc.)
# - Infinite loops printing to stdout
# - Cursor blink animation
```

**Solutions:**
```yaml
# Disable cursor blinking (reduces 60Hz timer)
cursor_blink_enabled: false

# Reduce scrollback (less memory to manage)
scrollback_lines: 1000

# Reduce mouse wheel scroll speed
mouse_wheel_scroll_lines: 1  # Reduce from default 3

# Note: Polling interval is optimized at 16ms (~60Hz)
# This is needed for responsive updates and smooth rendering
```

### Memory Issues

**Problem:** High memory consumption

**Solution:**
```yaml
# Limit scrollback
scrollback_lines: 5000
max_scrollback_lines: 10000

# Exit and restart periodically
exit_on_shell_exit: true
```

## Feature-Specific Issues

### Clipboard Not Working

**Problem:** Copy/paste doesn't work

**Platform-specific solutions:**

**macOS:**
```bash
# Uses pbcopy/pbpaste (built-in)
# No additional dependencies needed

# Verify clipboard access
echo "test" | pbcopy
pbpaste
```

**Linux:**
```bash
# Requires xclip or xsel for clipboard operations
# Install xclip (recommended)
sudo apt-get install xclip  # Debian/Ubuntu
sudo dnf install xclip      # Fedora
sudo pacman -S xclip        # Arch

# Or install xsel as alternative
sudo apt-get install xsel   # Debian/Ubuntu

# Test clipboard
echo "test" | xclip -selection clipboard
xclip -selection clipboard -o

# Test PRIMARY selection (for middle-click paste)
echo "test" | xclip -selection primary
xclip -selection primary -o

# For Wayland users
sudo apt-get install wl-clipboard
```

**Windows:**
```powershell
# Uses win32clipboard (built-in)
# Clipboard should work by default

# Verify PowerShell clipboard access
"test" | Set-Clipboard
Get-Clipboard
```

**Notes:**
- Uses pyperclip for cross-platform clipboard support
- On Linux, also copies to PRIMARY selection for middle-click paste
- Middle-click paste works with PRIMARY selection on Linux (requires xclip/xsel)
- Keyboard shortcuts:
  - Ctrl+Shift+C / Cmd+C: Copy selection
  - Ctrl+Shift+V / Cmd+V: Paste from clipboard
  - Ctrl+C (with selection): Copy selection
  - Ctrl+C (no selection): Send SIGINT to PTY
  - Middle-click: Paste PRIMARY selection (Linux)

### Screenshots Not Saving

**Problem:** Screenshot command doesn't create file

**Diagnosis:**
```bash
# Check default screenshot directory
# Priority: config > OSC 7 CWD > XDG_PICTURES_DIR/Screenshots > ~/Pictures/Screenshots > ~

# Check if default directory exists
ls -la ~/Pictures/Screenshots

# Check permissions
touch ~/Pictures/Screenshots/test.txt
rm ~/Pictures/Screenshots/test.txt
```

**Solution:**
```bash
# Create default directory
mkdir -p ~/Pictures/Screenshots

# Or set custom directory in config
# Edit ~/.config/par-term-emu-tui-rust/config.yaml
screenshot_directory: ~/my-screenshots

# Test screenshot
par-term-emu-tui-rust --screenshot 2 --auto-quit 4

# Check available formats
# Supported: png (default), jpeg, bmp, svg, html
# Set in config.yaml:
screenshot_format: png

# Auto-open after capture
# Set in config.yaml:
open_screenshot_after_capture: true
```

### Shell Integration Not Working

**Problem:** Status bar doesn't show current directory

**Diagnosis:**
```bash
# Check integration files
ls ~/.config/par-term-emu-tui-rust/shell-integration/

# Check shell profile sourcing
grep -r "shell-integration" ~/.bashrc ~/.zshrc ~/.config/fish/config.fish
```

**Solution:**
```bash
# Reinstall shell integration
par-term-emu-tui-rust install shell-integration --all

# Manually source (bash)
echo 'source ~/.config/par-term-emu-tui-rust/shell-integration/bash_integration.sh' >> ~/.bashrc

# Manually source (zsh)
echo 'source ~/.config/par-term-emu-tui-rust/shell-integration/zsh_integration.sh' >> ~/.zshrc

# Restart shell
exec $SHELL
```

### Keyboard Shows Escape Codes After TUI Apps

**Problem:** After exiting nvim, htop, or other TUI apps, keyboard input appears as codes like "8u 5u" or "105;5u"

**Status:** **FIXED** automatically as of v0.4.0

**How it's fixed:**
- Terminal core automatically resets keyboard protocol state when:
  - TUI apps exit alternate screen mode
  - Full terminal reset occurs
- No manual intervention needed

**If you still see this:**
1. Verify you're running v0.4.0 or later: `par-term-emu-tui-rust --version`
2. Try Ctrl+L to force screen refresh
3. As a workaround, type: `reset` and press Enter

**Background:**
Some TUI applications enable KITTY keyboard protocol for enhanced input but fail to disable it when exiting (due to crashes or improper cleanup). The terminal emulator now automatically cleans up this state to prevent corruption.

**Related:**
- See [KEYBOARD_PROTOCOL.md](KEYBOARD_PROTOCOL.md) for more details about KITTY keyboard protocol
- This was a common issue with applications that crash or don't handle signals properly

### Hyperlinks Not Clickable

**Problem:** URLs don't open when clicked

**Diagnosis:**
```yaml
# Check config (in ~/.config/par-term-emu-tui-rust/config.yaml)
clickable_urls: true  # Must be true to enable URL clicking
url_modifier: "ctrl"  # Default requires Ctrl+Click
allowed_url_schemes:  # Only these schemes are allowed
  - http
  - https
  - ftp
  - ftps
  - file
  - mailto
warn_on_unknown_url_scheme: true  # Warn when blocking URLs
```

**Solution:**
```bash
# Test URL detection
# OSC 8 hyperlinks (explicit)
echo -e '\e]8;;https://example.com\e\\Click me\e]8;;\e\\'

# Plain text URLs (auto-detected)
echo "https://github.com"

# Check modifier key requirement
# Default: Ctrl+Click
# Change in config.yaml:
url_modifier: "none"   # No modifier required
url_modifier: "ctrl"   # Ctrl+Click (default)
url_modifier: "shift"  # Shift+Click
url_modifier: "alt"    # Alt+Click

# Allow additional URL schemes
allowed_url_schemes:
  - http
  - https
  - ssh
  - vscode
```

### Mouse Selection Not Working

**Problem:** Can't select text with mouse

**Diagnosis:**
- Check if application has enabled mouse tracking (mouse events sent to app)
- When mouse tracking is on, terminal intercepts mouse events
- Test in different applications

**Solution:**
```bash
# When mouse tracking is enabled, use Shift+Click to select
# Shift + Click & Drag (bypasses mouse tracking)

# Double-click to select word
# Triple-click to select line

# Disable mouse tracking in applications:

# Vim/Neovim
:set mouse=

# Tmux
tmux set -g mouse off

# Htop
# Press F10 to open settings, disable mouse

# Configure word selection boundaries
# In config.yaml:
word_characters: "/-+\\~_."  # Default word boundary chars

# Configure selection behavior
auto_copy_selection: true           # Auto-copy on selection (default)
keep_selection_after_copy: true     # Keep selection visible (like iTerm2)
copy_trailing_newline: false        # Include \n when copying lines
```

## Platform-Specific Issues

### macOS Issues

**Problem:** Screenshot shortcut conflicts with system shortcuts

**Solution:**
```
System Settings → Keyboard → Keyboard Shortcuts → Screenshots
Disable conflicting shortcuts (e.g., Cmd+Shift+S)

# Terminal shortcuts
Ctrl+Shift+S - Screenshot
Ctrl+Shift+C - Copy
Ctrl+Shift+V - Paste
Cmd+C/V also work on macOS
```

**Problem:** Font not rendering properly

**Solution:**
```bash
# Install Hack font (recommended monospace font)
par-term-emu-tui-rust install font

# Font is installed to:
# ~/Library/Fonts/Hack-Regular.ttf (and variants)

# Restart terminal emulator to pick up new fonts
```

### Linux Issues

**Problem:** X11 clipboard not working

**Solution:**
```bash
# Install xclip (required for clipboard operations)
sudo apt-get install xclip   # Debian/Ubuntu
sudo dnf install xclip       # Fedora
sudo pacman -S xclip         # Arch

# For Wayland (alternative to X11)
sudo apt-get install wl-clipboard

# Verify clipboard tools
which xclip
which xsel

# Test clipboard
echo "test" | xclip -selection clipboard
xclip -selection clipboard -o

# Test PRIMARY selection (middle-click paste)
echo "test" | xclip -selection primary
xclip -selection primary -o
```

**Problem:** Permission denied for terminfo installation

**Solution:**
```bash
# User install (no sudo, installs to ~/.terminfo)
par-term-emu-tui-rust install terminfo

# System-wide install (requires sudo, installs to /usr/share/terminfo)
sudo par-term-emu-tui-rust install terminfo --system

# Verify installation
infocmp par-term
toe | grep par-term
```

### Windows Issues

**Problem:** Path too long error

**Solution:**
```powershell
# Enable long paths
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

**Problem:** Unicode characters not displaying

**Solution:**
```powershell
# Set console to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## Debug Mode

The application has three levels of debug logging:

1. **TUI Application Logs** - High-level application logic
2. **Python Core Logs** - Python bindings and widget integration
3. **Rust Core Logs** - Terminal emulation and PTY operations

See [DEBUG.md](DEBUG.md) for comprehensive debugging guide.

### Enable Debug Logging

**TUI Application Logs:**
```bash
# Enable TUI application debug logging
par-term-emu-tui-rust --debug

# Log location (timestamped files in current directory)
ls -l debug_logs/terminal_debug_*.log
```

**Core Debug Logs (Rust + Python Bindings):**
```bash
# Enable core debug logging with environment variable
DEBUG_LEVEL=3 par-term-emu-tui-rust --debug

# Rust core log location (terminal emulation, VT parsing, PTY)
/tmp/par_term_emu_core_rust_debug_rust.log

# Python core log location (bindings, widget integration)
/tmp/par_term_emu_core_rust_debug_python.log
```

**Makefile Shortcuts:**
```bash
make debug           # DEBUG_LEVEL=2 (info)
make debug-verbose   # DEBUG_LEVEL=3 (debug)
make debug-trace     # DEBUG_LEVEL=4 (trace - WARNING: huge logs)
make debug-tail      # View core logs in real-time
make debug-clear     # Clear core debug logs
```

### Debug Levels (Core Logs)

| Level | Name  | What's Logged |
|-------|-------|---------------|
| 0     | OFF   | Nothing (default) |
| 1     | ERROR | Critical issues, corruption detection |
| 2     | INFO  | Screen switches, device queries, widget lifecycle |
| 3     | DEBUG | VT sequences, generation tracking, render calls |
| 4     | TRACE | Every operation, full content, buffer snapshots |

### Debug Log Contents

**TUI Application Log (`debug_logs/terminal_debug_*.log`):**
- Configuration loading and validation
- Terminal initialization and lifecycle
- Key bindings and mouse events
- Screenshot operations and paths
- Error stack traces
- User interactions

**Python Core Log (`/tmp/par_term_emu_debug_python.log`):**
- Widget lifecycle (mount, unmount, resize)
- Render operations and generation tracking
- Corruption detection warnings
- Frame snapshot creation

**Rust Core Log (`/tmp/par_term_emu_core_rust_debug_rust.log`):**
- VT sequence parsing (CSI, OSC, ESC)
- PTY read/write operations
- Screen buffer switches (primary ↔ alternate)
- Terminal state changes
- Generation counter updates

### Analyzing Debug Logs

**TUI Application Logs:**
```bash
# Search for errors
grep -i error debug_logs/terminal_debug_*.log

# Search for warnings
grep -i warn debug_logs/terminal_debug_*.log

# View last 50 lines
tail -50 debug_logs/terminal_debug_*.log

# Real-time monitoring
tail -f debug_logs/terminal_debug_*.log
```

**Core Debug Logs:**
```bash
# Monitor both core logs in real-time
tail -f /tmp/par_term_emu_core_rust_debug_rust.log \
        /tmp/par_term_emu_debug_python.log

# Search for specific patterns
grep "SCREEN_SWITCH" /tmp/par_term_emu_core_rust_debug_rust.log
grep "CORRUPTION" /tmp/par_term_emu_debug_python.log
grep "VT_INPUT" /tmp/par_term_emu_core_rust_debug_rust.log

# Or use make shortcuts
make debug-tail  # Tail core logs
make debug-view  # View core logs with less
```

### Common Error Patterns

**Configuration Errors (TUI Application Log):**
```
ERROR: Failed to load config: ...
Failed to parse config file: invalid YAML syntax
```

**Terminal Errors (Core Logs):**
```
[ERROR] [PTY] Failed to spawn shell: ...
[ERROR] Terminal initialization failed
```

**Rendering Corruption (Python Core Log):**
```
[ERROR] [CORRUPTION] widget=terminal line=0 suspicious_content=[...]
[WARNING] rendering with stale generation
```

**Screenshot Errors (TUI Application Log):**
```
ERROR: Screenshot failed: Permission denied
Failed to create screenshot directory: ...
```

## Getting Help

### Before Asking for Help

1. **Check debug logs:**
   ```bash
   par-term-emu-tui-rust --debug
   cat debug_logs/terminal_debug_*.log
   ```

2. **Try with default config:**
   ```bash
   mv ~/.config/par-term-emu-tui-rust/config.yaml{,.backup}
   par-term-emu-tui-rust --init-config
   ```

3. **Test minimal case:**
   ```bash
   par-term-emu-tui-rust --auto-quit 2
   ```

4. **Check version:**
   ```bash
   par-term-emu-tui-rust --version
   python --version
   uv --version
   ```

### Information to Include

When reporting issues, include:

```bash
# System information
uname -a

# Python version
python --version

# Package version
par-term-emu-tui-rust --version

# Terminal emulator
echo $TERM
echo $TERM_PROGRAM

# Debug log (if applicable)
cat debug_logs/terminal_debug_*.log

# Configuration
cat ~/.config/par-term-emu-tui-rust/config.yaml
```

### Where to Get Help

**GitHub Issues:**
- URL: https://github.com/paulrobello/par-term-emu-tui-rust/issues
- For bug reports and feature requests
- Include system information and debug logs

**GitHub Discussions:**
- URL: https://github.com/paulrobello/par-term-emu-tui-rust/discussions
- For questions and general discussion
- Share tips and workflows

**Documentation:**
- Review all documentation in `docs/`
- Check [Debug FAQ](DEBUG.md#faq) for debugging questions
- See examples in README

## Quick Reference: Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Clipboard not working (Linux) | `sudo apt-get install xclip` |
| URLs not opening (default: Ctrl+Click) | Set `url_modifier: "none"` for click-only in config.yaml |
| Colors wrong | Check `theme` setting in config, try `--theme dark-background` |
| Mouse selection not working | Use Shift+Click when mouse tracking is enabled |
| Config file errors | Use interactive recovery or `--init-config` |
| Screenshot directory missing | Creates in ~/Pictures/Screenshots automatically |
| Shell integration not working | Run `par-term-emu-tui-rust install shell-integration` |
| Keyboard shows escape codes | Fixed in v0.4.0 - automatic reset on app exit |
| TUI crashes on startup | Check debug logs: `par-term-emu-tui-rust --debug` |

## Related Documentation

- [Quick Start Guide](QUICK_START.md) - Get started quickly
- [Configuration Reference](CONFIG_REFERENCE.md) - All settings
- [Debug Guide](DEBUG.md) - Advanced debugging
- [Features](FEATURES.md) - Complete feature list
- [Key Bindings](KEY_BINDINGS.md) - Keyboard shortcuts
- [Keyboard Protocol](KEYBOARD_PROTOCOL.md) - KITTY protocol details
- [Architecture](ARCHITECTURE.md) - System design and development guide
