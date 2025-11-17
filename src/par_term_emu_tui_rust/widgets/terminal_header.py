"""
Custom header widget for terminal emulator with visual bell indicator.
"""

from textual.reactive import reactive
from textual.widgets import Header


class TerminalHeader(Header):
    """
    Custom header widget that displays a bell icon when terminal bell is triggered.

    The bell icon (🔔) appears in the sub-title when a bell event
    is detected, and disappears when the user interacts with the terminal via
    keyboard or mouse input.
    """

    bell_active: reactive[bool] = reactive(False)

    def __init__(self) -> None:
        """Initialize the terminal header."""
        super().__init__()
        self._original_sub_title = ""

    def on_mount(self) -> None:
        """Store original sub-title on mount."""
        self._original_sub_title = self.screen.sub_title

    def show_bell(self) -> None:
        """Show the bell icon in the header."""
        if not self.bell_active:
            self.bell_active = True
            # Add bell icon to sub-title
            if self.screen.sub_title:
                self.screen.sub_title = f"{self.screen.sub_title} 🔔"
            else:
                self.screen.sub_title = "🔔"

    def hide_bell(self) -> None:
        """Hide the bell icon in the header."""
        if self.bell_active:
            self.bell_active = False
            # Restore original sub-title
            self.screen.sub_title = self._original_sub_title
