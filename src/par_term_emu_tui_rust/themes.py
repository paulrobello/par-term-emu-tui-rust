"""
Theme system for par-term-emu-tui-rust TUI.

Provides built-in color themes compatible with iTerm2 theme format.
Each theme defines 16 ANSI palette colors plus default colors for
background, foreground, cursor, and selection.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Theme:
    """Terminal color theme.

    Attributes:
        name: Theme display name.
        palette: List of 16 hex color strings for ANSI colors 0-15.
        background: Default background color (hex string).
        foreground: Default foreground color (hex string).
        cursor: Cursor color (hex string).
        cursor_text: Cursor text color (hex string).
        selection: Selection background color (hex string).
        selection_text: Selection text color (hex string).
        link: Link/hyperlink color (hex string).
        bold: Bold text color when use_bold_color is enabled (hex string).
        cursor_guide: Cursor guide color for vertical line (hex string).
        underline: Underline color when use_underline_color is enabled (hex string).
        badge: Badge color (hex string).
        match: Match/search highlight color (hex string).
    """

    name: str
    palette: list[str]
    background: str
    foreground: str
    cursor: str
    cursor_text: str
    selection: str
    selection_text: str
    link: str
    bold: str
    cursor_guide: str
    underline: str
    badge: str
    match: str

    def __post_init__(self) -> None:
        """Validate theme has exactly 16 palette colors."""
        if len(self.palette) != 16:
            msg = f"Theme '{self.name}' must have exactly 16 palette colors, got {len(self.palette)}"
            raise ValueError(
                msg,
            )


# Built-in themes ported from iTerm2
THEMES: dict[str, Theme] = {
    "dark-background": Theme(
        name="Dark Background",
        palette=[
            "#000000",
            "#bb0000",
            "#00bb00",
            "#bbbb00",
            "#0000bb",
            "#bb00bb",
            "#00bbbb",
            "#bbbbbb",
            "#555555",
            "#ff5555",
            "#55ff55",
            "#ffff55",
            "#5555ff",
            "#ff55ff",
            "#55ffff",
            "#ffffff",
        ],
        background="#000000",
        foreground="#bbbbbb",
        cursor="#bbbbbb",
        cursor_text="#000000",
        selection="#b5d5ff",
        selection_text="#000000",
        link="#0645ad",
        bold="#ffffff",
        cursor_guide="#a6e8ff",
        underline="#bbbbbb",
        badge="#ff0000",
        match="#ffff00",
    ),
    "high-contrast": Theme(
        name="High Contrast",
        palette=[
            "#000000",
            "#ff0000",
            "#00ff00",
            "#ffff00",
            "#0000ff",
            "#ff00ff",
            "#00ffff",
            "#ffffff",
            "#7f7f7f",
            "#ff7f7f",
            "#7fff7f",
            "#ffff7f",
            "#7f7fff",
            "#ff7fff",
            "#7fffff",
            "#ffffff",
        ],
        background="#000000",
        foreground="#ffffff",
        cursor="#ffffff",
        cursor_text="#000000",
        selection="#333333",
        selection_text="#ffffff",
        link="#00ffff",
        bold="#ffffff",
        cursor_guide="#ff00ff",
        underline="#ffffff",
        badge="#ff0000",
        match="#ffff00",
    ),
    "light-background": Theme(
        name="Light Background",
        palette=[
            "#000000",
            "#bb0000",
            "#00bb00",
            "#bbbb00",
            "#0000bb",
            "#bb00bb",
            "#00bbbb",
            "#bbbbbb",
            "#555555",
            "#ff5555",
            "#55ff55",
            "#ffff55",
            "#5555ff",
            "#ff55ff",
            "#55ffff",
            "#ffffff",
        ],
        background="#ffffff",
        foreground="#000000",
        cursor="#000000",
        cursor_text="#ffffff",
        selection="#cbe4ff",
        selection_text="#000000",
        link="#0645ad",
        bold="#000000",
        cursor_guide="#cbe4ff",
        underline="#000000",
        badge="#ff0000",
        match="#ffff00",
    ),
    "pastel-dark": Theme(
        name="Pastel (Dark Background)",
        palette=[
            "#4f4f4f",
            "#ff6c60",
            "#a8ff60",
            "#ffffb6",
            "#96cbfe",
            "#ff73fd",
            "#c6c5fe",
            "#eeeeee",
            "#7c7c7c",
            "#ffb6b0",
            "#ceffac",
            "#ffffcc",
            "#b5dcff",
            "#ff9cfe",
            "#dfdffe",
            "#ffffff",
        ],
        background="#000000",
        foreground="#bbbbbb",
        cursor="#ffa560",
        cursor_text="#ffffff",
        selection="#363983",
        selection_text="#f2f2f2",
        link="#96cbfe",
        bold="#ffffff",
        cursor_guide="#c6c5fe",
        underline="#bbbbbb",
        badge="#ff6c60",
        match="#ffffb6",
    ),
    "regular": Theme(
        name="Regular",
        palette=[
            "#14191e",
            "#b43c2a",
            "#00c200",
            "#c7c400",
            "#2744c7",
            "#c040be",
            "#00c5c7",
            "#c7c7c7",
            "#686868",
            "#dd7975",
            "#58e790",
            "#ece100",
            "#a7abf2",
            "#e17ee1",
            "#60fdff",
            "#ffffff",
        ],
        background="#fafafa",
        foreground="#101010",
        cursor="#000000",
        cursor_text="#ffffff",
        selection="#b3d7ff",
        selection_text="#000000",
        link="#2744c7",
        bold="#000000",
        cursor_guide="#b3d7ff",
        underline="#101010",
        badge="#b43c2a",
        match="#c7c400",
    ),
    "smoooooth": Theme(
        name="Smoooooth",
        palette=[
            "#14191e",
            "#b43c2a",
            "#00c200",
            "#c7c400",
            "#2744c7",
            "#c040be",
            "#00c5c7",
            "#c7c7c7",
            "#686868",
            "#dd7975",
            "#58e790",
            "#ece100",
            "#a7abf2",
            "#e17ee1",
            "#60fdff",
            "#ffffff",
        ],
        background="#15191f",
        foreground="#dcdcdc",
        cursor="#ffffff",
        cursor_text="#000000",
        selection="#b3d7ff",
        selection_text="#000000",
        link="#60fdff",
        bold="#ffffff",
        cursor_guide="#a7abf2",
        underline="#dcdcdc",
        badge="#dd7975",
        match="#ece100",
    ),
    "solarized": Theme(
        name="Solarized",
        palette=[
            "#073642",
            "#dc322f",
            "#859900",
            "#b58900",
            "#268bd2",
            "#d33682",
            "#2aa198",
            "#eee8d5",
            "#002b36",
            "#cb4b16",
            "#586e75",
            "#657b83",
            "#839496",
            "#6c71c4",
            "#93a1a1",
            "#fdf6e3",
        ],
        background="#002b36",
        foreground="#839496",
        cursor="#839496",
        cursor_text="#073642",
        selection="#073642",
        selection_text="#93a1a1",
        link="#268bd2",
        bold="#93a1a1",
        cursor_guide="#586e75",
        underline="#839496",
        badge="#dc322f",
        match="#b58900",
    ),
    "solarized-dark": Theme(
        name="Solarized Dark",
        palette=[
            "#073642",  # base02
            "#dc322f",  # red
            "#859900",  # green
            "#b58900",  # yellow
            "#268bd2",  # blue
            "#d33682",  # magenta
            "#2aa198",  # cyan
            "#eee8d5",  # base2
            "#002b36",  # base03
            "#cb4b16",  # orange
            "#586e75",  # base01
            "#657b83",  # base00
            "#839496",  # base0
            "#6c71c4",  # violet
            "#93a1a1",  # base1
            "#fdf6e3",  # base3
        ],
        background="#002b36",  # base03
        foreground="#839496",  # base0
        cursor="#93a1a1",  # base1
        cursor_text="#002b36",
        selection="#073642",
        selection_text="#93a1a1",
        link="#268bd2",
        bold="#93a1a1",
        cursor_guide="#586e75",
        underline="#839496",
        badge="#dc322f",
        match="#b58900",
    ),
    "solarized-light": Theme(
        name="Solarized Light",
        palette=[
            "#eee8d5",  # base2
            "#dc322f",  # red
            "#859900",  # green
            "#b58900",  # yellow
            "#268bd2",  # blue
            "#d33682",  # magenta
            "#2aa198",  # cyan
            "#073642",  # base02
            "#fdf6e3",  # base3
            "#cb4b16",  # orange
            "#93a1a1",  # base1
            "#839496",  # base0
            "#657b83",  # base00
            "#6c71c4",  # violet
            "#586e75",  # base01
            "#002b36",  # base03
        ],
        background="#fdf6e3",  # base3
        foreground="#657b83",  # base00
        cursor="#586e75",  # base01
        cursor_text="#fdf6e3",
        selection="#eee8d5",
        selection_text="#586e75",
        link="#268bd2",
        bold="#586e75",
        cursor_guide="#93a1a1",
        underline="#657b83",
        badge="#dc322f",
        match="#b58900",
    ),
    "iterm2-dark": Theme(
        name="iTerm2 Dark",
        palette=[
            "#2e3436",
            "#cc0000",
            "#4e9a06",
            "#c4a000",
            "#3465a4",
            "#75507b",
            "#06989a",
            "#d3d7cf",
            "#555753",
            "#ef2929",
            "#8ae234",
            "#fce94f",
            "#729fcf",
            "#ad7fa8",
            "#34e2e2",
            "#eeeeec",
        ],
        background="#000000",
        foreground="#d3d7cf",
        cursor="#d3d7cf",
        cursor_text="#000000",
        selection="#eeeeec",
        selection_text="#555753",
        link="#729fcf",
        bold="#eeeeec",
        cursor_guide="#555753",
        underline="#d3d7cf",
        badge="#cc0000",
        match="#fce94f",
    ),
    "tango-dark": Theme(
        name="Tango Dark",
        palette=[
            "#2e3436",
            "#cc0000",
            "#4e9a06",
            "#c4a000",
            "#3465a4",
            "#75507b",
            "#06989a",
            "#d3d7cf",
            "#555753",
            "#ef2929",
            "#8ae234",
            "#fce94f",
            "#729fcf",
            "#ad7fa8",
            "#34e2e2",
            "#eeeeec",
        ],
        background="#2e3436",
        foreground="#d3d7cf",
        cursor="#d3d7cf",
        cursor_text="#2e3436",
        selection="#eeeeec",
        selection_text="#555753",
        link="#729fcf",
        bold="#eeeeec",
        cursor_guide="#555753",
        underline="#d3d7cf",
        badge="#cc0000",
        match="#fce94f",
    ),
    "tango-light": Theme(
        name="Tango Light",
        palette=[
            "#2e3436",
            "#cc0000",
            "#4e9a06",
            "#c4a000",
            "#3465a4",
            "#75507b",
            "#06989a",
            "#d3d7cf",
            "#555753",
            "#ef2929",
            "#8ae234",
            "#fce94f",
            "#729fcf",
            "#ad7fa8",
            "#34e2e2",
            "#eeeeec",
        ],
        background="#ffffff",
        foreground="#2e3436",
        cursor="#2e3436",
        cursor_text="#ffffff",
        selection="#cbe4ff",
        selection_text="#2e3436",
        link="#3465a4",
        bold="#2e3436",
        cursor_guide="#cbe4ff",
        underline="#2e3436",
        badge="#cc0000",
        match="#c4a000",
    ),
}

# Default theme
DEFAULT_THEME = "iterm2-dark"


def get_theme(name: str) -> Theme:
    """Get theme by name (case-insensitive, normalized).

    Args:
        name: Theme name (can use spaces or hyphens, case-insensitive).
              Examples: "Dark Background", "dark-background", "DARK_BACKGROUND"

    Returns:
        Theme object.

    Raises:
        ValueError: If theme name is not found.
    """
    # Normalize theme name: lowercase, replace spaces/underscores with hyphens
    normalized = name.lower().replace(" ", "-").replace("_", "-")

    if normalized not in THEMES:
        available = ", ".join(sorted(THEMES.keys()))
        msg = f"Theme '{name}' not found. Available themes: {available}"
        raise ValueError(msg)

    return THEMES[normalized]


def list_themes() -> list[str]:
    """Get list of available theme names (display names).

    Returns:
        Sorted list of theme display names.
    """
    return sorted(theme.name for theme in THEMES.values())


def list_theme_keys() -> list[str]:
    """Get list of available theme keys (normalized names).

    Returns:
        Sorted list of theme keys for use in --theme flag.
    """
    return sorted(THEMES.keys())
