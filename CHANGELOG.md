# Changelog

All notable changes to par-term-emu-tui-rust will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2025-01-19

### Added
- **Interactive Configuration Editor**: Comprehensive configuration UI accessible via `Alt+Ctrl+Shift+C`
  - Tabbed interface with Settings and Raw YAML editing modes
  - Widget-based form editor with 15 organized configuration sections
  - Immediate validation and type checking with descriptive help text
  - Syntax highlighting in Raw YAML tab with real-time validation
  - Automatic backup creation before saving changes
  - Restart reminder toast notification after configuration changes

- **Terminal Session Recording**: Full session recording with `Ctrl+Shift+R`
  - Recording indicator (⏺️) in header shows active status
  - Start/stop recording with single keypress toggle
  - Multiple export formats: Asciicast (.cast) and JSON (.json)
  - Smart directory selection with configurable fallbacks
  - Auto-export option to save immediately when recording stops
  - Customizable title templates with `{timestamp}` placeholder
  - Optional auto-open to launch recordings in default application

- **Backend Integration Enhancements**
  - Native notification control: bell sound volume, desktop notifications, visual bell
  - Activity/silence detection with configurable thresholds
  - Clipboard sync event limits (max events and bytes per event)
  - Shell integration statistics in status bar (commands, failures, average duration)

### Changed
- Configuration screen now uses tabbed interface instead of single-page form
- Recording directory selection now respects `XDG_VIDEOS_DIR` environment variable

## [0.4.0] - 2025-01-18

### Added
- **Automatic Config Backup**: Every config save creates timestamped backup (`config.yaml.backup.YYYYMMDD_HHMMSS`)
- **Interactive Recovery**: When config parsing fails, prompts for recovery options:
  - Reset to defaults
  - Restore from backup
  - View all available backups
  - Exit gracefully
- **Comprehensive Validation**: All config values validated for proper types, ranges, and formats
  - Numeric values (int/float) properly converted from YAML strings
  - Range clamping for float values (0.0-1.0) like `minimum_contrast`
  - Positive/non-negative validation for numeric settings
  - RGB tuple validation for color values
  - Enum validation for theme and screenshot format settings
- **Config UI Improvements**: Optimized widget widths for better layout
- **Restart Notification**: Toast message after saving config reminds user to restart TUI

### Changed
- **Bold Brightening Default**: Changed `bold_brightening` default from `true` to `false` for better color accuracy

### Fixed
- **Keyboard Protocol State Management**: Automatic reset when TUI applications exit alternate screen mode
  - Prevents keyboard corruption (escape codes like "8u 5u" appearing as input)
  - Fixed in Rust terminal core (`par-term-emu-core-rust`) for robust, automatic cleanup
  - No manual intervention needed after exiting nvim, htop, etc.

## [0.3.1] - 2025-01-15

### Added
- **Automatic Contrast Adjustment**: iTerm2-compatible minimum contrast system
  - `minimum_contrast` (0.0-1.0) - Automatic contrast adjustment for live display (default 0.5)
  - `faint_text_alpha` (0.0-1.0) - Alpha multiplier for faint/dim text (default 0.5)
  - `screenshot_minimum_contrast` (0.0-1.0 or null) - Independent contrast setting for screenshots
  - Uses NTSC perceived brightness formula for accurate readability
  - Ensures text remains readable on any background color

- **Bold Text Brightening**: Enhanced bold text rendering
  - `bold_brightening` (default: false) - Use bright ANSI colors (8-15) for bold text with normal colors (0-7)
  - Matches iTerm2's "Use Bright Bold" setting
  - When enabled: Bold red (1) automatically renders as bright red (9)
  - When disabled: Bold text uses original color without brightening

## [0.3.0] - 2025-01-10

### Added
- **Visual Bell Flash**: Animated bell icon overlay (🔔) when terminal receives BEL character
- **Install Command Discoverability**: `install` subcommand now visible in `--help` output
- **KITTY Keyboard Protocol Documentation**: Comprehensive guide for enhanced keyboard handling
- **Configuration Expansion**: 57 configuration options including color system, backend control, recording, and notification features
- **Better CLI Help**: Install subcommand now visible in main help output
- **Code Organization**: Added BellFlash widget for visual bell feedback
- **Backend Control Surface**: Status bar now surfaces shell integration stats

### Changed
- Enhanced documentation with install command references
- Updated USAGE.md with install command
- Updated CLAUDE.md with installation commands reference
- Updated all documentation to reflect new scrolling default

## [0.2.0] - 2025-01-05

### Added
- KITTY keyboard protocol support with auto-detection
- Improved code consistency and type safety across codebase

### Fixed
- Fixed all lint errors (22 → 0)
- Achieved 100% type checking compliance
- Enhanced test suite reliability with all 20 tests passing

## [0.1.0] - 2024-12-28

### Added
- Initial release
- Textual-based TUI terminal emulator
- Full ANSI support (16/256/true color)
- Scrollback buffer with keyboard and mouse navigation
- Mouse support (text selection, clickable URLs, mouse tracking)
- OSC 8 hyperlinks and auto-detected plain text URLs
- OSC 9/777 notification support with toast messages
- Shell integration with directory tracking
- Screenshots in multiple formats (PNG, SVG, HTML)
- 12 built-in themes with custom theme support
- Cross-platform clipboard support with OSC 52
- Efficient rendering using Textual Line API
- XDG-compliant configuration
