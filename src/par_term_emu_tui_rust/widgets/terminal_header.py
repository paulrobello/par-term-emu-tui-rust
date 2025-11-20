"""
Custom header widget for terminal emulator with visual bell indicator.
"""

from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Header


class TerminalHeader(Header):
    """
    Custom header widget that displays indicators for terminal events.

    Features:
    - Bell icon (🔔) appears when terminal bell is triggered
    - Recording icon (⏺️) appears when terminal recording is active

    The bell icon disappears when the user interacts with the terminal via
    keyboard or mouse input. The recording icon persists until recording is stopped.
    """

    bell_active: reactive[bool] = reactive(False)
    recording_active: reactive[bool] = reactive(False)

    def __init__(self) -> None:
        """Initialize the terminal header."""
        super().__init__()
        self._original_sub_title = ""

    def on_mount(self) -> None:
        """Store original sub-title on mount."""
        self._original_sub_title = self.screen.sub_title

    def _update_sub_title(self) -> None:
        """Update sub-title with current indicators."""
        indicators = []
        if self.recording_active:
            indicators.append("⏺️ REC")
        if self.bell_active:
            indicators.append("🔔")

        if indicators:
            indicator_str = " ".join(indicators)
            if self._original_sub_title:
                self.screen.sub_title = f"{self._original_sub_title} {indicator_str}"
            else:
                self.screen.sub_title = indicator_str
        else:
            self.screen.sub_title = self._original_sub_title

    def show_bell(self) -> None:
        """Show the bell icon in the header."""
        if not self.bell_active:
            self.bell_active = True
            self._update_sub_title()

    def hide_bell(self) -> None:
        """Hide the bell icon in the header."""
        if self.bell_active:
            self.bell_active = False
            self._update_sub_title()

    def show_recording(self) -> None:
        """Show the recording icon in the header."""
        if not self.recording_active:
            self.recording_active = True
            self._update_sub_title()

    def hide_recording(self) -> None:
        """Hide the recording icon in the header."""
        if self.recording_active:
            self.recording_active = False
            self._update_sub_title()
