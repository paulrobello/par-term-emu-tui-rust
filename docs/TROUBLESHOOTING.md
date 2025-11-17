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
ERROR: Python 3.14 or higher required
```

**Solution:**
```bash
# Check Python version
python3 --version

# macOS (using Homebrew)
brew install python@3.14

# Linux (Ubuntu/Debian)
sudo apt-get install python3.14

# Linux (Fedora)
sudo dnf install python3.14

# Create alias
alias python=python3.14
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

# Or use make
make install

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
# Enable debug logging
par-term-emu-tui-rust --debug

# Check debug log
cat debug_logs/terminal_debug_*.log
```

**Common causes:**
1. Missing dependencies
2. Configuration file syntax errors
3. Terminal compatibility issues

**Solutions:**
```bash
# Reinstall dependencies
uv sync

# Reset configuration
rm ~/.config/par-term-emu-tui-rust/config.yaml
par-term-emu-tui-rust --init-config

# Test with minimal config
par-term-emu-tui-rust --auto-quit 2
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
```

**Solution:**
```bash
# Validate YAML syntax
python3 -c "import yaml, os; yaml.safe_load(open(os.path.expanduser('~/.config/par-term-emu-tui-rust/config.yaml'), encoding='utf-8'))"

# Or recreate default config
mv ~/.config/par-term-emu-tui-rust/config.yaml ~/.config/par-term-emu-tui-rust/config.yaml.backup
par-term-emu-tui-rust --init-config
```

## Display Problems

### Colors Not Showing

**Problem:** Terminal appears monochrome or colors incorrect

**Diagnosis:**
```bash
# Check TERM variable
echo $TERM

# Test true color
printf "\x1b[38;2;255;100;0mTRUECOLOR\x1b[0m\n"
```

**Solution:**
```bash
# Set TERM variable
export TERM=xterm-256color

# Or for true color
export TERM=xterm-256color

# Add to shell profile
echo 'export TERM=xterm-256color' >> ~/.bashrc
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
scrollback_lines: 1000  # Reduce from 10000

# Or disable unlimited scrollback
scrollback_lines: 5000
max_scrollback_lines: 10000
```

### High CPU Usage

**Problem:** TUI consuming excessive CPU

**Diagnosis:**
```bash
# Monitor CPU usage
top -p $(pgrep -f par-term-emu-tui-rust)
```

**Solutions:**
```yaml
# Disable cursor blinking
cursor_blink_enabled: false

# Reduce scrollback
scrollback_lines: 1000

# Disable mouse tracking in apps
# vim: :set mouse=
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
# No additional dependencies needed
# Verify clipboard access
echo "test" | pbcopy
pbpaste
```

**Linux:**
```bash
# Install xclip
sudo apt-get install xclip  # Debian/Ubuntu
sudo dnf install xclip      # Fedora
sudo pacman -S xclip        # Arch

# Test clipboard
echo "test" | xclip -selection clipboard
xclip -selection clipboard -o
```

**Windows:**
```powershell
# Clipboard should work by default
# Verify PowerShell clipboard access
"test" | Set-Clipboard
Get-Clipboard
```

### Screenshots Not Saving

**Problem:** Screenshot command doesn't create file

**Diagnosis:**
```bash
# Check screenshot directory
ls -la ~/Pictures/Screenshots

# Check permissions
touch ~/Pictures/Screenshots/test.txt
rm ~/Pictures/Screenshots/test.txt
```

**Solution:**
```bash
# Create directory
mkdir -p ~/Pictures/Screenshots

# Set in config
echo "screenshot_directory: ~/Pictures/Screenshots" >> ~/.config/par-term-emu-tui-rust/config.yaml

# Test screenshot
par-term-emu-tui-rust --screenshot 2 --auto-quit 4
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

### Hyperlinks Not Clickable

**Problem:** URLs don't open when clicked

**Diagnosis:**
```yaml
# Check config
clickable_urls: true  # Should be true
url_modifier: "none"  # Or required modifier key
```

**Solution:**
```bash
# Test URL detection
echo -e '\e]8;;https://example.com\e\\Click me\e]8;;\e\\'
echo "https://github.com"

# Check modifier key requirement
# If url_modifier: "ctrl", must Ctrl+Click
```

### Mouse Selection Not Working

**Problem:** Can't select text with mouse

**Diagnosis:**
- Check if application has enabled mouse tracking
- Test in different applications

**Solution:**
```bash
# For selection when mouse tracking enabled, use Shift
# Shift + Click & Drag

# Disable mouse tracking in vim
:set mouse=

# Disable mouse tracking in tmux
tmux set -g mouse off
```

## Platform-Specific Issues

### macOS Issues

**Problem:** Screenshot shortcut conflicts

**Solution:**
```
System Settings → Keyboard → Keyboard Shortcuts
Disable conflicting shortcuts
```

**Problem:** Font not rendering

**Solution:**
```bash
# Install Hack font
par-term-emu-tui-rust install font

# Verify font
fc-list | grep Hack

# Restart terminal app
```

### Linux Issues

**Problem:** X11 clipboard not working

**Solution:**
```bash
# Install xclip
sudo apt-get install xclip

# For Wayland
sudo apt-get install wl-clipboard
```

**Problem:** Permission denied for terminfo

**Solution:**
```bash
# User install (no sudo)
par-term-emu-tui-rust install terminfo

# System install (with sudo)
sudo par-term-emu-tui-rust install terminfo --system
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

### Enable Debug Logging

```bash
# Start with debug logging
par-term-emu-tui-rust --debug

# Log location (timestamped files)
ls -l debug_logs/terminal_debug_*.log
```

### Debug Log Contents

**Useful information in logs:**
- Configuration loading
- Terminal initialization
- Key events
- Mouse events
- Screenshot operations
- Error stack traces

### Analyzing Debug Logs

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

### Common Error Patterns

**Configuration errors:**
```
ERROR: Failed to load config: ...
```

**Terminal errors:**
```
ERROR: Terminal initialization failed
```

**Screenshot errors:**
```
ERROR: Screenshot failed: ...
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
- Check [FAQ](#) for common questions
- See examples in README

## Related Documentation

- [Quick Start Guide](QUICK_START.md) - Get started quickly
- [Installation Guide](INSTALLATION.md) - Installation help
- [Configuration Reference](CONFIG_REFERENCE.md) - All settings
- [Debug Guide](DEBUG.md) - Advanced debugging
- [Features](FEATURES.md) - Complete feature list
- [Contributing](CONTRIBUTING.md) - Development setup
