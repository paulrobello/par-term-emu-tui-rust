"""Theme management for terminal widget."""

from typing import TYPE_CHECKING

from par_term_emu_core_rust import CursorStyle, PtyTerminal
from par_term_emu_core_rust.debug import debug_log

from par_term_emu_tui_rust.themes import get_theme

if TYPE_CHECKING:
    from par_term_emu_tui_rust.config import TuiConfig


def parse_color(color_hex: str) -> tuple[int, int, int]:
    """Parse hex color to RGB tuple.

    Args:
        color_hex: Hex color string in format "#rrggbb"

    Returns:
        RGB tuple (r, g, b) where each component is 0-255
    """
    if color_hex.startswith("#"):
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        return r, g, b
    return 0, 0, 0


def apply_theme(term: PtyTerminal, config: TuiConfig) -> str | None:
    """Apply the configured theme to the terminal.

    This sets all terminal colors including ANSI palette, default colors,
    cursor, selection, link, and special colors.

    Args:
        term: The terminal instance to apply theme to
        config: TUI configuration containing theme name

    Returns:
        The theme background color (hex string) or None if theme failed to load
    """
    try:
        theme = get_theme(config.theme)
    except ValueError as e:
        debug_log("THEME", f"Failed to load theme: {e}, using default")
        return None

    # Set ANSI palette colors (0-15)
    for i, color in enumerate(theme.palette):
        r, g, b = parse_color(color)
        term.set_ansi_palette_color(i, r, g, b)

    # Set default colors
    r, g, b = parse_color(theme.foreground)
    term.set_default_fg(r, g, b)

    r, g, b = parse_color(theme.background)
    term.set_default_bg(r, g, b)

    # Set cursor colors
    r, g, b = parse_color(theme.cursor)
    term.set_cursor_color(r, g, b)

    # Set selection colors
    r, g, b = parse_color(theme.selection)
    term.set_selection_bg_color(r, g, b)

    r, g, b = parse_color(theme.selection_text)
    term.set_selection_fg_color(r, g, b)

    # Set link color
    r, g, b = parse_color(theme.link)
    term.set_link_color(r, g, b)

    # Set bold color
    r, g, b = parse_color(theme.bold)
    term.set_bold_color(r, g, b)

    # Set cursor guide color
    r, g, b = parse_color(theme.cursor_guide)
    term.set_cursor_guide_color(r, g, b)

    # Set badge color
    r, g, b = parse_color(theme.badge)
    term.set_badge_color(r, g, b)

    # Set match/search highlight color
    r, g, b = parse_color(theme.match)
    term.set_match_color(r, g, b)

    debug_log("THEME", f"Applied theme '{theme.name}'")

    return theme.background


def apply_cursor_style(term: PtyTerminal, config: TuiConfig) -> None:
    """Apply the configured cursor style to the terminal.

    Maps the config string value to CursorStyle enum and applies it.
    Valid values: "blinking_block", "steady_block", "blinking_underline",
                  "steady_underline", "blinking_bar", "steady_bar"

    Args:
        term: The terminal instance to apply cursor style to
        config: TUI configuration containing cursor_style setting
    """
    # Map config string to CursorStyle enum
    style_map = {
        "blinking_block": CursorStyle.BlinkingBlock,
        "steady_block": CursorStyle.SteadyBlock,
        "blinking_underline": CursorStyle.BlinkingUnderline,
        "steady_underline": CursorStyle.SteadyUnderline,
        "blinking_bar": CursorStyle.BlinkingBar,
        "steady_bar": CursorStyle.SteadyBar,
    }

    style_str = config.cursor_style.lower()
    if style_str in style_map:
        try:
            term.set_cursor_style(style_map[style_str])
            debug_log("CURSOR", f"Applied cursor style: {style_str}")
        except Exception as e:
            debug_log("CURSOR", f"Failed to set cursor style '{style_str}': {e}")
    else:
        debug_log(
            "CURSOR",
            f"Invalid cursor style '{style_str}', valid values: {list(style_map.keys())}",
        )
