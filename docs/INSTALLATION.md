# Installation Guide

Complete installation instructions for Par Term Emu TUI Rust, including dependencies, setup, and post-installation configuration.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Post-Installation Setup](#post-installation-setup)
- [Component Installation](#component-installation)
- [Verification](#verification)
- [Troubleshooting Installation](#troubleshooting-installation)
- [Related Documentation](#related-documentation)

## Prerequisites

Before installing Par Term Emu TUI Rust, ensure your system meets these requirements:

### Required Software

| Requirement | Minimum Version | Check Command |
|-------------|----------------|---------------|
| Python | 3.12 | `python --version` |
| uv | Latest | `uv --version` |
| Terminal | True color support | See below |

### Verify Terminal Capabilities

**Check true color support:**
```bash
# Test 24-bit color
printf "\x1b[38;2;255;100;0mTRUECOLOR\x1b[0m\n"
```

If you see "TRUECOLOR" in orange, your terminal supports true color.

**Recommended terminals:**
- **macOS**: iTerm2, Wezterm, Alacritty
- **Linux**: Alacritty, Kitty, Wezterm, GNOME Terminal
- **Windows**: Windows Terminal, Wezterm

### System Dependencies

**macOS:**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Linux:**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install clipboard support dependencies (optional)
sudo apt-get install xclip  # Debian/Ubuntu
sudo dnf install xclip      # Fedora
sudo pacman -S xclip        # Arch
```

**Windows:**
```powershell
# Install uv if not already installed
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation

### Install from Source

**Clone and install:**
```bash
# Clone the repository
git clone https://github.com/paulrobello/par-term-emu-tui-rust.git
cd par-term-emu-tui-rust

# Install dependencies
uv sync

# Or use make
make install
```

### Install from PyPI

> **📝 Note:** PyPI installation coming soon. Currently install from source.

```bash
# Future: Install from PyPI (not yet available)
uv pip install par-term-emu-tui-rust
```

### Development Installation

For development with editable install:

```bash
# Clone repository
git clone https://github.com/paulrobello/par-term-emu-tui-rust.git
cd par-term-emu-tui-rust

# Install with development dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

## Post-Installation Setup

After installation, install additional components for enhanced functionality.

### Quick Setup (Recommended)

Install all components with one command:

```bash
# Install terminfo, shell integration, and font
par-term-emu-tui-rust install all
```

This installs:
- Terminfo definition for optimal compatibility
- Shell integration for enhanced features
- Hack font for screenshot support

### Verify Installation

```bash
# Check installed version
par-term-emu-tui-rust --version

# Test basic functionality
par-term-emu-tui-rust --auto-quit 2
```

## Component Installation

### Terminfo Definition

Install the par-term terminfo definition for optimal terminal compatibility.

**User installation (recommended):**
```bash
par-term-emu-tui-rust install terminfo
```

**System-wide installation:**
```bash
# Requires sudo/administrator privileges
sudo par-term-emu-tui-rust install terminfo --system
```

**Verify installation:**
```bash
# Check terminfo is installed
infocmp par-term

# Should display terminfo definition
```

**What it does:**
- Defines terminal capabilities for par-term
- Enables proper application behavior
- Provides correct key mapping

### Shell Integration

Install shell integration for enhanced terminal features.

```mermaid
graph LR
    Install[Install Integration]
    Source[Source in Shell]
    Features[Enhanced Features]

    Install --> Source
    Source --> Features

    style Install fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style Source fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style Features fill:#e65100,stroke:#ff9800,stroke-width:3px,color:#ffffff
```

**Auto-detect current shell:**
```bash
# Installs for $SHELL
par-term-emu-tui-rust install shell-integration
```

**Install for all shells:**
```bash
# Installs for bash, zsh, and fish
par-term-emu-tui-rust install shell-integration --all
```

**Install for specific shell:**
```bash
# Bash
par-term-emu-tui-rust install shell-integration bash

# Zsh
par-term-emu-tui-rust install shell-integration zsh

# Fish
par-term-emu-tui-rust install shell-integration fish
```

**Activate integration:**
```bash
# Restart shell
exec $SHELL

# Or manually source (bash/zsh)
source ~/.par_term_emu_core_rust_shell_integration.bash
source ~/.par_term_emu_core_rust_shell_integration.zsh

# Fish automatically loads from config
```

**Features provided:**
- Current working directory tracking (OSC 7)
- Prompt navigation markers
- Command status tracking
- Enhanced terminal title

### Font for Screenshots

Install Hack font for optimal screenshot rendering.

```bash
par-term-emu-tui-rust install font
```

**Installation location:** `~/.local/share/fonts/Hack/`

**License:** MIT/Bitstream Vera License

**What it does:**
- Provides monospace font for screenshots
- Ensures consistent text rendering
- Supports extended Unicode characters

**Verify installation:**
```bash
# List installed fonts (macOS)
fc-list | grep Hack

# List installed fonts (Linux)
fc-list | grep Hack

# Windows: Check Fonts in Control Panel
```

### Installation Help

Get detailed help for any component:

```bash
# General help
par-term-emu-tui-rust install --help

# Component-specific help
par-term-emu-tui-rust install terminfo --help
par-term-emu-tui-rust install shell-integration --help
par-term-emu-tui-rust install font --help
```

## Verification

### Test Installation

**Basic functionality test:**
```bash
# Run for 2 seconds then quit
par-term-emu-tui-rust --auto-quit 2
```

**Test with command:**
```bash
# Inject command and screenshot
par-term-emu-tui-rust --command "echo 'Hello World'" --screenshot 1 --auto-quit 3
```

**Verify components:**
```bash
# Check terminfo
infocmp par-term

# Check shell integration files
ls ~/.par_term_emu_core_rust_shell_integration.*

# Check font
fc-list | grep Hack
```

### Configuration Test

**Create default config:**
```bash
par-term-emu-tui-rust --init-config
```

**Verify config location:**
```bash
# macOS/Linux
cat ~/.config/par-term-emu-tui-rust/config.yaml

# Windows
type %APPDATA%\par-term-emu-tui-rust\config.yaml
```

## Troubleshooting Installation

### Python Version Issues

**Problem:** `python: command not found` or wrong version

**Solution:**
```bash
# Check Python version
python3 --version

# If 3.12+, create alias
alias python=python3

# Or install Python 3.12+
# macOS (using Homebrew)
brew install python@3.12

# Linux (using apt)
sudo apt-get install python3.12

# Windows: Download from python.org
```

### UV Not Found

**Problem:** `uv: command not found`

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.cargo/bin:$PATH"

# Reload shell
exec $SHELL
```

### Permission Errors

**Problem:** Permission denied during installation

**Solution:**
```bash
# User installation (no sudo required)
par-term-emu-tui-rust install terminfo

# For system-wide, use sudo
sudo par-term-emu-tui-rust install terminfo --system

# Fix file permissions
chmod +x ~/.local/bin/par-term-emu-tui-rust
```

### Dependency Conflicts

**Problem:** Conflicting package versions

**Solution:**
```bash
# Clean and reinstall
rm -rf .venv
uv sync

# Or force reinstall
uv sync --reinstall
```

### Shell Integration Not Loading

**Problem:** Shell integration features not working

**Solution:**
```bash
# Reinstall for current shell
par-term-emu-tui-rust install shell-integration --all

# Manually source (bash example)
echo 'source ~/.par_term_emu_core_rust_shell_integration.bash' >> ~/.bashrc

# Restart shell
exec $SHELL
```

### Font Not Available

**Problem:** Hack font not showing up

**Solution:**
```bash
# Reinstall font
par-term-emu-tui-rust install font

# Rebuild font cache (Linux)
fc-cache -f -v

# Restart applications that use fonts
```

## Related Documentation

- [Quick Start Guide](QUICK_START.md) - Get started in 5 minutes
- [Configuration Reference](CONFIG_REFERENCE.md) - All configuration options
- [Usage Guide](USAGE.md) - Running and using the TUI
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Contributing](CONTRIBUTING.md) - Development setup
