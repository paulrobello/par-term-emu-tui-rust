# TUI Configuration Reference

Comprehensive reference for par-term-emu-tui-rust TUI application configuration options and settings.

## Table of Contents

- [Overview](#overview)
- [Configuration File Location](#configuration-file-location)
- [Currently Implemented Settings](#currently-implemented-settings)
- [Selection & Clipboard](#selection--clipboard)
- [Mouse & Pointer](#mouse--pointer)
- [Cursor Configuration](#cursor-configuration)
- [Scrollback Configuration](#scrollback-configuration)
- [Paste Behavior](#paste-behavior)
- [Focus & Interaction](#focus--interaction)
- [Security Settings](#security-settings)
- [Theme Configuration](#theme-configuration)
- [Notification Settings](#notification-settings)
- [Screenshot Configuration](#screenshot-configuration)
- [Hyperlinks & URLs](#hyperlinks--urls)
- [UI Elements](#ui-elements)
- [Shell Behavior](#shell-behavior)
- [Related Documentation](#related-documentation)

---

## Overview

The TUI application settings are stored in a YAML configuration file and control the application experience. These settings are managed by the `TuiConfig` Python dataclass.

**Configuration layers:**
- **TUI Layer** (this document): Application-level settings managed by `TuiConfig` in Python
- **Terminal Core**: Low-level terminal emulator settings (see [par-term-emu-core-rust documentation](https://github.com/paulrobello/par-term-emu-core-rust))

**Key Distinction**: TUI settings control the *application experience* (selection, clipboard, themes), while core settings control the *terminal emulation behavior* (VT modes, color parsing).

---

## Configuration File Location

**XDG-compliant path:**
- Linux/macOS: `~/.config/par-term-emu-tui-rust/config.yaml`
- Configuration is type-safe with Python dataclasses
- Backward compatible (new fields use defaults)
- Auto-created on first run with default values

### Editing Configuration

**Built-in Config Editor (Recommended):**

Press **Alt+Ctrl+Shift+C** while the TUI is running to open the interactive config editor:
- **Syntax highlighting**: YAML syntax highlighting with Monokai theme
- **Live validation**: Checks YAML syntax before saving
- **Auto-creation**: Creates config file with defaults if it doesn't exist
- **Keyboard shortcuts**:
  - `Ctrl+S` or click "Save" button to save changes
  - `Escape` or click "Cancel" to discard changes
- **Line numbers**: Easy navigation with line numbers
- **Tab behavior**: Smart indentation for YAML editing

**Manual Editing:**

```bash
# Edit with your preferred editor
$EDITOR ~/.config/par-term-emu-tui-rust/config.yaml

# Or use command-line flag
par-term-emu-tui-rust --init-config  # Creates default config
```

---

## Currently Implemented Settings

**Implementation Status** (Last Updated: 2025-11-16):
- ✅ **32 options fully implemented**

| Setting | Config Key | Default | Notes |
|---------|-----------|---------|-------|
| Auto-copy selection | `auto_copy_selection` | `true` | Copies on double/triple-click and shift+drag |
| Keep selection after copy | `keep_selection_after_copy` | `true` | iTerm2-like behavior |
| Expose clipboard to apps | `expose_system_clipboard` | `true` | OSC 52 clipboard access |
| Copy trailing newline | `copy_trailing_newline` | `false` | Adds \\n when copying lines |
| Word characters | `word_characters` | `"/-+\\~_."` | iTerm2-compatible word boundaries for double-click |
| Triple-click wrapped lines | `triple_click_selects_wrapped_lines` | `true` | Intelligent line selection following wraps |
| Scrollback lines | `scrollback_lines` | `10000` | Configurable scrollback buffer |
| Max scrollback (safety) | `max_scrollback_lines` | `100000` | Safety limit for unlimited |
| Cursor blink enabled | `cursor_blink_enabled` | `false` | Cursor blinking with timer |
| Cursor blink rate | `cursor_blink_rate` | `0.5` | Configurable blink interval |
| Cursor style | `cursor_style` | `"blinking_block"` | Block/underline/bar with blink variants |
| Paste chunk size | `paste_chunk_size` | `0` | Chunked paste for large content |
| Paste chunk delay | `paste_chunk_delay_ms` | `10` | Delay between chunks |
| Paste warn size | `paste_warn_size` | `100000` | Warn before large paste |
| Focus follows mouse | `focus_follows_mouse` | `false` | Auto-focus on mouse enter |
| Middle-click paste | `middle_click_paste` | `true` | Paste on middle mouse button |
| Mouse wheel scroll lines | `mouse_wheel_scroll_lines` | `3` | Lines to scroll per wheel tick |
| Disable insecure sequences | `disable_insecure_sequences` | `false` | Blocks OSC 8/52/9/777 and Sixel when enabled |
| Accept OSC 7 | `accept_osc7` | `true` | Directory tracking via shell integration |
| Visual bell enabled | `visual_bell_enabled` | `true` | Shows bell icon (🔔) in header on BEL character |
| Theme | `theme` | `"dark-background"` | Color theme name |
| Show notifications | `show_notifications` | `true` | Display OSC 9/777 notifications |
| Notification timeout | `notification_timeout` | `5` | Notification display duration (seconds) |
| Screenshot directory | `screenshot_directory` | `None` | Directory for screenshots |
| Screenshot format | `screenshot_format` | `"png"` | Format: png, jpeg, svg, bmp, html |
| Open screenshot after capture | `open_screenshot_after_capture` | `false` | Auto-open with system viewer |
| Exit on shell exit | `exit_on_shell_exit` | `true` | Exit TUI when shell exits |
| Clickable URLs | `clickable_urls` | `true` | Enable clicking URLs to open in browser |
| Link color | `link_color` | `[100, 150, 255]` | RGB color for hyperlinks (blue) |
| URL modifier key | `url_modifier` | `"none"` | Required modifier: none, ctrl, shift, alt |
| Search match color | `search_match_color` | `[255, 255, 0]` | RGB color for search highlights (yellow) |
| Show status bar | `show_status_bar` | `true` | Show/hide status bar at bottom |

---

## Selection & Clipboard

### Overview

These settings control how text selection and clipboard operations work in the TUI.

### Selection Behavior Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `auto_copy_selection` | `bool` | `true` | Automatically copy selected text to clipboard |
| `keep_selection_after_copy` | `bool` | `true` | Keep text highlighted after copying |
| `copy_trailing_newline` | `bool` | `false` | Include trailing newline when copying full lines |
| `word_characters` | `str` | `"/-+\\~_."` | Characters considered part of a word for double-click selection (iTerm2-compatible) |
| `triple_click_selects_wrapped_lines` | `bool` | `true` | Triple-click selects full wrapped lines vs just visible line |

### Clipboard Access

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `expose_system_clipboard` | `bool` | `true` | Allow applications to access clipboard via OSC 52 |

**Security Note**: OSC 52 clipboard write access is controlled here.

### Example Configuration

```yaml
# Selection & Clipboard
auto_copy_selection: true
keep_selection_after_copy: true
expose_system_clipboard: true
copy_trailing_newline: false
word_characters: "/-+\\~_."  # iTerm2-compatible (for URL-friendly: "-_.~:/?#[]@!$&'()*+,;=")
triple_click_selects_wrapped_lines: true
```

---

## Mouse & Pointer

### Mouse Behavior Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `focus_follows_mouse` | `bool` | `false` | Automatically focus terminal on mouse enter |
| `middle_click_paste` | `bool` | `true` | Paste on middle mouse button click (PRIMARY selection on Linux) |
| `mouse_wheel_scroll_lines` | `int` | `3` | Number of lines to scroll per mouse wheel tick |

### Example Configuration

```yaml
# Mouse & Focus
focus_follows_mouse: false       # Don't auto-focus on hover
middle_click_paste: true         # Enable middle-click paste
mouse_wheel_scroll_lines: 3      # Scroll 3 lines per tick
```

---

## Cursor Configuration

### Cursor Visual Settings

| Setting | Type | Default | Options | Description |
|---------|------|---------|---------|-------------|
| `cursor_blink_enabled` | `bool` | `false` | - | Enable cursor blinking animation |
| `cursor_blink_rate` | `float` | `0.5` | > 0 | Blink interval in seconds |
| `cursor_style` | `str` | `"blinking_block"` | See below | Cursor appearance |

### Cursor Style Options

- `"block"` - Solid block cursor
- `"blinking_block"` - Blinking block cursor
- `"underline"` - Solid underline cursor
- `"blinking_underline"` - Blinking underline cursor
- `"bar"` - Solid vertical bar cursor
- `"blinking_bar"` - Blinking vertical bar cursor

### Example Configuration

```yaml
# Cursor
cursor_blink_enabled: true
cursor_blink_rate: 0.5  # 500ms
cursor_style: "blinking_block"
```

---

## Scrollback Configuration

### Scrollback Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `scrollback_lines` | `int` | `10000` | Number of lines to keep in scrollback (0 = unlimited) |
| `max_scrollback_lines` | `int` | `100000` | Safety limit when unlimited is enabled |

**Notes:**
- `scrollback_lines = 0` enables unlimited scrollback (up to `max_scrollback_lines`)
- Scrollback is only available in the primary screen (not alternate screen)
- Memory usage: ~100 bytes per line (approximate)

### Example Configuration

```yaml
# Scrollback
scrollback_lines: 10000      # Keep 10k lines
max_scrollback_lines: 100000 # Safety limit
```

---

## Paste Behavior

### Paste Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `paste_chunk_size` | `int` | `0` | Paste in chunks of N bytes (0 = no chunking) |
| `paste_chunk_delay_ms` | `int` | `10` | Delay between chunks in milliseconds |
| `paste_warn_size` | `int` | `100000` | Warn before pasting more than N bytes |

**Chunked Paste**: Useful for large clipboard content that might overwhelm the shell or application.

### Example Configuration

```yaml
# Paste
paste_chunk_size: 0           # No chunking by default
paste_chunk_delay_ms: 10      # 10ms delay if chunking enabled
paste_warn_size: 100000       # Warn on >100KB pastes
```

---

## Focus & Interaction

### Focus Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `focus_follows_mouse` | `bool` | `false` | Auto-focus terminal on mouse enter |

### Example Configuration

```yaml
# Focus
focus_follows_mouse: false
```

---

## Security Settings

### Security Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `disable_insecure_sequences` | `bool` | `false` | Block potentially dangerous escape sequences |
| `accept_osc7` | `bool` | `true` | Accept OSC 7 directory tracking |

### Disabled Sequences When `disable_insecure_sequences = true`

When enabled, the following escape sequences are blocked by the terminal core:
- **OSC 8** - Hyperlinks (clickable URLs in terminal output)
- **OSC 52** - Clipboard operations (read/write access to system clipboard)
- **OSC 9** - iTerm2 notifications (simple notification messages)
- **OSC 777** - urxvt notifications (rich notifications with title and message)
- **Sixel graphics** - Inline images (bitmap graphics embedded in terminal)

**Security Implications:**
- OSC 52 can allow malicious applications to read sensitive clipboard data
- OSC 8 hyperlinks could redirect to malicious URLs
- Sixel graphics can consume significant memory and CPU

**Recommendation**: Enable `disable_insecure_sequences: true` in untrusted or sandboxed environments.

### OSC 7 Directory Tracking

**Purpose**: Allows terminal applications (typically shells) to report their current working directory to the TUI.

**Benefits:**
- Enables the status bar to display the current directory
- Used by shell integration (zsh, bash with proper hooks)
- Helps terminal know where to save screenshots (when `screenshot_directory: null`)

**Implementation**:
- The terminal core accepts OSC 7 sequences when `accept_osc7: true`
- Directory changes are tracked via `shell_integration_state()`
- TUI receives directory updates through polling

**Security**: Generally safe to keep enabled as it only receives information, doesn't grant control.

### Example Configuration

```yaml
# Security Settings
disable_insecure_sequences: false  # Allow all sequences (default)
accept_osc7: true                   # Enable directory tracking (default)

# For untrusted environments
# disable_insecure_sequences: true
# accept_osc7: false
```

---

## Theme Configuration

### Theme Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `theme` | `str` | `"dark-background"` | Color theme name to use for terminal colors |

**Available Themes:**
- Use `par-term-emu-tui-rust --list-themes` to see all available themes
- Themes control the terminal's color palette and appearance

### Example Configuration

```yaml
# Theme
theme: "dark-background"  # Default dark theme
```

---

## Notification Settings

### Notification Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `show_notifications` | `bool` | `true` | Display OSC 9/777 notifications as toast messages |
| `notification_timeout` | `int` | `5` | Duration in seconds to display notifications |

**Notes:**
- OSC 9 provides simple notifications (message only)
- OSC 777 provides rich notifications (title + message)
- Terminal applications can trigger desktop-style notifications
- Notifications appear as toast overlays in the TUI

### Example Configuration

```yaml
# Notifications
show_notifications: true      # Enable notification toasts
notification_timeout: 5       # Auto-dismiss after 5 seconds
```

---

## Screenshot Configuration

### Screenshot Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `screenshot_directory` | `str \| None` | `None` | Directory to save screenshots (None = auto-detect) |
| `screenshot_format` | `str` | `"png"` | File format: `"png"`, `"jpeg"`, `"bmp"`, `"svg"`, `"html"` |
| `open_screenshot_after_capture` | `bool` | `false` | Automatically open screenshot with system viewer |

**Screenshot Directory Auto-Detection** (when `None`):
1. Shell's current working directory (from OSC 7)
2. XDG_PICTURES_DIR/Screenshots
3. ~/Pictures/Screenshots
4. Home directory

**Screenshot Format Options:**
- `png` - Lossless, best for text (default)
- `jpeg` - Smaller file size, lossy compression
- `bmp` - Uncompressed, large file size
- `svg` - Vector format, infinitely scalable with selectable text
- `html` - Full HTML document with inline styles, viewable in browsers

### Example Configuration

```yaml
# Screenshots
screenshot_directory: null             # Auto-detect directory
screenshot_format: "png"               # PNG format
open_screenshot_after_capture: false   # Don't auto-open
```

---

## Hyperlinks & URLs

### Overview

Control how clickable hyperlinks work in the terminal.

### Hyperlink Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `clickable_urls` | `bool` | `true` | Enable clicking URLs to open in browser |
| `link_color` | `tuple[int, int, int]` | `(100, 150, 255)` | RGB color for hyperlinks (blue) |
| `url_modifier` | `str` | `"none"` | Modifier key required for URL clicks |

**URL Detection:**
- **OSC 8 Hyperlinks**: Properly formatted URLs with OSC 8 escape sequences
- **Plain Text URLs**: Auto-detected http://, https://, ftp://, and other common schemes

**Modifier Key Options:**
- `"none"` - Click URLs directly without any modifier
- `"ctrl"` - Require Ctrl+Click to open URLs
- `"shift"` - Require Shift+Click to open URLs
- `"alt"` - Require Alt+Click to open URLs

### Search Highlighting

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `search_match_color` | `tuple[int, int, int]` | `(255, 255, 0)` | RGB color for search match highlights |

**Notes:**
- This setting prepares for future search feature implementation
- Color is specified as RGB tuple with values 0-255
- Default is yellow for high visibility

### Example Configuration

```yaml
# Hyperlinks & URLs
clickable_urls: true                 # Enable URL clicking
link_color: [100, 150, 255]         # Blue hyperlinks
url_modifier: "none"                # No modifier required (click directly)

# Search Highlighting
search_match_color: [255, 255, 0]   # Yellow search matches
```

### Usage Examples

```bash
# Create OSC 8 hyperlink
echo -e '\e]8;;https://example.com\e\\Click me!\e]8;;\e\\'

# Plain URL (auto-detected)
echo "Visit https://github.com"
```

---

## UI Elements

### Overview

These settings control the visibility and behavior of UI elements in the terminal application.

### UI Element Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `show_status_bar` | `bool` | `true` | Show or hide the status bar at the bottom |
| `visual_bell_enabled` | `bool` | `true` | Enable visual bell indicator (bell icon in header) |

**Status Bar Notes:**
- When `true`: Status bar is visible and can display information like current directory (OSC 7)
- When `false`: Status bar is completely hidden to maximize terminal space
- The status bar is always present in the DOM for runtime toggling, but hidden via CSS when disabled
- Changes to this setting require restarting the application

**Visual Bell Notes:**
- When `true`: Bell icon (🔔) appears in header when terminal receives BEL character (`\x07`)
- When `false`: Bell events are ignored (no visual feedback)
- Bell icon clears on next keyboard input or mouse click
- Provides non-intrusive visual notification without audio

### Example Configuration

```yaml
# UI Elements
show_status_bar: true        # Show status bar (default)
visual_bell_enabled: true    # Enable visual bell indicator (default)
```

---

## Shell Behavior

### Shell Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `exit_on_shell_exit` | `bool` | `true` | Exit TUI application when shell exits |

**Notes:**
- When `true`: TUI exits immediately when the shell process exits
- When `false`: Displays exit message and allows restart with Ctrl+Shift+R
- Useful for reviewing output after shell exits or debugging

### Example Configuration

```yaml
# Shell Behavior
exit_on_shell_exit: true  # Exit immediately when shell exits
```

---

## Related Documentation

- [README.md](../README.md) - TUI application overview and usage guide
- [DEBUG.md](DEBUG.md) - TUI debugging guide
- [Core Library Documentation](https://github.com/paulrobello/par-term-emu-core-rust) - Terminal emulator core features
