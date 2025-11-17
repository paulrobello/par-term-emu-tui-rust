"""
Configuration management for par-term-emu-tui-rust TUI.

Handles loading and saving user preferences using YAML and XDG directories.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

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
                                   Note: Currently not implemented.
                                   (default: False)
        accept_osc7: Allow directory tracking via OSC 7 sequences.
                    When True, terminal applications can report current working directory.
                    Note: Currently not implemented.
                    (default: True)
        theme: Color theme name to use for terminal colors.
              Available themes can be listed with `--list-themes`.
              (default: "dark-background")
        show_notifications: Display OSC 9/777 notifications as toast messages.
                          When True, terminal applications can display desktop-style
                          notifications using OSC 9 (simple) or OSC 777 (title + message).
                          (default: True)
        notification_timeout: Duration in seconds to display notifications.
                            How long notification toasts remain visible before auto-dismissing.
                            (default: 5)
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
        open_screenshot_after_capture: Automatically open screenshot after capture.
                                      When True, opens the screenshot file with the system's
                                      default image viewer (macOS: open, Linux: xdg-open,
                                      Windows: start).
                                      (default: False)
        exit_on_shell_exit: Exit TUI when shell exits.
                           When True, the TUI application exits when the shell process exits.
                           When False, displays exit message and allows restart with Ctrl+Shift+R.
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
                     (default: "none")
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

    # Notifications (OSC 9/777)
    show_notifications: bool = True  # Display OSC 9/777 notifications as toasts
    notification_timeout: int = 5  # Notification display duration in seconds

    # Screenshot
    screenshot_directory: str | None = None  # Directory to save screenshots
    screenshot_format: str = "png"  # Screenshot file format (png, jpeg, bmp, svg)
    open_screenshot_after_capture: bool = False  # Open screenshot with default viewer

    # Shell Behavior
    exit_on_shell_exit: bool = True  # Exit TUI when shell exits

    # Hyperlinks & URLs
    clickable_urls: bool = True  # Enable clicking URLs to open in browser
    link_color: tuple[int, int, int] = (100, 150, 255)  # RGB color for hyperlinks (blue)
    url_modifier: str = "none"  # Modifier key for URL clicks: "none", "ctrl", "shift", "alt"

    # Search & Highlighting
    search_match_color: tuple[int, int, int] = (255, 255, 0)  # RGB color for search matches (yellow)

    # UI Elements
    show_status_bar: bool = True  # Show or hide the status bar at the bottom

    # Visual Bell
    visual_bell_enabled: bool = True  # Enable visual bell indicator (bell icon in header)

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

            # Only use keys that exist in our dataclass
            valid_keys = set(cls.__annotations__)
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}

            return cls(**filtered_data)
        except Exception:
            logger.exception("Failed to load config from %s", config_path)
            return cls()

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
