# PAR TERM EMU TUI RUST - Architecture Document

Comprehensive architecture documentation for the par-term-emu-tui-rust terminal user interface, detailing system design, components, data flows, and implementation patterns.

## Table of Contents
- [Overview](#overview)
- [Architecture Layers](#architecture-layers)
  - [Application Layer](#1-application-layer-terminalapp)
  - [Terminal Widget Layer](#2-terminal-widget-layer-terminalwidget)
  - [Rendering System](#3-rendering-system-renderer)
  - [Selection System](#4-selection-system-selectionmanager)
  - [Clipboard System](#5-clipboard-system-clipboardmanager)
  - [Screenshot System](#6-screenshot-system-screenshotmanager)
  - [Theme System](#7-theme-system-themespy--theme_managerpy)
  - [Configuration System](#8-configuration-system-tuiconfig)
  - [Message System](#9-message-system-messagespy)
  - [Supporting Widgets](#10-supporting-widgets)
- [Data Flow Diagrams](#data-flow-diagrams)
  - [Update/Render Flow](#updaterender-flow)
  - [Input/Write Flow](#inputwrite-flow)
  - [Shell Integration Flow](#shell-integration-flow)
  - [Message Flow Architecture](#message-flow-architecture)
- [Key Design Patterns](#key-design-patterns)
- [Threading & Concurrency](#threading--concurrency)
- [Performance Characteristics](#performance-characteristics)
- [Extension Points](#extension-points)
- [Key Features Implementation](#key-features-implementation)
- [Configuration Loading Chain](#configuration-loading-chain)
- [Debugging Infrastructure](#debugging-infrastructure)
- [Technology Stack](#technology-stack)
- [Conclusion](#conclusion)
- [Related Documentation](#related-documentation)

---

## Overview

**par-term-emu-tui-rust** is a Textual-based terminal user interface (TUI) that wraps the **par-term-emu-core-rust** terminal emulator library. It provides an interactive shell environment within a Python TUI framework, with advanced features including text selection, clipboard management, themes, screenshots, and shell integration.

**Key Technologies:**
- Python 3.14
- Textual 6.6.0+ (TUI framework)
- par-term-emu-core-rust 0.2.3+ (Rust terminal emulator backend)
- PyYAML 6.0.3+ (configuration management)
- xdg-base-dirs 6.0.2+ (XDG directory compliance)
- pyperclip 1.11.0+ (cross-platform clipboard)

**Project Structure:**
```
par-term-emu-tui-rust/
├── src/par_term_emu_tui_rust/
│   ├── app.py                          # Main Textual application
│   ├── config.py                       # Configuration management (TuiConfig)
│   ├── messages.py                     # Custom Textual messages
│   ├── themes.py                       # Color theme definitions (11 built-in themes)
│   ├── utils.py                        # Utility functions
│   ├── installer.py                    # Installation script handler
│   ├── terminal_widget/
│   │   ├── __init__.py
│   │   ├── terminal_widget.py          # Main TerminalWidget class (1480 lines)
│   │   ├── rendering.py                # Renderer class for line-based rendering
│   │   ├── selection.py                # SelectionManager for text selection
│   │   ├── clipboard.py                # ClipboardManager for clipboard ops
│   │   ├── screenshot.py               # ScreenshotManager for screenshot capture
│   │   └── theme_manager.py            # Apply themes to terminal
│   └── widgets/
│       ├── __init__.py
│       ├── status_bar.py               # StatusBar widget (directory display)
│       └── flash_line.py               # FlashLine widget (flash messages)
├── tests/
├── pyproject.toml
├── README.md
├── docs/
│   ├── DEBUG.md                        # Comprehensive debugging guide
│   ├── CONFIG_REFERENCE.md             # Configuration options reference
│   ├── DOCUMENTATION_STYLE_GUIDE.md    # Documentation standards
│   └── ARCHITECTURE.md                 # This file
└── Makefile
```

---

## Architecture Layers

### 1. Application Layer (`TerminalApp`)

**File:** `app.py`

The top-level Textual application that manages the overall UI structure and application lifecycle.

**Key Responsibilities:**
- Compose UI hierarchy (Header, TerminalWidget, StatusBar, FlashLine, Footer)
- Handle application-level key bindings (Ctrl+Shift+Q to quit)
- Manage screenshot capture and auto-quit timers
- Process custom messages from child widgets (Directory changes, title changes, flash notifications)
- Parse and handle command-line arguments
- Manage theme operations (list, export, apply themes)
- Disable default Ctrl+Q and Ctrl+C bindings to let them pass to the terminal

**Key Methods:**
- `__init__()` - Initialize with optional shell command, config, and debug settings
- `compose()` - Create child widgets (Header, TerminalWidget, StatusBar, FlashLine, Footer)
- `on_mount()` - Schedule screenshot and auto-quit timers
- `_take_screenshot()` - Capture terminal buffer to file (PNG/JPEG/SVG/HTML/BMP)
- `_auto_quit()` - Exit application after delay
- `on_flash()` - Handle Flash messages from child widgets
- `on_directory_changed()` - Handle OSC 7 directory change messages
- `on_title_changed()` - Handle OSC 0/1/2 title change messages
- `flash()` - Display transient flash message to user
- `main()` - Entry point with full CLI argument parsing

**Configuration Integration:**
- Loads `TuiConfig` from YAML (XDG_CONFIG_HOME)
- Passes config to TerminalWidget
- Respects theme override from CLI (`--theme` flag)

**Message Flow:**
- Receives `DirectoryChanged` messages → updates StatusBar
- Receives `TitleChanged` messages → updates app sub_title
- Receives `Flash` messages → displays via FlashLine widget

---

### 2. Terminal Widget Layer (`TerminalWidget`)

**File:** `terminal_widget/terminal_widget.py` (1480 lines)

The core custom Textual widget that wraps `par_term_emu_core_rust.PtyTerminal` and provides interactive shell access with advanced terminal features.

**Inheritance:** `Widget` with `can_focus=True`

**Key Responsibilities:**
- Wrap PtyTerminal (Rust terminal emulator backend)
- Manage PTY lifecycle (spawn shell, write input, kill process)
- Poll for PTY updates using generation tracking
- Render terminal content using Textual's Line API
- Handle all user input (keyboard and mouse)
- Manage text selection and clipboard
- Implement scrollback buffer navigation
- Apply themes and configure cursor styles
- Handle shell integration (OSC 7, OSC 0/1/2)
- Manage cursor blinking

**Threading Model:**

```mermaid
graph TB
    subgraph "PTY Reader Thread - Rust Backend"
        A[Read from PTY socket]
        B[Parse VT sequences]
        C[Update terminal grid/scrollback]
        D[Increment update_generation]
        A --> B --> C --> D
    end

    D -->|atomic counter| E[Shared Memory<br/>Generation Counter]

    subgraph "Textual Event Loop - Main Python Thread"
        E --> F[_poll_updates<br/>every 16ms]
        F --> G{Generation<br/>changed?}
        G -->|Yes| H[Create atomic snapshot]
        H --> I[Schedule debounced<br/>refresh 5ms]
        I --> J[_do_refresh]
        J --> K[render_line for<br/>each visible line]
        K --> L[Return Rich Segments]

        M[on_key /<br/>on_mouse_*] --> N[Handle selection/<br/>clipboard]
        N --> O[Write to PTY]
    end

    L --> P[Terminal Display]

    style A fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style D fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style E fill:#ff6f00,stroke:#ffa726,stroke-width:2px,color:#ffffff
    style F fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style K fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style P fill:#2e7d32,stroke:#66bb6a,stroke-width:2px,color:#ffffff
```

**Generation Tracking Pattern:**

The widget uses atomic generation counters to detect when PTY content has changed:

```python
# In PTY reader thread (Rust):
self.term.update_generation()  # Increments on each update

# In Textual event loop:
current_gen = self.term.update_generation()
if self.term.has_updates_since(self.last_update_generation):
    self.last_update_generation = current_gen
    self.refresh()  # Schedule render
```

**Key Attributes:**

```python
# Terminal dimensions (reactive)
terminal_cols: int = 80
terminal_rows: int = 24

# PTY instance
term: PtyTerminal  # Rust terminal emulator

# State tracking
_scroll_offset: int          # Lines scrolled up from bottom (0 = at bottom)
_at_bottom: bool             # True if viewing live output
_rendering_ready: bool       # False until widget has non-zero size
_was_alt_screen: bool        # Tracks primary ↔ alternate screen switching
_cursor_blink_visible: bool  # Current blink state

# Shell integration state
_last_known_directory: str   # From OSC 7
_last_known_title: str       # From OSC 0/1/2

# Generation tracking
last_update_generation: int  # Last PTY generation we processed
render_generation: int       # Generation being rendered (atomic snapshot)

# Managers (composition)
selection: SelectionManager
clipboard: ClipboardManager
screenshot: ScreenshotManager
renderer: Renderer
```

**Key Methods:**

```python
# Lifecycle
on_mount()                    # Spawn shell, apply theme, start polling
on_unmount()                  # Stop polling, kill shell
on_resize(event)              # Resize PTY and widget on window resize

# Update polling
_poll_updates()               # Check for PTY updates (called every 16ms)
_do_refresh()                 # Execute debounced refresh

# Rendering
render_line(y) -> Strip       # Render one line of terminal content

# Input handling
async on_key(event)           # Handle keyboard input
async on_mouse_down(event)    # Handle mouse press (selection, URL clicks)
async on_mouse_move(event)    # Handle mouse move (selection drag)
async on_mouse_up(event)      # Handle mouse release
async on_mouse_scroll_*()     # Handle scrollback navigation

# Actions (key bindings)
action_copy_selection()       # Copy selected text to clipboard
action_paste_clipboard()      # Paste from clipboard to PTY
action_save_screenshot()      # Save screenshot
action_scroll_up/down/top/bottom()  # Navigate scrollback

# PTY communication
_send_shell_command()         # Send scheduled command after 1s delay
_send_mouse_event()           # Send SGR mouse events to PTY
_toggle_cursor_blink()        # Toggle cursor visibility

# Helpers
_get_cell_metrics()           # Get pixel metrics from environment
```

**Configuration Integration:**

The widget accepts a `TuiConfig` object and respects 30 configuration options including scrollback_lines, cursor settings, clipboard behavior, mouse handling, security options, theme selection, notifications, screenshots, and URL handling.

**Message Production:**

- Posts `DirectoryChanged(directory)` when OSC 7 cwd changes
- Posts `TitleChanged(title)` when OSC 0/1/2 title changes
- Posts `Flash(content, style, duration)` for notifications

**Key Bindings:**

```
Ctrl+Shift+C        Copy selection
Ctrl+Shift+V        Paste from clipboard
Ctrl+Shift+S        Save screenshot
Ctrl+Shift+PageUp   Scroll up one page
Ctrl+Shift+PageDown Scroll down one page
Shift+Home          Scroll to top
Shift+End           Scroll to bottom
```

---

### 3. Rendering System (`Renderer`)

**File:** `terminal_widget/rendering.py`

Handles efficient line-by-line rendering of terminal content to Rich Segments, with support for colors, text attributes, selections, cursor, hyperlinks, and graphics (Sixel).

**Key Responsibilities:**
- Create atomic frame snapshots from terminal state
- Pre-fetch all lines from snapshot (optimization)
- Render each line with colors, attributes, selections, cursor, hyperlinks
- Handle wide characters (CJK)
- Render Sixel graphics as Unicode half-blocks
- Cache color conversions and style objects

**Key Methods:**

```python
def prepare_frame(widget_id: str)
    # Create atomic snapshot of terminal state
    # Pre-fetch all lines to avoid per-line cloning
    # Clear hyperlink cache for new frame

def render_line(y, widget_id, widget_size, rendering_ready) -> Strip
    # Render a single line using the prepared frame snapshot
    # Apply selection highlighting
    # Apply cursor if on this line
    # Apply hyperlink styling
    # Handle Sixel graphics
    # Return Rich Strip with Segments

def _render_graphic_line(graphic, row, term_cols) -> list[Segment]
    # Render Sixel graphic using Unicode half-blocks
    # Top pixel = foreground color
    # Bottom pixel = background color
```

**Optimization Techniques:**

- **LRU Cache (1024)** for `_rgb_to_hex()` - avoids repeated string formatting
- **LRU Cache (512)** for `_create_style()` - reuses Style objects
- **Pre-fetch all lines** in `prepare_frame()` - reduces Rust→Python FFI calls
- **Frame-level snapshot** - prevents stale rendering during alternate screen switches
- **Hyperlink cache** - per-frame cache of detected links

**Color Handling:**

```python
def _rgb_to_hex(r: int, g: int, b: int) -> str
    # Convert RGB to "#rrggbb" hex string (cached)

def _create_style(...) -> Style
    # Create Rich Style with color, bgcolor, bold, italic, etc. (cached)
```

**Selection Rendering:**

When a selection exists (`selection.start` and `selection.end`), the renderer highlights the selected region with:
- Selection background color
- Selection text color
- Spans multiple lines if needed

---

### 4. Selection System (`SelectionManager`)

**File:** `terminal_widget/selection.py`

Manages text selection state and operations for the terminal widget.

**Key Responsibilities:**
- Track selection start/end positions (col, row)
- Detect double-click (word selection)
- Detect triple-click (line selection)
- Handle shift+click to extend selection
- Provide selected text to clipboard manager
- Clear selection on input

**Key Methods:**

```python
def __init__(term, config, get_terminal_cols)
def clear()
def select_word_at(col, row, frame_snapshot)
def select_line(row, term_cols)
def select_region(start, end)
def set_selection(start, end)
def get_selected_text(frame_snapshot) -> str
```

**Selection State:**

```python
self.start: tuple[int, int] | None  # (col, row) or None
self.end: tuple[int, int] | None    # (col, row) or None
self.selecting: bool                # True during mouse drag
```

**Word Boundary Detection:**

Uses terminal's native `get_word_at(col, row, word_characters)` method which respects the configured `word_characters` setting (default: `"/-+\\~_."`).

---

### 5. Clipboard System (`ClipboardManager`)

**File:** `terminal_widget/clipboard.py`

Manages clipboard operations with cross-platform support.

**Key Responsibilities:**
- Copy selected text to system clipboard
- Handle trailing newline option
- Copy to X11 PRIMARY selection on Linux (for middle-click paste)
- Provide feedback on success/failure

**Key Methods:**

```python
def copy_to_clipboard(text, to_primary=True) -> tuple[bool, str | None]
    # Copy using pyperclip (Windows/macOS/Linux)
    # Also copy to PRIMARY on Linux if requested

def _copy_to_primary(text)
    # Linux-only: copy to X11 PRIMARY selection
    # Uses xclip or xsel
```

**Cross-Platform Support:**
- **Windows:** win32clipboard
- **macOS:** pbcopy
- **Linux:** xclip/xsel (with fallback)
- pyperclip handles all abstraction

---

### 6. Screenshot System (`ScreenshotManager`)

**File:** `terminal_widget/screenshot.py`

Manages screenshot capture with smart directory detection and multiple format support.

**Key Responsibilities:**
- Determine save directory (config → OSC 7 cwd → XDG_PICTURES_DIR → home)
- Capture terminal buffer in multiple formats
- Generate timestamped filenames
- Notify user of success/failure

**Supported Formats:**
- PNG (lossless, default)
- JPEG (lossy, smaller file size)
- BMP (uncompressed)
- SVG (vector, infinitely scalable)
- HTML (full document with inline styles)

**Key Methods:**

```python
def get_directory() -> str
    # Smart directory detection with fallback chain

def capture_screenshot(format) -> str
    # Capture to file, return path
```

---

### 7. Theme System (`themes.py` + `theme_manager.py`)

**File:** `themes.py`

Defines the `Theme` dataclass and 11 built-in color themes compatible with iTerm2.

**Theme Components:**

```python
@dataclass
class Theme:
    name: str
    palette: list[str]         # 16 ANSI colors (hex)
    background: str            # Default background
    foreground: str            # Default foreground
    cursor: str                # Cursor color
    cursor_text: str           # Text color under cursor
    selection: str             # Selection background
    selection_text: str        # Selection text color
    link: str                  # Hyperlink color
    bold: str                  # Bold text color
    cursor_guide: str          # Vertical cursor guide
    underline: str             # Underline color
    badge: str                 # Badge color
    match: str                 # Search match highlight
```

**Built-in Themes:**
1. `dark-background` (default)
2. `high-contrast`
3. `light-background`
4. `pastel-dark`
5. `regular`
6. `smoooooth`
7. `solarized`
8. `solarized-dark`
9. `solarized-light`
10. `tango-dark`
11. `tango-light`

Custom themes can be created in `~/.config/par-term-emu-tui-rust/themes/`

**File:** `terminal_widget/theme_manager.py`

Applies themes to the terminal instance.

**Key Functions:**

```python
def apply_theme(term: PtyTerminal, config: TuiConfig)
    # Set ANSI palette (0-15)
    # Set default colors (fg, bg)
    # Set cursor colors
    # Set selection colors
    # Set link/bold/underline/badge/match colors

def apply_cursor_style(term: PtyTerminal, config: TuiConfig)
    # Map config string to CursorStyle enum
    # Apply to terminal

def parse_color(color_hex: str) -> tuple[int, int, int]
    # Convert "#rrggbb" to RGB tuple
```

---

### 8. Configuration System (`TuiConfig`)

**File:** `config.py`

Manages application configuration with YAML persistence and XDG directory compliance.

**Key Responsibilities:**
- Define configuration schema as Python dataclass
- Load/save from/to YAML files
- Use XDG_CONFIG_HOME (~/.config/)
- Provide sensible defaults
- Validate configuration on load

**Configuration Storage:**

```
~/.config/par-term-emu-tui-rust/config.yaml
```

**30 Configuration Options:**

**Selection & Clipboard:**
- `auto_copy_selection` - Copy on selection complete (default: true)
- `keep_selection_after_copy` - Keep visible after copy (default: true)
- `expose_system_clipboard` - Allow apps to read clipboard (default: true)
- `copy_trailing_newline` - Add newline when copying (default: false)
- `word_characters` - Word boundary chars (default: `"/-+\\~_."`)
- `triple_click_selects_wrapped_lines` - Follow wrapping (default: true)

**Scrollback & Cursor:**
- `scrollback_lines` - Keep N lines (0=unlimited up to max) (default: 10000)
- `max_scrollback_lines` - Safety limit (default: 100000)
- `cursor_blink_enabled` - Enable blinking (default: false)
- `cursor_blink_rate` - Interval in seconds (default: 0.5)
- `cursor_style` - Visual style (default: `"blinking_block"`)

**Paste:**
- `paste_chunk_size` - Chunk size in bytes (0=no chunking) (default: 0)
- `paste_chunk_delay_ms` - Delay between chunks (default: 10)
- `paste_warn_size` - Warn before pasting > N bytes (default: 100000)

**Mouse & Focus:**
- `focus_follows_mouse` - Auto-focus on hover (default: false)
- `middle_click_paste` - Paste on middle click (default: true)
- `mouse_wheel_scroll_lines` - Lines per wheel tick (default: 3)

**Security:**
- `disable_insecure_sequences` - Filter risky sequences (default: false)
- `accept_osc7` - Allow directory tracking (default: true)

**Theme & Appearance:**
- `theme` - Theme name (default: `"dark-background"`)
- `show_status_bar` - Show status bar (default: true)

**Notifications:**
- `show_notifications` - Display OSC 9/777 toasts (default: true)
- `notification_timeout` - Toast duration seconds (default: 5)

**Screenshots:**
- `screenshot_directory` - Save directory (default: auto-detect)
- `screenshot_format` - File format (default: `"png"`)
- `open_screenshot_after_capture` - Auto-open viewer (default: false)

**Hyperlinks & URLs:**
- `clickable_urls` - Enable URL clicking (default: true)
- `link_color` - RGB tuple (default: `(100, 150, 255)`)
- `url_modifier` - Required modifier (default: `"none"`)

**Shell Behavior:**
- `exit_on_shell_exit` - Exit TUI when shell exits (default: true)

**Key Methods:**

```python
@classmethod
def load(config_path=None) -> TuiConfig
    # Load from YAML, use defaults for missing keys

def save(config_path=None)
    # Save to YAML

@staticmethod
def default_config_path() -> Path
    # Return XDG_CONFIG_HOME/par-term-emu-tui-rust/config.yaml

def to_dict() -> dict[str, Any]
    # Convert to dictionary
```

---

### 9. Message System (`messages.py`)

**File:** `messages.py`

Custom Textual message types for inter-widget communication.

**Message Types:**

```python
@dataclass
class Flash(Message):
    """Request a transient flash message.

    Args:
        content: Message content
        style: Semantic style (default, warning, success, error)
        duration: Display duration seconds (or None for default)
    """
    content: str | Content
    style: Literal["default", "warning", "success", "error"]
    duration: float | None = None


@dataclass
class DirectoryChanged(Message):
    """Terminal directory changed via OSC 7.

    Args:
        directory: The new working directory path
    """
    directory: str


@dataclass
class TitleChanged(Message):
    """Terminal title changed via OSC 0/1/2.

    Args:
        title: The new title
    """
    title: str
```

---

### 10. Supporting Widgets

#### StatusBar (`widgets/status_bar.py`)

Displays information at the bottom of the TUI (directory from OSC 7).

**CSS Classes:**
- `.status_bar.-default`
- `.status_bar.-success`
- `.status_bar.-warning`
- `.status_bar.-error`

**Key Methods:**

```python
def update_content(content, style="default")
    # Update display with styled content
```

#### FlashLine (`widgets/flash_line.py`)

Overlay widget for transient flash messages (notifications, clipboard feedback).

**CSS:**
- Position: top of screen as overlay
- Visibility: initially hidden
- Auto-hide after duration

**Key Methods:**

```python
def flash(content, duration=None, style="default")
    # Flash message for specified duration
    # Auto-hide after timeout
```

---

## Data Flow Diagrams

### Update/Render Flow

```mermaid
sequenceDiagram
    participant PTY as PTY Reader<br/>Thread (Rust)
    participant Gen as update_generation<br/>(atomic)
    participant Poll as _poll_updates()<br/>[16ms timer]
    participant Refresh as _do_refresh()
    participant Render as render_line(y)
    participant Display as Terminal<br/>Display

    PTY->>PTY: Read from PTY socket
    PTY->>PTY: Parse VT sequences
    PTY->>PTY: Update grid/scrollback
    PTY->>Gen: Increment generation

    Poll->>Gen: Read current generation
    Gen-->>Poll: generation value

    alt Generation changed
        Poll->>Poll: Check alt screen switch
        Poll->>Poll: Check notifications (OSC 9/777)
        Poll->>Poll: Check directory change (OSC 7)
        Poll->>Poll: Check title change (OSC 0/1/2)
        Poll->>Refresh: Schedule debounced refresh (5ms)

        Refresh->>Refresh: prepare_frame() - Create atomic snapshot
        Refresh->>Render: refresh() - Trigger render cycle

        loop For each visible line
            Render->>Render: Get line from snapshot
            Render->>Render: Apply colors & attributes
            Render->>Render: Apply selection
            Render->>Render: Apply cursor
            Render->>Render: Handle hyperlinks
            Render-->>Display: Return Rich Strip
        end
    end
```

### Input/Write Flow

```mermaid
graph TD
    A[User Input] --> B{Input Type}

    B -->|Keyboard| C[on_key event]
    C --> D{Special Key?}
    D -->|Copy Ctrl+C/Cmd+C| E[Copy selection<br/>to clipboard]
    D -->|Paste Ctrl+V/Cmd+V| F[Paste from<br/>clipboard]
    D -->|Other| G[Map to escape<br/>sequence]
    E --> H[Post Flash<br/>message]
    F --> I[term.write_str text]
    G --> I

    B -->|Mouse| J{Mouse Event}
    J -->|Down| K[on_mouse_down]
    K --> L{Click Type}
    L -->|Double| M[Select word]
    L -->|Triple| N[Select line]
    L -->|Shift+Click| O[Extend selection]
    L -->|URL+Modifier| P[Open URL<br/>in browser]
    L -->|Normal| Q[Start selection]

    J -->|Move| R[on_mouse_move]
    R --> S{Selecting?}
    S -->|Yes| T[Extend selection]
    S -->|No & Mouse Tracking| U[Send mouse<br/>event to PTY]

    J -->|Up| V[on_mouse_up]
    V --> W[End selection]
    W --> X{Auto copy?}
    X -->|Yes| E

    J -->|Scroll| Y[on_mouse_scroll<br/>_up/down]
    Y --> Z[Navigate<br/>scrollback]

    I --> AA[PTY stdin]
    AA --> AB[Shell]
    U --> AA

    style E fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style H fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style P fill:#ff6f00,stroke:#ffa726,stroke-width:2px,color:#ffffff
    style AB fill:#2e7d32,stroke:#66bb6a,stroke-width:2px,color:#ffffff
```

### Shell Integration Flow

```mermaid
graph LR
    A[Terminal App<br/>bash/zsh] --> B{Sequence Type}

    B -->|OSC 7| C["OSC 7 sequence<br/>file://host/path"]
    C --> D[par_term_emu parses]
    D --> E[Stores in<br/>shell_integration_state]
    E --> F[_poll_updates<br/>detects change]
    F --> G[Posts DirectoryChanged<br/>message]
    G --> H[TerminalApp<br/>.on_directory_changed]
    H --> I[Updates<br/>StatusBar]

    B -->|OSC 0/1/2| J["OSC 0/1/2 sequence<br/>title"]
    J --> K[par_term_emu parses]
    K --> L[Stores in<br/>title]
    L --> M[_poll_updates<br/>detects change]
    M --> N[Posts TitleChanged<br/>message]
    N --> O[TerminalApp<br/>.on_title_changed]
    O --> P[Updates<br/>app.sub_title]

    B -->|OSC 9/777| Q[Notification sequence]
    Q --> R[par_term_emu parses]
    R --> S[Stores in<br/>notification queue]
    S --> T[_poll_updates calls<br/>drain_notifications]
    T --> U[app.notify -<br/>displays toast]

    style C fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style I fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style P fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style U fill:#ff6f00,stroke:#ffa726,stroke-width:2px,color:#ffffff
```

### Message Flow Architecture

```mermaid
graph TB
    subgraph "TerminalWidget"
        A[Detect OSC 7<br/>directory change] --> B[Post DirectoryChanged<br/>message]
        C[Detect OSC 0/1/2<br/>title change] --> D[Post TitleChanged<br/>message]
        E[Clipboard/Screenshot<br/>operation] --> F[Post Flash<br/>message]
    end

    subgraph "TerminalApp"
        B --> G[on_directory_changed<br/>handler]
        D --> H[on_title_changed<br/>handler]
        F --> I[on_flash<br/>handler]

        G --> J[Update StatusBar<br/>widget]
        H --> K[Update app.sub_title<br/>header]
        I --> L[Update FlashLine<br/>widget]
    end

    J --> M[Display directory<br/>in status bar]
    K --> N[Display title<br/>in header]
    L --> O[Display flash<br/>message overlay]

    style B fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style D fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style F fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style M fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style N fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style O fill:#ff6f00,stroke:#ffa726,stroke-width:2px,color:#ffffff
```

---

## Key Design Patterns

### 1. Atomic Snapshot Pattern

The renderer uses atomic snapshots to prevent race conditions during rendering:

```python
# In _poll_updates():
self.renderer.prepare_frame(widget_id)  # Creates atomic snapshot

# Later, in render_line():
# All line renders use the same snapshot
# No risk of alternate screen switch happening mid-render
```

**Why?** Without snapshots, if the PTY switches screens between render_line(0) and render_line(23), different lines could come from different screen buffers (corruption).

### 2. Generation Tracking Pattern

Uses atomic counters to detect when content has changed:

```python
current_gen = self.term.update_generation()
if self.term.has_updates_since(self.last_update_generation):
    # Content changed, need to refresh
    self.refresh()
```

**Why?** Avoids polling the entire screen on every timer tick. Only refreshes when content actually changed.

### 3. Debounced Refresh Pattern

Batches rapid successive updates:

```python
# In _poll_updates():
if self._refresh_timer is not None:
    self._refresh_timer.stop()  # Cancel previous timer

# Schedule refresh after 5ms delay
self._refresh_timer = self.set_timer(0.005, self._do_refresh)
```

**Why?** Prevents partial rendering during scrollbar drags and other rapid updates. Multiple generation changes coalesce into one render cycle.

### 4. Callable Dependency Pattern

Managers receive callables to access widget state:

```python
self.renderer = Renderer(
    term=self.term,
    get_terminal_cols=lambda: self.terminal_cols,
    get_selection_start=lambda: self.selection.start,
    get_cursor_blink_visible=lambda: self._cursor_blink_visible,
)
```

**Why?** Avoids circular dependencies and late binding of state. Renderer always reads current state when rendering.

### 5. Manager Composition Pattern

Feature-specific functionality isolated in manager classes:

```python
self.selection = SelectionManager(...)
self.clipboard = ClipboardManager(...)
self.screenshot = ScreenshotManager(...)
self.renderer = Renderer(...)
```

**Why?** Clean separation of concerns. Each manager handles one aspect. Easy to test and extend.

### 6. Reactive Attributes Pattern

Textual's reactive system for dimension tracking:

```python
terminal_cols = reactive(80)
terminal_rows = reactive(24)

def watch_terminal_cols(self, cols: int):
    """Called when terminal_cols changes"""
    # Resize PTY if not in initialization
```

**Why?** Automatic synchronization between widget and PTY dimensions. Watchers prevent action during initialization via `_resizing` guard.

---

## Threading & Concurrency

### Thread Safety Analysis

| Component | Thread(s) | Safety |
|-----------|-----------|--------|
| PTY Reader | Rust thread | Only updates atomic counter |
| Textual Event Loop | Main Python thread | All widget methods run here |
| update_generation | Atomic (lock-free) | Safe from both threads |
| Terminal grid | Protected by Rust | Only PTY thread modifies |
| Snapshots | Copy-on-read | Immutable for render_line() |

### Critical Sections

1. **generation counter** - Read/write from both threads (atomic)
2. **snapshot** - Created in event loop, read during render (no threading during render)
3. **_scroll_offset** - Only read/written in event loop (safe)

### No Race Conditions Because:

- Only atomic operations between threads
- All UI updates happen in event loop
- Snapshots are immutable during render phase
- Generation tracking prevents stale rendering

---

## Performance Characteristics

### Rendering Performance

- **Line API** - Only renders visible lines (60-80 lines max on screen)
- **Snapshot pre-fetch** - All lines loaded once per frame (not per render_line call)
- **LRU caching** - Colors (1024) and Styles (512) cached
- **Debounced refresh** - Multiple updates coalesce (prevents excessive renders)

**Frame Rate:** ~60 Hz (Textual updates ~17ms per frame)

### Memory Usage

- **Scrollback buffer** - Configurable (default 10,000 lines)
- **Snapshot** - One atomic copy per frame (~200 cells × 24 = ~5KB each)
- **Caches** - LRU color cache (1024 entries) and style cache (512 entries)

### Polling Efficiency

- **Poll interval** - 16ms (60 Hz) matches typical display refresh rate
- **Generation-based** - Only refreshes when content changes
- **Debounce delay** - 5ms allows rapid updates to batch

---

## Extension Points

### Adding a New Manager

```python
# 1. Create manager class
class MyManager:
    def __init__(self, term, config, get_terminal_cols):
        self.term = term
        self.config = config
        self.get_terminal_cols = get_terminal_cols

    def my_method(self):
        pass

# 2. Initialize in TerminalWidget.__init__()
self.my_manager = MyManager(
    term=self.term,
    config=self.config,
    get_terminal_cols=lambda: self.terminal_cols,
)

# 3. Use in widget methods
self.my_manager.my_method()
```

### Adding a New Message Type

```python
# 1. Define in messages.py
@dataclass
class MyMessage(Message):
    """Custom message."""
    data: str

# 2. Post from widget
self.post_message(MyMessage(data="something"))

# 3. Handle in app
@on(MyMessage)
def on_my_message(self, event: MyMessage):
    event.stop()
    # Process event
```

### Adding a New Theme

```yaml
# ~/.config/par-term-emu-tui-rust/themes/my-theme.yaml
name: My Theme
palette:
  - "#000000"
  - "#ff0000"
  # ... (14 more colors)
background: "#000000"
foreground: "#ffffff"
cursor: "#ffffff"
cursor_text: "#000000"
selection: "#0066ff"
selection_text: "#ffffff"
link: "#0645ad"
bold: "#ffffff"
cursor_guide: "#a6e8ff"
underline: "#ffffff"
badge: "#ff0000"
match: "#ffff00"
```

Then use: `par-term-emu-tui-rust --theme my-theme`

---

## Key Features Implementation

### 1. Text Selection

**Flow:**
1. User Shift+clicks and drags
2. `on_mouse_down()` starts selection
3. `on_mouse_move()` extends selection
4. `on_mouse_up()` finalizes and optionally copies
5. `renderer.render_line()` applies highlighting

**Code Path:**
- `TerminalWidget.on_mouse_down()` → `SelectionManager.set_selection()`
- `renderer.render_line()` → checks `selection.start/end` → applies colors

### 2. Clipboard Operations

**Copy:**
1. Text selected
2. User presses Ctrl+Shift+C or releases mouse
3. `SelectionManager.get_selected_text()` extracts text
4. `ClipboardManager.copy_to_clipboard()` writes to system clipboard
5. On Linux: also copies to X11 PRIMARY selection

**Paste:**
1. User presses Ctrl+Shift+V or middle-clicks
2. `ClipboardManager` reads from clipboard
3. `term.write_str(text)` sends to PTY

### 3. Scrollback Navigation

**Scroll up:**
1. User presses Shift+PageUp
2. `action_scroll_up()` increases `_scroll_offset`
3. `renderer` renders lines from scrollback buffer
4. Visual shows previous output

**Scroll down:**
1. User presses Shift+PageDown
2. `action_scroll_down()` decreases `_scroll_offset`
3. When `_scroll_offset == 0`, shows live output

### 4. Cursor Blinking

**If enabled:**
1. `on_mount()` starts `_cursor_blink_timer`
2. Timer calls `_toggle_cursor_blink()` every `cursor_blink_rate` seconds
3. Toggles `_cursor_blink_visible` boolean
4. `renderer.render_line()` checks flag
5. Only blinks for BlinkingBlock/BlinkingUnderline/BlinkingBar styles

### 5. URL Clicking

**Detection:**
1. User clicks on terminal
2. `on_mouse_down()` detects click position
3. `renderer.render_line()` tracks hyperlink spans (OSC 8 + plain text URLs)
4. Check if click is within hyperlink region
5. Check for required modifier (ctrl/shift/alt/none)
6. Call `webbrowser.open(url)`

### 6. Shell Integration

**Directory tracking (OSC 7):**
1. Shell sends ESC ] 7 ; file://hostname/path ST
2. `par_term_emu` parses and stores in `shell_integration_state()`
3. `_poll_updates()` checks for change
4. Posts `DirectoryChanged` message
5. App updates StatusBar with directory

**Title tracking (OSC 0/1/2):**
1. App sends ESC ] 0/1/2 ; title ST
2. `par_term_emu` parses and stores in `title()`
3. `_poll_updates()` checks for change
4. Posts `TitleChanged` message
5. App updates header with title

### 7. Notifications (OSC 9/777)

**Flow:**
1. App sends ESC ] 9 ; message ST or ESC ] 777 ; title ; message ST
2. `par_term_emu` stores in notification queue
3. `_poll_updates()` calls `drain_notifications()`
4. App calls `self.notify(message, timeout=config.notification_timeout)`
5. Textual displays as toast message

---

## Configuration Loading Chain

```mermaid
graph LR
    A[CLI Arguments<br/>Highest Priority] -->|--theme override| B[Override Config]
    A -->|--config custom path| C[Custom Config File]

    C --> D[config.yaml in<br/>XDG_CONFIG_HOME]
    B --> D

    D -->|~/.config/par-term-emu-tui-rust/<br/>config.yaml| E[TuiConfig.load]

    E --> F{Missing keys?}
    F -->|Yes| G[Defaults from<br/>dataclass<br/>Lowest Priority]
    F -->|No| H[Fully Loaded<br/>Config]
    G --> H

    H --> I[Pass to<br/>TerminalWidget]

    style A fill:#2e7d32,stroke:#66bb6a,stroke-width:2px,color:#ffffff
    style D fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style G fill:#ff6f00,stroke:#ffa726,stroke-width:2px,color:#ffffff
    style I fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
```

**Config Flow:**
```python
# In app.py main():
if config is None:
    config = TuiConfig.load()  # Load from ~/.config/...

if theme_override:
    config.theme = theme_override  # CLI overrides file

# Pass to TerminalWidget:
app = TerminalApp(config=config, ...)
```

---

## Debugging Infrastructure

### Debug Levels (0-4)

Set `DEBUG_LEVEL` environment variable:

```bash
DEBUG_LEVEL=3 python -m par_term_emu_tui_rust
```

**Logs to separate files:**
- `/tmp/par_term_emu_debug_rust.log` - Core terminal emulation (Rust)
- `/tmp/par_term_emu_debug_python.log` - TUI widget operations (Python)

### Available Debug Methods

```python
from par_term_emu_core_rust.debug import (
    debug_log,          # General logging
    debug_trace,        # Detailed trace (level 4)
    log_generation_check,      # Generation tracking
    log_widget_lifecycle,      # Widget mount/unmount/resize
    log_render_call,    # Render call details
    log_render_content, # Rendered line content
    log_screen_corruption,     # Corruption detection
)
```

---

## Summary: Component Relationships

```mermaid
graph TB
    subgraph "Application Layer"
        App[TerminalApp<br/>app.py]
        App --> Header[Header Widget]
        App --> Term[TerminalWidget]
        App --> Status[StatusBar Widget]
        App --> Flash[FlashLine Widget]
        App --> Footer[Footer Widget]
    end

    subgraph "TerminalWidget - Core"
        Term --> PTY[PtyTerminal<br/>Rust Backend]
        Term --> Sel[SelectionManager]
        Term --> Clip[ClipboardManager]
        Term --> Shot[ScreenshotManager]
        Term --> Rend[Renderer]
    end

    subgraph "Configuration & Themes"
        Config[TuiConfig<br/>config.py]
        Themes[Theme System<br/>themes.py]
        ThemeMan[ThemeManager<br/>theme_manager.py]
    end

    subgraph "Message System"
        Msg1[DirectoryChanged]
        Msg2[TitleChanged]
        Msg3[Flash]
    end

    App --> Config
    Term --> Config
    Term --> Themes
    PTY --> ThemeMan

    Term -.Post.-> Msg1
    Term -.Post.-> Msg2
    Term -.Post.-> Msg3

    Msg1 -.Handle.-> App
    Msg2 -.Handle.-> App
    Msg3 -.Handle.-> App

    App --> Status
    App --> Flash

    style App fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style Term fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style PTY fill:#ff6f00,stroke:#ffa726,stroke-width:2px,color:#ffffff
    style Config fill:#0d47a1,stroke:#2196f3,stroke-width:2px,color:#ffffff
    style Themes fill:#1b5e20,stroke:#4caf50,stroke-width:2px,color:#ffffff
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Textual 6.6.0+ | TUI framework |
| **Terminal Emulation** | par-term-emu-core-rust 0.2.3+ | VT100/220/420 terminal emulation (Rust) |
| **Configuration** | PyYAML 6.0.3+ | YAML config parsing |
| **Clipboard** | pyperclip 1.11.0+ | Cross-platform clipboard |
| **XDG Compliance** | xdg-base-dirs 6.0.2+ | XDG directory handling |
| **Runtime** | Python 3.14 | Application runtime |
| **Build** | hatchling | Python packaging |
| **Quality** | ruff, pyright, pytest | Linting, type checking, testing |

---

## Conclusion

The par-term-emu-tui-rust architecture is a well-structured Python TUI wrapper around a Rust terminal emulator backend. Key strengths:

1. **Clean separation of concerns** - App, Widget, Managers, Config, Themes
2. **Thread-safe design** - Atomic snapshots, generation tracking
3. **Performance-optimized** - Debounced refresh, LRU caching, line API
4. **Feature-rich** - Selection, clipboard, themes, screenshots, shell integration
5. **User-configurable** - 30 options in YAML config
6. **Debuggable** - Comprehensive logging infrastructure
7. **Extensible** - Manager pattern allows easy feature additions

The architecture successfully demonstrates how to integrate a high-performance Rust backend (par-term-emu-core-rust) with a Python TUI framework (Textual) while maintaining clean abstractions and efficient rendering.

---

## Related Documentation

- [README](../README.md) - Project overview and quickstart
- [CONFIG_REFERENCE](CONFIG_REFERENCE.md) - Complete configuration reference
- [DEBUG](DEBUG.md) - Debugging guide and troubleshooting
- [DOCUMENTATION_STYLE_GUIDE](DOCUMENTATION_STYLE_GUIDE.md) - Documentation standards
