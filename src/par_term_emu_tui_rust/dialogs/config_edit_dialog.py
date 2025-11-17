"""Provides config file editor dialog."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, ClassVar

import yaml
from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static, TextArea

from par_term_emu_tui_rust.app import TerminalApp
from par_term_emu_tui_rust.config import TuiConfig

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult


class ConfigEditDialog(ModalScreen[bool]):
    """Modal dialog that allows config file editing with syntax highlighting."""

    DEFAULT_CSS = """
    ConfigEditDialog {
        background: black 75%;
        align: center middle;

        &> Vertical {
            background: $surface;
            width: 90%;
            height: 90%;
            min-width: 80;
            border: thick $panel;
            border-title-color: $primary;
            padding: 1;

            #button_bar {
                width: 1fr;
                height: auto;
                align: right middle;
                padding: 0 1;
            }

            #config_path {
                width: 1fr;
                height: auto;
                padding: 0 1 1 1;
                color: $text-muted;
            }

            TextArea {
                width: 1fr;
                height: 1fr;
                margin-bottom: 1;
            }
        }
    }
    """

    BINDINGS: ClassVar = [
        Binding("escape", "dismiss(False)", "Cancel", show=True),
        Binding("ctrl+s", "save", "Save", show=True),
    ]

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize the config edit dialog.

        Args:
            config_path: Optional path to config file. If None, uses default config path.
        """
        super().__init__()
        self.config_path = config_path if config_path is not None else TuiConfig.default_config_path()
        self.original_content: str = ""
        self.dirty: bool = False

    def compose(self) -> ComposeResult:
        """Compose the content of the dialog."""
        with Vertical() as v:
            v.border_title = "Config Editor"

            # Show config file path
            yield Static(f"File: {self.config_path}", id="config_path")

            # Create TextArea in code editor mode
            text_area = TextArea(
                id="config_editor",
                language="yaml",
                theme="monokai",
                show_line_numbers=True,
                tab_behavior="indent",
            )
            yield text_area

            # Button bar
            with Horizontal(id="button_bar"):
                yield Button("Save", id="save", variant="primary")
                yield Button("Cancel", id="cancel")

    async def on_mount(self) -> None:
        """Mount the view and load config file content."""
        # Load config file content
        try:
            if not self.config_path.exists():
                # Create default config file if it doesn't exist
                default_config = TuiConfig()
                self.config_path.parent.mkdir(parents=True, exist_ok=True)

                with self.config_path.open("w", encoding="utf-8") as f:
                    yaml.safe_dump(
                        asdict(default_config),
                        f,
                        default_flow_style=False,
                        sort_keys=False,
                    )

            # Load the config file (either existing or newly created)
            with self.config_path.open(encoding="utf-8") as f:
                self.original_content = f.read()

        except Exception as e:
            self.original_content = f"# Error loading config: {e}\n"

        # Set content in TextArea
        text_area = self.query_one("#config_editor", TextArea)
        text_area.text = self.original_content
        text_area.focus()

    @on(TextArea.Changed)
    def mark_dirty(self, event: TextArea.Changed) -> None:
        """Mark the config as dirty when content changes."""
        event.stop()
        self.dirty = self.query_one("#config_editor", TextArea).text != self.original_content

    @on(Button.Pressed, "#save")
    async def action_save(self, event: Button.Pressed | None = None) -> None:
        """Save the config file."""
        if event:
            event.stop()

        text_area = self.query_one("#config_editor", TextArea)
        content = text_area.text

        # Validate YAML syntax
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            app = self.app
            if isinstance(app, TerminalApp):
                app.flash(
                    f"Invalid YAML syntax: {e}",
                    style="error",
                )
            return

        # Save to file
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with self.config_path.open("w", encoding="utf-8") as f:
                f.write(content)

            app = self.app
            if isinstance(app, TerminalApp):
                app.flash(
                    f"Config saved to {self.config_path}",
                    style="success",
                )
            self.dismiss(True)
        except Exception as e:
            app = self.app
            if isinstance(app, TerminalApp):
                app.flash(
                    f"Failed to save config: {e}",
                    style="error",
                )

    @on(Button.Pressed, "#cancel")
    def on_cancel(self, event: Button.Pressed) -> None:
        """Cancel editing and close dialog."""
        event.stop()
        if self.dirty:
            # Could add confirmation dialog here
            pass
        self.dismiss(False)
