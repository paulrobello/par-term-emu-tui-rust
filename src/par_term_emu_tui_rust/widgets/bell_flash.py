"""
Visual bell flash widget - displays a 3x3 bell icon overlay.

Shows a bell icon (🔔) in the center of the screen for 1 second when
the terminal receives a bell character (BEL/\x07).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.reactive import var
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.timer import Timer


class BellFlash(Static):
    """
    A 3x3 flash widget that displays a bell icon in the center of the screen.

    This widget appears as an overlay when the terminal receives a bell character,
    showing a bell icon (🔔) for .25 seconds before automatically hiding.
    """

    DEFAULT_CSS = """
    BellFlash {
        width: 4;
        height: 3;
        padding: 0;
        margin: 0;
        border: round $warning;
        background: black;
        color: $warning;
        layer: bell_flash;
        visibility: hidden;
        &.-visible {
            visibility: visible;
        }
    }
    """

    flash_timer: var[Timer | None] = var(None)

    def __init__(self) -> None:
        """Initialize the bell flash widget."""
        super().__init__("🔔")

    def flash(self, duration: float = 0.25) -> None:
        """Flash the bell icon for a brief period.

        Args:
            duration: Duration in seconds to show the bell icon (default: 0.25).
        """
        # Cancel any existing timer
        if self.flash_timer is not None:
            self.flash_timer.stop()

        # Hide first to reset any ongoing flash
        self.visible = False

        def hide() -> None:
            """Hide the bell icon after timer expires."""
            self.visible = False
            self.remove_class("-visible")

        # Show the bell icon
        self.add_class("-visible")
        self.visible = True

        # Set timer to hide after duration
        self.flash_timer = self.set_timer(duration, hide)
