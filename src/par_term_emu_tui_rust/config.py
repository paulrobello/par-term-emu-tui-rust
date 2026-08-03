"""
Configuration management for par-term-emu-tui-rust TUI.

Handles loading and saving user preferences using YAML and XDG directories.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field, fields
from typing import TYPE_CHECKING, Any, get_type_hints

from xdg_base_dirs import xdg_config_home

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TuiConfig:
    """TUI configuration settings.

    Attributes:
        auto_copy_selection: Automatically copy selected text to clipboard.
                            When True, double-click, triple-click, and shift+drag
                            selections are automatically copied. (default: True)
        keep_selection_after_copy: Keep text highlighted after copying.
                                   When True, selection remains visible until next
                                   input event or new selection (like iTerm2).
                                   (default: True)
        expose_system_clipboard: Allow terminal applications to read system clipboard.
                                When True, enables OSC 52 clipboard queries, allowing
                                terminal applications to read clipboard contents via
                                escape sequences. When False, blocks clipboard read
                                for security. (default: True)
        copy_trailing_newline: Include trailing newline when copying lines.
                              When True, adds \\n at the end of copied line content.
                              (default: False)
        word_characters: Characters considered part of a word for double-click selection.
                        Any character not in this string will be treated as a word boundary.
                        Default matches iTerm2: "/-+\\~_." (slash, hyphen, plus, backslash, tilde, underscore, dot)
                        (default: "/-+\\~_.")
        triple_click_selects_wrapped_lines: Select full wrapped lines on triple-click.
                                           When True, triple-click follows line wrapping.
                                           When False, only selects visible line.
                                           (default: True)
        scrollback_lines: Maximum number of lines to keep in scrollback buffer.
                         Set to 0 for unlimited (up to max_scrollback_lines safety limit).
                         (default: 10000)
        max_scrollback_lines: Safety limit for unlimited scrollback.
                             Maximum number of lines even when scrollback_lines is 0.
                             (default: 100000)
        cursor_blink_enabled: Enable cursor blinking.
                             When True, blinking cursor styles (BlinkingBlock, BlinkingUnderline,
                             BlinkingBar) will blink. Steady cursor styles (SteadyBlock,
                             SteadyUnderline, SteadyBar) remain always visible regardless.
                             (default: False)
        cursor_blink_rate: Cursor blink interval in seconds.
                          Time between blink state changes.
                          (default: 0.5)
        cursor_style: Default cursor appearance.
                     Valid values: "blinking_block", "steady_block", "blinking_underline",
                     "steady_underline", "blinking_bar", "steady_bar"
                     (default: "blinking_block")
        paste_chunk_size: Paste in chunks to avoid overwhelming the terminal.
                         Set to 0 to disable chunking and paste all at once.
                         (default: 0)
        paste_chunk_delay_ms: Delay in milliseconds between paste chunks.
                             Only used when paste_chunk_size > 0.
                             (default: 10)
        paste_warn_size: Warn user before pasting content larger than this many bytes.
                        Helps prevent accidentally pasting huge content.
                        (default: 100000)
        focus_follows_mouse: Auto-focus terminal on mouse hover.
                            When True, terminal automatically gains focus when mouse enters.
                            (default: False)
        middle_click_paste: Paste on middle mouse button click.
                           When True, middle click pastes text. On Linux, pastes from
                           X11 PRIMARY selection (text selected with mouse). On macOS/Windows,
                           pastes from regular clipboard.
                           (default: True)
        mouse_wheel_scroll_lines: Number of lines to scroll per mouse wheel tick.
                                 Controls how many lines the terminal scrolls when using the
                                 mouse wheel (when mouse tracking is off).
                                 (default: 3)
        disable_insecure_sequences: Block potentially risky escape sequences.
                                   When True, filters out sequences that could be security risks.
                                   (default: False)
        accept_osc7: Allow directory tracking via OSC 7 sequences.
                    When True, terminal applications can report current working directory.
                    (default: True)
        theme: Color theme name to use for terminal colors.
              Available themes can be listed with `--list-themes`.
              (default: "dark-background")
        bold_brightening: Use bright ANSI colors (8-15) for bold text with normal colors (0-7).
                         When True, bold text with ANSI colors 0-7 automatically uses bright
                         variants 8-15 (like iTerm2's "Use Bright Bold" setting). When False,
                         bold text uses the original color without brightening.
                         (default: False)
        minimum_contrast: Minimum contrast adjustment for live terminal display (iTerm2-compatible).
                         Automatically adjusts text colors to ensure readability against backgrounds.
                         Uses NTSC perceived brightness formula. Applied to both live display
                         and screenshots unless screenshot_minimum_contrast is explicitly set.
                         Range: 0.0-1.0 where:
                         - 0.0 = disabled (default)
                         - 0.5 = moderate contrast (recommended, matches iTerm2 slider at 50%)
                         - 1.0 = maximum contrast
                         (default: 0.0)
        faint_text_alpha: Alpha multiplier for faint/dim text (SGR 2).
                         0.0 makes faint text invisible, 1.0 renders it normally.
                         (default: 0.5)
        show_notifications: Display OSC 9/777 notifications as toast messages.
                          When True, terminal applications can display desktop-style
                          notifications using OSC 9 (simple) or OSC 777 (title + message).
                          (default: True)
        notification_timeout: Duration in seconds to display notifications.
                            How long notification toasts remain visible before auto-dismissing.
                            (default: 5)
        notification_bell_desktop: Forward BEL events to desktop notification centers.
                                   When True, backend triggers OS-level notifications.
                                   (default: False)
        notification_bell_sound: Volume (0-100) for backend sound alerts on BEL.
                                 0 disables sounds.
                                 (default: 0)
        notification_bell_visual: Enable backend visual bell overlay (independent of TUI bell).
                                  (default: True)
        notification_activity_enabled: Emit alerts when activity resumes after inactivity window.
                                       (default: False)
        notification_activity_threshold: Seconds of inactivity before activity notifications fire.
                                         (default: 10)
        notification_silence_enabled: Emit alerts after prolonged silence.
                                      (default: False)
        notification_silence_threshold: Seconds of silence that trigger alerts.
                                        (default: 300)
        notification_max_buffer: Maximum number of OSC 9/777 notifications buffered in the backend.
                                 Older entries are dropped when the cap is reached.
                                 (default: 64)
        clipboard_max_sync_events: Cap for clipboard synchronization history stored by the backend.
                                   Prevents unbounded memory use while debugging.
                                   (default: 64)
        clipboard_max_event_bytes: Maximum payload size retained per clipboard sync event in bytes.
                                   Payloads larger than this are truncated.
                                   (default: 2048)
        screenshot_directory: Directory to save screenshots.
                            When None (default), tries in order:
                            1. Shell's current working directory (from OSC 7)
                            2. XDG_PICTURES_DIR/Screenshots
                            3. ~/Pictures/Screenshots
                            4. Home directory
                            Set to a path string to override default behavior.
                            (default: None)
        screenshot_format: File format for screenshots.
                          Supported formats: "png", "jpeg", "bmp", "svg", "html"
                          - png: Lossless, best for text (default)
                          - jpeg: Smaller file size, lossy compression
                          - bmp: Uncompressed, large file size
                          - svg: Vector format, infinitely scalable with selectable text
                          - html: Full HTML document with inline styles, viewable in browsers
                          (default: "png")
        screenshot_minimum_contrast: Minimum contrast adjustment for screenshots (iTerm2-compatible).
                                    When set to None (default), inherits the live `minimum_contrast`.
                                    Set a float (0.0-1.0) to override screenshots only.
                                    (default: None, i.e., reuse minimum_contrast)
        open_screenshot_after_capture: Automatically open screenshot after capture.
                                      When True, opens the screenshot file with the system's
                                      default image viewer (macOS: open, Linux: xdg-open,
                                      Windows: start).
                                      (default: False)
        recording_directory: Directory to save terminal recordings.
                           When None (default), uses same logic as screenshot_directory:
                           1. Shell's current working directory (from OSC 7)
                           2. XDG_PICTURES_DIR/Recordings or ~/Videos/Recordings
                           3. Home directory
                           Set to a path string to override default behavior.
                           (default: None)
        recording_format: File format for terminal recordings.
                         Supported formats:
                         - "asciicast": asciinema v2 format (default, playback with asciinema)
                         - "json": JSON export with full session data
                         (default: "asciicast")
        recording_title_template: Template for recording session title.
                                 Use {timestamp} for automatic timestamp insertion.
                                 Example: "Build Session {timestamp}"
                                 (default: "Terminal Session {timestamp}")
        recording_auto_export_on_stop: Automatically export recording when stopped.
                                      When True, recording is saved to file automatically when
                                      stopped. When False, recording data is kept in memory only
                                      (useful for programmatic access).
                                      (default: True)
        open_recording_after_export: Automatically open recording after export.
                                    When True, opens the recording file with the system's
                                    default application (e.g., asciinema player for .cast files).
                                    (default: False)
        exit_on_shell_exit: Exit TUI when shell exits.
                           When True, the TUI application exits when the shell process exits.
                           When False, the TUI remains open after the shell exits, allowing
                           you to inspect the final screen contents. Restarting the shell
                           requires restarting the application via the CLI.
                           (default: True)
        clickable_urls: Enable clicking URLs to open in browser.
                       When True, clicking on URLs (OSC 8 hyperlinks or plain text URLs)
                       will open them in the default web browser.
                       (default: True)
        link_color: RGB color tuple for hyperlinks.
                   Controls the visual appearance of clickable links in the terminal.
                   Format: (red, green, blue) where each value is 0-255.
                   (default: (100, 150, 255) - blue)
        url_modifier: Modifier key required for URL clicks.
                     "none" - Click URLs directly without modifier
                     "ctrl" - Require Ctrl+Click to open URLs
                     "shift" - Require Shift+Click to open URLs
                     "alt" - Require Alt+Click to open URLs
                     (default: "ctrl")
        allowed_url_schemes: List of URL schemes allowed to be opened via clickable
                            links. Schemes are case-insensitive. Examples include
                            "http", "https", "ftp", "ftps", "file", "mailto".
                            (default: ["http", "https", "ftp", "ftps", "file", "mailto"])
        warn_on_unknown_url_scheme: Warn when a URL is blocked because its scheme
                                   is not in allowed_url_schemes. When True, a
                                   non-fatal warning is displayed instead of opening
                                   the URL.
                                   (default: True)
        search_match_color: RGB color tuple for search match highlights.
                           Controls the visual appearance of search matches in the terminal.
                           Format: (red, green, blue) where each value is 0-255.
                           Prepares for future search feature implementation.
                           (default: (255, 255, 0) - yellow)
        show_status_bar: Show or hide the status bar at the bottom of the terminal.
                        When True, the status bar is visible and can display information
                        like current directory (OSC 7). When False, the status bar is
                        completely hidden to maximize terminal space.
                        (default: True)
        visual_bell_enabled: Enable visual bell indicator in the header.
                           When True, a bell icon (🔔) appears in the header when the
                           terminal receives a bell character (BEL/\\x07). The icon
                           disappears on the next keyboard or mouse input.
                           (default: True)
        keyboard_protocol_enabled: Enable KITTY keyboard protocol for embedded applications.
                                  When True, sends enhanced keyboard sequences to the shell,
                                  allowing apps to distinguish Ctrl+I from Tab, Ctrl+M from Enter,
                                  and receive key release events (if flags include 2).
                                  Applications must support KITTY protocol to benefit.
                                  (default: False)
        keyboard_protocol_flags: KITTY protocol feature flags.
                                Bitwise OR combination of:
                                - 1: Disambiguate escape codes (Ctrl+I ≠ Tab)
                                - 2: Report key press and release events
                                - 4: Report alternate key representations
                                - 8: Report all keys as escape codes
                                - 16: Include associated text with events
                                Example: 3 = 1 + 2 (disambiguate + events)
                                (default: 1)
        keyboard_protocol_auto_detect: Auto-detect and enable KITTY protocol when apps request it.
                                      When True, monitors PTY output for protocol activation sequences
                                      (CSI >flags u) and automatically enables the protocol. When apps
                                      disable it (CSI <u), automatically disables. Works seamlessly with
                                      supporting applications without manual configuration.
                                      (default: False)
    """

    # Selection & Clipboard (Currently Implemented)
    auto_copy_selection: bool = True
    keep_selection_after_copy: bool = True
    expose_system_clipboard: bool = True

    # Selection Enhancement (Phase 1)
    copy_trailing_newline: bool = False
    word_characters: str = "/-+\\~_."
    triple_click_selects_wrapped_lines: bool = True

    # Scrollback & Cursor (Phase 2)
    scrollback_lines: int = 10000
    max_scrollback_lines: int = 100000
    cursor_blink_enabled: bool = False
    cursor_blink_rate: float = 0.5
    cursor_style: str = "blinking_block"

    # Paste Enhancement (Phase 3)
    paste_chunk_size: int = 0  # Bytes per chunk (0 = no chunking)
    paste_chunk_delay_ms: int = 10  # Delay between chunks in milliseconds
    paste_warn_size: int = 100000  # Warn before pasting > N bytes

    # Mouse & Focus (Phase 4)
    focus_follows_mouse: bool = False  # Auto-focus on mouse hover
    middle_click_paste: bool = True  # Paste PRIMARY selection on middle click
    mouse_wheel_scroll_lines: int = 3  # Number of lines to scroll per mouse wheel tick

    # Security & Advanced (Phase 5)
    disable_insecure_sequences: bool = False  # Block risky escape sequences
    accept_osc7: bool = True  # Directory tracking (OSC 7)

    # Theme (Phase 6)
    theme: str = "dark-background"  # Color theme name
    bold_brightening: bool = False  # Use bright colors (8-15) for bold text with colors 0-7
    minimum_contrast: float = 0.0  # Minimum contrast for display (0.0-1.0, default 0.0)
    faint_text_alpha: float = 0.5  # Faint text alpha (0.0=hidden, 1.0=normal)

    # Notifications (OSC 9/777)
    show_notifications: bool = True  # Display OSC 9/777 notifications as toasts
    notification_timeout: int = 5  # Notification display duration in seconds
    notification_bell_desktop: bool = False  # Forward BEL events to desktop notification centers
    notification_bell_sound: int = 0  # Volume 0-100 for backend bell audio
    notification_bell_visual: bool = True  # Backend visual bell overlay
    notification_activity_enabled: bool = False  # Enable activity notifications
    notification_activity_threshold: int = 10  # Seconds of inactivity before activity alert
    notification_silence_enabled: bool = False  # Enable silence notifications
    notification_silence_threshold: int = 300  # Seconds of silence before alert
    notification_max_buffer: int = 64  # Max OSC 9/777 entries retained in backend queue

    # Clipboard debug/sync controls
    clipboard_max_sync_events: int = 64  # Max clipboard sync events retained
    clipboard_max_event_bytes: int = 2048  # Max bytes per clipboard sync event

    # Screenshot
    screenshot_directory: str | None = None  # Directory to save screenshots
    screenshot_format: str = "png"  # Screenshot file format (png, jpeg, bmp, svg)
    screenshot_minimum_contrast: float | None = None  # Minimum contrast override for screenshots
    open_screenshot_after_capture: bool = False  # Open screenshot with default viewer

    # Recording
    recording_directory: str | None = None  # Directory to save recordings
    recording_format: str = "asciicast"  # Recording file format (asciicast, json)
    recording_title_template: str = "Terminal Session {timestamp}"  # Title template for recordings
    recording_auto_export_on_stop: bool = True  # Auto-export when stopping recording
    open_recording_after_export: bool = False  # Open recording with default app after export

    # Shell Behavior
    exit_on_shell_exit: bool = True  # Exit TUI when shell exits

    # Hyperlinks & URLs
    clickable_urls: bool = True  # Enable clicking URLs to open in browser
    link_color: tuple[int, int, int] = (100, 150, 255)  # RGB color for hyperlinks (blue)
    url_modifier: str = "ctrl"  # Modifier key for URL clicks: "none", "ctrl", "shift", "alt"
    allowed_url_schemes: list[str] = field(  # URL schemes allowed for clickable links
        default_factory=lambda: ["http", "https", "ftp", "ftps", "file", "mailto"],
    )
    warn_on_unknown_url_scheme: bool = True  # Warn when blocking URLs with unsupported schemes

    # Search & Highlighting
    search_match_color: tuple[int, int, int] = (255, 255, 0)  # RGB color for search matches (yellow)

    # UI Elements
    show_status_bar: bool = True  # Show or hide the status bar at the bottom

    # Visual Bell
    visual_bell_enabled: bool = True  # Enable visual bell indicator (bell icon in header)

    # Keyboard Protocol (KITTY)
    keyboard_protocol_enabled: bool = False  # Enable KITTY keyboard protocol for embedded apps
    keyboard_protocol_flags: int = (
        1  # KITTY protocol flags (1=disambiguate, 2=events, 4=alternate, 8=report_all, 16=associated_text)
    )
    keyboard_protocol_auto_detect: bool = False  # Auto-detect and enable when apps request protocol

    @staticmethod
    def _validate_value(field_name: str, value: Any, field_type: Any) -> Any:
        """Validate and clamp config values to valid ranges.

        Args:
            field_name: Name of the field being validated
            value: Value to validate
            field_type: Expected type of the field

        Returns:
            Validated and potentially clamped value

        Raises:
            ValueError: If value cannot be validated
        """
        # Validate float ranges (0.0-1.0)
        if field_name in ("minimum_contrast", "faint_text_alpha"):
            val = float(value)
            if val < 0.0:
                logger.warning("%s value %s is below 0.0, clamping to 0.0", field_name, val)
                return 0.0
            if val > 1.0:
                logger.warning("%s value %s is above 1.0, clamping to 1.0", field_name, val)
                return 1.0
            return val

        if field_name == "screenshot_minimum_contrast":
            if value is None:
                return None
            val = float(value)
            if val < 0.0:
                logger.warning("%s value %s is below 0.0, clamping to 0.0", field_name, val)
                return 0.0
            if val > 1.0:
                logger.warning("%s value %s is above 1.0, clamping to 1.0", field_name, val)
                return 1.0
            return val

        # Validate positive float values
        if field_name == "cursor_blink_rate":
            if field_type is float:
                val = float(value)
                if val <= 0.0:
                    logger.warning("%s value %s must be positive, using default 0.5", field_name, val)
                    return 0.5
                return val

        # Validate non-negative integers
        if field_name in (
            "scrollback_lines",
            "max_scrollback_lines",
            "paste_chunk_size",
            "paste_chunk_delay_ms",
            "paste_warn_size",
            "notification_timeout",
            "notification_activity_threshold",
            "notification_silence_threshold",
            "notification_max_buffer",
            "clipboard_max_sync_events",
            "clipboard_max_event_bytes",
            "keyboard_protocol_flags",
        ):
            if field_type is int:
                val = int(value)
                if val < 0:
                    logger.warning("%s value %s is negative, clamping to 0", field_name, val)
                    return 0
                return val

        if field_name == "notification_bell_sound":
            val = int(value)
            if val < 0:
                return 0
            if val > 100:
                logger.warning("notification_bell_sound %s above 100, clamping", val)
                return 100
            return val

        # Validate positive integers
        if field_name == "mouse_wheel_scroll_lines":
            if field_type is int:
                val = int(value)
                if val < 1:
                    logger.warning("%s value %s must be at least 1, using default 3", field_name, val)
                    return 3
                return val

        # Validate RGB tuples (0-255)
        if field_name in ("link_color", "search_match_color"):
            if isinstance(value, (list, tuple)) and len(value) == 3:
                clamped = []
                for i, component in enumerate(value):
                    val = int(component)
                    if val < 0:
                        logger.warning("%s[%d] value %s is below 0, clamping to 0", field_name, i, val)
                        clamped.append(0)
                    elif val > 255:
                        logger.warning("%s[%d] value %s is above 255, clamping to 255", field_name, i, val)
                        clamped.append(255)
                    else:
                        clamped.append(val)
                return tuple(clamped)

        # Validate cursor_style values
        if field_name == "cursor_style":
            valid_styles = {
                "blinking_block",
                "steady_block",
                "blinking_underline",
                "steady_underline",
                "blinking_bar",
                "steady_bar",
            }
            val = str(value).lower()
            if val not in valid_styles:
                logger.warning(
                    "%s value %r is invalid, using default 'blinking_block'. Valid values: %s",
                    field_name,
                    value,
                    valid_styles,
                )
                return "blinking_block"
            return val

        # Validate url_modifier values
        if field_name == "url_modifier":
            valid_modifiers = {"none", "ctrl", "shift", "alt"}
            val = str(value).lower()
            if val not in valid_modifiers:
                logger.warning(
                    "%s value %r is invalid, using default 'ctrl'. Valid values: %s",
                    field_name,
                    value,
                    valid_modifiers,
                )
                return "ctrl"
            return val

        # Validate screenshot_format values
        if field_name == "screenshot_format":
            valid_formats = {"png", "jpeg", "bmp", "svg", "html"}
            val = str(value).lower()
            if val not in valid_formats:
                logger.warning(
                    "%s value %r is invalid, using default 'png'. Valid values: %s",
                    field_name,
                    value,
                    valid_formats,
                )
                return "png"
            return val

        # No specific validation needed
        return value

    @classmethod
    def load(cls, config_path: Path | None = None) -> TuiConfig:
        """Load configuration from YAML file.

        Args:
            config_path: Optional path to config file. If None, uses XDG config directory.

        Returns:
            TuiConfig instance with loaded settings or defaults if file doesn't exist.
        """
        if config_path is None:
            config_path = cls.default_config_path()

        if not config_path.exists():
            logger.debug("Config file not found at %s, using defaults", config_path)
            return cls()

        try:
            import yaml

            with config_path.open(encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Get actual types (not string annotations) using get_type_hints
            type_hints = get_type_hints(cls)

            # Convert types to match dataclass field types
            converted_data = {}
            for field_info in fields(cls):
                if field_info.name not in data:
                    continue

                value = data[field_info.name]
                field_type = type_hints.get(field_info.name, field_info.type)
                field_type_str = str(field_type)

                try:
                    converted_value = None

                    # Handle None values
                    if value is None:
                        converted_value = None
                    # Handle bool (must come before int since bool is subclass of int)
                    elif field_type is bool:
                        converted_value = bool(value) if not isinstance(value, bool) else value
                    # Handle int
                    elif field_type is int:
                        converted_value = int(value) if not isinstance(value, int) else value
                    # Handle float
                    elif field_type is float:
                        converted_value = float(value) if not isinstance(value, float) else value
                    # Handle tuple[int, int, int] for colors
                    elif "tuple" in field_type_str and "int" in field_type_str:
                        if isinstance(value, (list, tuple)):
                            converted_value = tuple(int(v) for v in value)
                        else:
                            converted_value = field_info.default
                    # Handle list[str]
                    elif "list" in field_type_str and "str" in field_type_str:
                        if isinstance(value, list):
                            converted_value = [str(v) for v in value]
                        else:
                            converted_value = field_info.default
                    # Handle str and other types
                    else:
                        converted_value = value

                    # Apply validation if we have a non-None value
                    if converted_value is not None:
                        converted_value = cls._validate_value(field_info.name, converted_value, field_type)

                    converted_data[field_info.name] = converted_value

                except ValueError, TypeError:
                    # Use default value if conversion fails
                    logger.warning(
                        "Failed to convert %s value %r to type %s, using default",
                        field_info.name,
                        value,
                        field_type,
                    )
                    converted_data[field_info.name] = field_info.default

            return cls(**converted_data)
        except Exception as e:
            logger.exception("Failed to load config from %s", config_path)
            # Re-raise with config path for better error handling upstream
            msg = f"Failed to parse config file {config_path}: {e}"
            raise RuntimeError(msg) from e

    @classmethod
    def load_with_recovery(cls, config_path: Path | None = None, interactive: bool = True) -> TuiConfig:
        """Load configuration with error recovery options.

        Args:
            config_path: Optional path to config file. If None, uses XDG config directory.
            interactive: If True, prompt user for recovery options on parse failure.

        Returns:
            TuiConfig instance with loaded settings or defaults.
        """
        if config_path is None:
            config_path = cls.default_config_path()

        try:
            return cls.load(config_path)
        except RuntimeError as e:
            if not interactive:
                logger.exception("Config parse failed (non-interactive)")
                return cls()

            # Find backup files
            backup_files = sorted(config_path.parent.glob(f"{config_path.name}.backup.*"), reverse=True)

            print(f"\n❌ Error: Failed to parse config file: {config_path}", file=__import__("sys").stderr)
            print(f"   {e}", file=__import__("sys").stderr)
            print("\nRecovery options:", file=__import__("sys").stderr)
            print("  1. Reset to default configuration", file=__import__("sys").stderr)

            if backup_files:
                print(f"  2. Restore from most recent backup ({backup_files[0].name})", file=__import__("sys").stderr)
                if len(backup_files) > 1:
                    print(f"  3. Show all {len(backup_files)} backup files", file=__import__("sys").stderr)
                    print("  4. Exit", file=__import__("sys").stderr)
                else:
                    print("  3. Exit", file=__import__("sys").stderr)
            else:
                print("  2. Exit", file=__import__("sys").stderr)

            while True:
                try:
                    choice = input("\nSelect option [1]: ").strip() or "1"

                    if choice == "1":
                        # Reset to defaults
                        print("✓ Using default configuration", file=__import__("sys").stderr)
                        return cls()

                    if backup_files and choice == "2":
                        # Restore most recent backup
                        backup_path = backup_files[0]
                        try:
                            # Copy backup to config file
                            config_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
                            print(f"✓ Restored config from {backup_path.name}", file=__import__("sys").stderr)
                            return cls.load(config_path)
                        except Exception as restore_error:
                            print(f"❌ Failed to restore backup: {restore_error}", file=__import__("sys").stderr)
                            print("Falling back to default configuration", file=__import__("sys").stderr)
                            return cls()

                    if backup_files and len(backup_files) > 1 and choice == "3":
                        # Show all backups
                        print("\nAvailable backups:", file=__import__("sys").stderr)
                        for i, backup in enumerate(backup_files, 1):
                            size = backup.stat().st_size
                            mtime = __import__("datetime").datetime.fromtimestamp(
                                backup.stat().st_mtime, tz=__import__("datetime").UTC
                            )
                            print(
                                f"  {i}. {backup.name} ({size} bytes, modified {mtime.strftime('%Y-%m-%d %H:%M:%S')})",
                                file=__import__("sys").stderr,
                            )

                        backup_choice = input("\nSelect backup number (or Enter to go back): ").strip()
                        if backup_choice and backup_choice.isdigit():
                            idx = int(backup_choice) - 1
                            if 0 <= idx < len(backup_files):
                                backup_path = backup_files[idx]
                                try:
                                    config_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
                                    print(
                                        f"✓ Restored config from {backup_path.name}",
                                        file=__import__("sys").stderr,
                                    )
                                    return cls.load(config_path)
                                except Exception as restore_error:
                                    print(
                                        f"❌ Failed to restore backup: {restore_error}",
                                        file=__import__("sys").stderr,
                                    )
                                    print("Falling back to default configuration", file=__import__("sys").stderr)
                                    return cls()
                        continue

                    # Exit option
                    exit_option = "4" if (backup_files and len(backup_files) > 1) else ("3" if backup_files else "2")
                    if choice == exit_option:
                        print("Exiting...", file=__import__("sys").stderr)
                        __import__("sys").exit(1)

                    print(f"Invalid option: {choice}", file=__import__("sys").stderr)
                except KeyboardInterrupt, EOFError:
                    print("\nExiting...", file=__import__("sys").stderr)
                    __import__("sys").exit(1)

    def save(self, config_path: Path | None = None) -> None:
        """Save configuration to YAML file.

        Args:
            config_path: Optional path to config file. If None, uses XDG config directory.
        """
        if config_path is None:
            config_path = self.default_config_path()

        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            import yaml

            with config_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    asdict(self),
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                )
            logger.debug("Saved config to %s", config_path)
        except Exception:
            logger.exception("Failed to save config to %s", config_path)

    @staticmethod
    def default_config_path() -> Path:
        """Get the default config file path using XDG directories.

        Returns:
            Path to config file in XDG_CONFIG_HOME/par-term-emu-tui-rust/config.yaml
        """
        return xdg_config_home() / "par-term-emu-tui-rust" / "config.yaml"

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Dictionary representation of config.
        """
        return asdict(self)
