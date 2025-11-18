"""Configuration screen with widget-based and raw YAML editing."""

from __future__ import annotations

import logging
from dataclasses import fields
from typing import TYPE_CHECKING, ClassVar, get_type_hints

from ruamel.yaml import YAML
from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, Select, Static, TabbedContent, TabPane, TextArea

from par_term_emu_tui_rust.config import TuiConfig
from par_term_emu_tui_rust.themes import THEMES

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult

logger = logging.getLogger(__name__)


class ConfigScreen(ModalScreen[bool]):
    """Configuration screen with tabbed interface for widget-based and raw YAML editing."""

    DEFAULT_CSS = """
    ConfigScreen {
        background: black 75%;
        align: center middle;

        &> Vertical {
            background: $surface;
            width: 95%;
            height: 95%;
            min-width: 100;
            min-height: 40;
            border: thick $panel;
            border-title-color: $primary;
            padding: 1;

            TabbedContent {
                height: 1fr;
            }

            TabPane {
                height: 1fr;
                padding: 0;
            }

            VerticalScroll {
                height: 100%;
                width: 100%;
                padding: 1;
            }

            .config_section {
                border: solid $panel;
                padding: 1;
                margin-bottom: 1;
                background: $surface-darken-1;
                height: auto;
            }

            .section_title {
                text-style: bold;
                color: $accent;
                margin-bottom: 1;
                height: 1;
            }

            .config_row {
                height: 3;
                margin-bottom: 0;
            }

            .config_label {
                width: 40;
                height: 3;
                padding-right: 2;
                content-align: right middle;
            }

            .config_input {
                width: 20;
                height: 3;
            }

            Checkbox.config_input {
                width: 7;
            }

            Input.config_input_number {
                width: 10;
            }

            Select.config_input {
                width: 45;
            }

            .config_help {
                color: $text-muted;
                margin-left: 42;
                margin-top: 0;
                margin-bottom: 2;
                height: auto;
            }

            #button_bar {
                height: auto;
                align: right middle;
                padding: 1 1 0 1;
            }

            #config_path {
                height: auto;
                padding: 0 1 1 1;
                color: $text-muted;
            }

            TextArea {
                height: 1fr;
            }
        }
    }
    """

    BINDINGS: ClassVar = [
        Binding("escape", "dismiss(False)", "Cancel", show=True),
        Binding("ctrl+s", "save", "Save", show=True),
    ]

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize the config screen.

        Args:
            config_path: Optional path to config file. If None, uses default config path.
        """
        super().__init__()
        self.config_path = config_path if config_path is not None else TuiConfig.default_config_path()
        self.config = TuiConfig.load(self.config_path)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.width = 4096  # Prevent line wrapping
        self.raw_yaml_content = ""
        self.dirty = False

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        with Vertical() as v:
            v.border_title = "Configuration"

            # Show config file path
            yield Static(f"File: {self.config_path}", id="config_path")

            with TabbedContent(initial="settings_tab"):
                with TabPane("Settings", id="settings_tab"):
                    yield from self._create_settings_tab()

                with TabPane("Raw YAML", id="raw_yaml_tab"):
                    yield from self._create_raw_yaml_tab()

            # Button bar
            with Horizontal(id="button_bar"):
                yield Button("Save", id="save", variant="primary")
                yield Button("Cancel", id="cancel")

    def _create_settings_tab(self) -> ComposeResult:
        """Create the widget-based settings tab."""
        scroll = VerticalScroll()

        # Selection & Clipboard Section
        with scroll:
            with Container(classes="config_section"):
                yield Label("Selection & Clipboard", classes="section_title")

                yield from self._create_checkbox_row(
                    "auto_copy_selection", "Auto-copy selection:", "Automatically copy selected text to clipboard"
                )
                yield from self._create_checkbox_row(
                    "keep_selection_after_copy", "Keep selection after copy:", "Keep text highlighted after copying"
                )
                yield from self._create_checkbox_row(
                    "expose_system_clipboard",
                    "Expose system clipboard:",
                    "Allow terminal apps to read system clipboard (OSC 52)",
                )
                yield from self._create_checkbox_row(
                    "copy_trailing_newline", "Copy trailing newline:", "Include trailing newline when copying lines"
                )
                yield from self._create_input_row(
                    "word_characters",
                    "Word characters:",
                    "Characters considered part of a word for double-click selection",
                )
                yield from self._create_checkbox_row(
                    "triple_click_selects_wrapped_lines",
                    "Triple-click selects wrapped:",
                    "Select full wrapped lines on triple-click",
                )

            # Scrollback Section
            with Container(classes="config_section"):
                yield Label("Scrollback & Buffer", classes="section_title")

                yield from self._create_input_row(
                    "scrollback_lines",
                    "Scrollback lines:",
                    "Maximum lines in scrollback buffer (0 = unlimited up to max)",
                    input_type="integer",
                )
                yield from self._create_input_row(
                    "max_scrollback_lines",
                    "Max scrollback lines:",
                    "Safety limit for unlimited scrollback",
                    input_type="integer",
                )

            # Cursor Section
            with Container(classes="config_section"):
                yield Label("Cursor", classes="section_title")

                yield from self._create_checkbox_row(
                    "cursor_blink_enabled", "Cursor blink enabled:", "Enable cursor blinking for blinking cursor styles"
                )
                yield from self._create_input_row(
                    "cursor_blink_rate", "Cursor blink rate:", "Cursor blink interval in seconds", input_type="number"
                )
                yield from self._create_select_row(
                    "cursor_style",
                    "Cursor style:",
                    "Default cursor appearance",
                    [
                        ("Blinking Block", "blinking_block"),
                        ("Steady Block", "steady_block"),
                        ("Blinking Underline", "blinking_underline"),
                        ("Steady Underline", "steady_underline"),
                        ("Blinking Bar", "blinking_bar"),
                        ("Steady Bar", "steady_bar"),
                    ],
                )

            # Paste Section
            with Container(classes="config_section"):
                yield Label("Paste", classes="section_title")

                yield from self._create_input_row(
                    "paste_chunk_size",
                    "Paste chunk size:",
                    "Paste in chunks (bytes, 0 = paste all at once)",
                    input_type="integer",
                )
                yield from self._create_input_row(
                    "paste_chunk_delay_ms",
                    "Paste chunk delay (ms):",
                    "Delay between paste chunks in milliseconds",
                    input_type="integer",
                )
                yield from self._create_input_row(
                    "paste_warn_size",
                    "Paste warn size:",
                    "Warn before pasting content larger than this (bytes)",
                    input_type="integer",
                )

            # Mouse Section
            with Container(classes="config_section"):
                yield Label("Mouse", classes="section_title")

                yield from self._create_checkbox_row(
                    "focus_follows_mouse", "Focus follows mouse:", "Auto-focus terminal on mouse hover"
                )
                yield from self._create_checkbox_row(
                    "middle_click_paste", "Middle-click paste:", "Paste on middle mouse button click"
                )
                yield from self._create_input_row(
                    "mouse_wheel_scroll_lines",
                    "Mouse wheel scroll lines:",
                    "Number of lines to scroll per mouse wheel tick",
                    input_type="integer",
                )

            # Theme Section
            with Container(classes="config_section"):
                yield Label("Theme & Colors", classes="section_title")

                theme_choices = [(theme.name, key) for key, theme in sorted(THEMES.items())]
                yield from self._create_select_row("theme", "Theme:", "Color theme to use for terminal", theme_choices)
                yield from self._create_checkbox_row(
                    "bold_brightening",
                    "Bold brightening:",
                    "Use bright ANSI colors (8-15) for bold text with normal colors (0-7)",
                )
                yield from self._create_input_row(
                    "minimum_contrast",
                    "Minimum contrast:",
                    "Minimum contrast adjustment for live display (0.0-1.0)",
                    input_type="number",
                )

            # Hyperlinks Section
            with Container(classes="config_section"):
                yield Label("Hyperlinks & URLs", classes="section_title")

                yield from self._create_checkbox_row(
                    "clickable_urls", "Clickable URLs:", "Enable clicking URLs to open in browser"
                )
                yield from self._create_select_row(
                    "url_modifier",
                    "URL modifier:",
                    "Modifier key required for URL clicks",
                    [
                        ("None", "none"),
                        ("Ctrl", "ctrl"),
                        ("Shift", "shift"),
                        ("Alt", "alt"),
                    ],
                )
                yield from self._create_input_row(
                    "link_color",
                    "Link color (R,G,B):",
                    "RGB color tuple for hyperlinks (e.g., 100,150,255)",
                    input_type="color",
                )
                yield from self._create_checkbox_row(
                    "warn_on_unknown_url_scheme",
                    "Warn on unknown URL scheme:",
                    "Warn when blocking URLs with unsupported schemes",
                )

            # Screenshot Section
            with Container(classes="config_section"):
                yield Label("Screenshot", classes="section_title")

                yield from self._create_input_row(
                    "screenshot_directory",
                    "Screenshot directory:",
                    "Directory to save screenshots (empty = auto-detect)",
                    allow_empty=True,
                )
                yield from self._create_select_row(
                    "screenshot_format",
                    "Screenshot format:",
                    "File format for screenshots",
                    [
                        ("PNG", "png"),
                        ("JPEG", "jpeg"),
                        ("BMP", "bmp"),
                        ("SVG", "svg"),
                        ("HTML", "html"),
                    ],
                )
                yield from self._create_input_row(
                    "screenshot_minimum_contrast",
                    "Screenshot minimum contrast:",
                    "Minimum contrast adjustment for screenshots (0.0-1.0)",
                    input_type="number",
                )
                yield from self._create_checkbox_row(
                    "open_screenshot_after_capture",
                    "Open screenshot after capture:",
                    "Automatically open screenshot with default viewer",
                )

            # Notifications Section
            with Container(classes="config_section"):
                yield Label("Notifications", classes="section_title")

                yield from self._create_checkbox_row(
                    "show_notifications", "Show notifications:", "Display OSC 9/777 notifications as toast messages"
                )
                yield from self._create_input_row(
                    "notification_timeout",
                    "Notification timeout:",
                    "Duration in seconds to display notifications",
                    input_type="integer",
                )

            # Shell & Security Section
            with Container(classes="config_section"):
                yield Label("Shell & Security", classes="section_title")

                yield from self._create_checkbox_row(
                    "exit_on_shell_exit", "Exit on shell exit:", "Exit TUI when shell exits"
                )
                yield from self._create_checkbox_row(
                    "accept_osc7", "Accept OSC 7:", "Allow directory tracking via OSC 7 sequences"
                )
                yield from self._create_checkbox_row(
                    "disable_insecure_sequences",
                    "Disable insecure sequences:",
                    "Block potentially risky escape sequences (not implemented)",
                )

            # UI Elements Section
            with Container(classes="config_section"):
                yield Label("UI Elements", classes="section_title")

                yield from self._create_checkbox_row(
                    "show_status_bar", "Show status bar:", "Show or hide the status bar at the bottom"
                )
                yield from self._create_checkbox_row(
                    "visual_bell_enabled", "Visual bell enabled:", "Enable visual bell indicator (bell icon in header)"
                )

            # Keyboard Protocol Section
            with Container(classes="config_section"):
                yield Label("Keyboard Protocol (KITTY)", classes="section_title")

                yield from self._create_checkbox_row(
                    "keyboard_protocol_enabled",
                    "Keyboard protocol enabled:",
                    "Enable KITTY keyboard protocol for embedded apps",
                )
                yield from self._create_input_row(
                    "keyboard_protocol_flags",
                    "Keyboard protocol flags:",
                    "Flags: 1=disambiguate, 2=events, 4=alternate, 8=report_all, 16=text (combine by adding)",
                    input_type="integer",
                )
                yield from self._create_checkbox_row(
                    "keyboard_protocol_auto_detect",
                    "Auto-detect keyboard protocol:",
                    "Auto-detect and enable when apps request protocol",
                )

            # Search Section
            with Container(classes="config_section"):
                yield Label("Search & Highlighting", classes="section_title")

                yield from self._create_input_row(
                    "search_match_color",
                    "Search match color (R,G,B):",
                    "RGB color tuple for search matches (e.g., 255,255,0)",
                    input_type="color",
                )

        yield scroll

    def _create_raw_yaml_tab(self) -> ComposeResult:
        """Create the raw YAML editing tab."""
        scroll = VerticalScroll()
        with scroll:
            text_area = TextArea(
                id="raw_yaml_editor",
                language="yaml",
                theme="monokai",
                show_line_numbers=True,
                tab_behavior="indent",
            )
            yield text_area
        yield scroll

    def _create_checkbox_row(self, field_name: str, label: str, help_text: str) -> ComposeResult:
        """Create a checkbox configuration row."""
        with Horizontal(classes="config_row"):
            yield Label(label, classes="config_label")
            checkbox = Checkbox(value=getattr(self.config, field_name), id=f"field_{field_name}")
            checkbox.add_class("config_input")
            yield checkbox
        yield Static(help_text, classes="config_help")

    def _create_input_row(
        self,
        field_name: str,
        label: str,
        help_text: str,
        input_type: str = "text",
        allow_empty: bool = False,
    ) -> ComposeResult:
        """Create an input configuration row."""
        value = getattr(self.config, field_name)

        # Handle None values for optional fields
        if value is None:
            value_str = ""
        elif input_type == "color":
            # Convert tuple to comma-separated string
            value_str = ",".join(str(v) for v in value)
        else:
            value_str = str(value)

        with Horizontal(classes="config_row"):
            yield Label(label, classes="config_label")
            input_widget = Input(
                value=value_str,
                id=f"field_{field_name}",
                placeholder="(auto-detect)" if allow_empty else "",
            )
            input_widget.add_class("config_input")
            if input_type in ("integer", "number"):
                input_widget.add_class("config_input_number")
            yield input_widget
        yield Static(help_text, classes="config_help")

    def _create_select_row(
        self,
        field_name: str,
        label: str,
        help_text: str,
        choices: list[tuple[str, str]],
    ) -> ComposeResult:
        """Create a select configuration row."""
        value = getattr(self.config, field_name)

        # Check if value exists in choices, if not use first choice
        choice_values = [choice[1] for choice in choices]
        if value not in choice_values and choices:
            value = choices[0][1]

        with Horizontal(classes="config_row"):
            yield Label(label, classes="config_label")
            select = Select(
                options=choices,
                value=value,
                id=f"field_{field_name}",
                allow_blank=False,
            )
            select.add_class("config_input")
            yield select
        yield Static(help_text, classes="config_help")

    async def on_mount(self) -> None:
        """Mount the view and load config file content."""
        # Load raw YAML content
        try:
            if not self.config_path.exists():
                # Create default config file if it doesn't exist
                self.config.save(self.config_path)

            with self.config_path.open(encoding="utf-8") as f:
                self.raw_yaml_content = f.read()

        except Exception as e:
            self.raw_yaml_content = f"# Error loading config: {e}\n"

        # Populate raw YAML editor after a short delay to ensure it's mounted
        self.set_timer(0.1, self._populate_raw_yaml_editor)

    def _populate_raw_yaml_editor(self) -> None:
        """Populate the raw YAML editor with content."""
        try:
            text_area = self.query_one("#raw_yaml_editor", TextArea)
            text_area.text = self.raw_yaml_content
        except Exception:
            # Widget not found or not mounted yet, will try again on tab change
            pass

    @on(TabbedContent.TabActivated)
    def on_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Handle tab activation to ensure content is loaded."""
        event.stop()
        if event.pane.id == "raw_yaml_tab":
            self._populate_raw_yaml_editor()

    @on(Checkbox.Changed)
    def mark_dirty_checkbox(self, event: Checkbox.Changed) -> None:
        """Mark config as dirty when checkbox changes."""
        self.dirty = True

    @on(Input.Changed)
    def mark_dirty_input(self, event: Input.Changed) -> None:
        """Mark config as dirty when input changes."""
        self.dirty = True

    @on(Select.Changed)
    def mark_dirty_select(self, event: Select.Changed) -> None:
        """Mark config as dirty when select changes."""
        self.dirty = True

    @on(TextArea.Changed, "#raw_yaml_editor")
    def mark_dirty_textarea(self, event: TextArea.Changed) -> None:
        """Mark config as dirty when raw YAML changes."""
        self.dirty = True

    @on(Button.Pressed, "#save")
    async def action_save(self, event: Button.Pressed | None = None) -> None:
        """Save the config file."""
        if event:
            event.stop()

        # Check which tab is active
        tabbed_content = self.query_one(TabbedContent)
        active_tab = tabbed_content.active

        if active_tab == "settings_tab":
            await self._save_from_widgets()
        else:
            await self._save_from_raw_yaml()

    async def _save_from_widgets(self) -> None:
        """Save configuration from widget values."""
        try:
            # Load existing YAML to preserve comments and structure
            yaml_data = None
            if self.config_path.exists():
                with self.config_path.open(encoding="utf-8") as f:
                    yaml_data = self.yaml.load(f)

            if yaml_data is None:
                yaml_data = {}

            # Get actual types (not string annotations) using get_type_hints
            type_hints = get_type_hints(TuiConfig)

            # Update values from widgets
            for field in fields(TuiConfig):
                widget_id = f"field_{field.name}"
                field_type = type_hints.get(field.name, field.type)

                try:
                    converted_value = None

                    if field_type is bool:
                        widget = self.query_one(f"#{widget_id}", Checkbox)
                        converted_value = widget.value
                    elif "Select" in str(type(self.query_one(f"#{widget_id}"))):
                        widget = self.query_one(f"#{widget_id}", Select)
                        converted_value = widget.value
                    else:
                        widget = self.query_one(f"#{widget_id}", Input)
                        value_str = widget.value.strip()

                        # Get the field type as a string for robust checking
                        field_type_str = str(field.type)

                        # Handle empty optional fields
                        if not value_str and field.default is None:
                            converted_value = None
                        # Handle tuple[int, int, int] for colors
                        elif "tuple" in field_type_str and "int" in field_type_str:
                            if value_str:
                                parts = [int(p.strip()) for p in value_str.split(",")]
                                if len(parts) != 3:
                                    msg = f"Color must have 3 values (R,G,B), got {len(parts)}"
                                    raise ValueError(msg)
                                converted_value = parts
                            else:
                                converted_value = field.default
                        # Handle list[str]
                        elif "list" in field_type_str:
                            # Don't update allowed_url_schemes from widgets (too complex)
                            continue
                        # Handle integer types (including int and any union with int)
                        elif field_type is int or (
                            hasattr(field_type, "__origin__") and int in getattr(field_type, "__args__", ())
                        ):
                            converted_value = (
                                int(value_str) if value_str else (field.default if field.default is not None else 0)
                            )
                        # Handle float types (including float and any union with float)
                        elif field_type is float or (
                            hasattr(field_type, "__origin__") and float in getattr(field_type, "__args__", ())
                        ):
                            converted_value = (
                                float(value_str) if value_str else (field.default if field.default is not None else 0.0)
                            )
                        # String or unknown types
                        else:
                            converted_value = value_str if value_str else field.default

                    # Apply validation if we have a non-None value
                    if converted_value is not None:
                        converted_value = TuiConfig._validate_value(field.name, converted_value, field_type)

                    yaml_data[field.name] = converted_value

                except Exception:
                    # Skip widgets that don't exist or can't be converted
                    continue

            # Backup existing config file before overwriting
            if self.config_path.exists():
                from datetime import UTC, datetime

                backup_path = self.config_path.with_suffix(
                    f".yaml.backup.{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
                )
                try:
                    backup_path.write_text(self.config_path.read_text(encoding="utf-8"), encoding="utf-8")
                    logger.info("Backed up config to %s", backup_path)
                except Exception as e:
                    logger.warning("Failed to backup config: %s", e)

            # Save using ruamel.yaml to preserve comments and formatting
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config_path.open("w", encoding="utf-8") as f:
                self.yaml.dump(yaml_data, f)

            from par_term_emu_tui_rust.app import TerminalApp

            app = self.app
            if isinstance(app, TerminalApp):
                app.flash(f"Config saved to {self.config_path}", style="success")

            self.dirty = False
            self.dismiss(True)

        except Exception as e:
            from par_term_emu_tui_rust.app import TerminalApp

            app = self.app
            if isinstance(app, TerminalApp):
                app.flash(f"Failed to save config: {e}", style="error")

    async def _save_from_raw_yaml(self) -> None:
        """Save configuration from raw YAML editor."""
        from par_term_emu_tui_rust.app import TerminalApp

        text_area = self.query_one("#raw_yaml_editor", TextArea)
        content = text_area.text

        # Validate YAML syntax
        try:
            self.yaml.load(content)
        except Exception as e:
            app = self.app
            if isinstance(app, TerminalApp):
                app.flash(f"Invalid YAML syntax: {e}", style="error")
            return

        # Save to file
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config_path.open("w", encoding="utf-8") as f:
                f.write(content)

            app = self.app
            if isinstance(app, TerminalApp):
                app.flash(f"Config saved to {self.config_path}", style="success")

            self.dirty = False
            self.dismiss(True)

        except Exception as e:
            app = self.app
            if isinstance(app, TerminalApp):
                app.flash(f"Failed to save config: {e}", style="error")

    @on(Button.Pressed, "#cancel")
    def on_cancel(self, event: Button.Pressed) -> None:
        """Cancel editing and close screen."""
        event.stop()
        self.dismiss(False)
