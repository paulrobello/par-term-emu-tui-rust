"""
Main Textual application for the terminal emulator demo.
"""

import argparse
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer

from par_term_emu_tui_rust import messages
from par_term_emu_tui_rust.config import TuiConfig
from par_term_emu_tui_rust.terminal_widget import TerminalWidget
from par_term_emu_tui_rust.terminal_widget.screenshot import ScreenshotManager
from par_term_emu_tui_rust.themes import list_themes
from par_term_emu_tui_rust.utils import open_with_default_app
from par_term_emu_tui_rust.widgets.flash_line import FlashLine
from par_term_emu_tui_rust.widgets.status_bar import StatusBar
from par_term_emu_tui_rust.widgets.terminal_header import TerminalHeader

if TYPE_CHECKING:
    from textual.content import Content


def setup_debug_logging() -> Path:
    """Set up debug logging to timestamped file.

    Returns:
        Path to debug log file
    """
    # Create debug directory
    debug_dir = Path("debug_logs")
    debug_dir.mkdir(exist_ok=True)

    # Create timestamped log file
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    log_file = debug_dir / f"terminal_debug_{timestamp}.log"

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )

    logger = logging.getLogger("par_term_emu_tui_rust")
    logger.info("Debug logging started - %s", log_file)

    return log_file


class TerminalApp(App):
    """A Textual app demonstrating the par-term-emu-tui-rust terminal emulator."""

    TITLE = "PAR TERM"
    SUB_TITLE = ""
    ALLOW_SELECT = False
    ENABLE_COMMAND_PALETTE = False

    BINDINGS: ClassVar = [
        ("ctrl+q", "", ""),  # Disable default Ctrl+Q quit binding
        ("ctrl+c", "", ""),  # Disable default Ctrl+C quit warning binding
        ("ctrl+shift+q", "quit", "Quit"),
        ("alt+ctrl+shift+c", "edit_config", "Edit Config"),
    ]
    AUTO_FOCUS = "TerminalWidget"

    def __init__(
        self,
        shell_command: str | None = None,
        shell_path: str | None = None,
        config: TuiConfig | None = None,
        debug_mode: bool = False,
        auto_quit_seconds: float | None = None,
        screenshot_after_seconds: float | None = None,
        open_screenshot: bool = False,
    ) -> None:
        """Initialize the app with an optional shell command to send after startup.

        Args:
            shell_command: Optional command to send to the shell after a 1-second delay.
            shell_path: Optional path to shell executable (default: $SHELL or /bin/bash).
            config: Optional TUI configuration. If None, loads from default config file.
            debug_mode: Enable debug logging to file (default: False).
            auto_quit_seconds: Optional seconds to wait before auto-quitting.
            screenshot_after_seconds: Optional seconds to wait before taking screenshot.
            open_screenshot: Open screenshot with default system viewer after capture.
        """
        super().__init__()
        self.shell_command = shell_command
        self.shell_path = shell_path
        self.config = config if config is not None else TuiConfig.load()
        self.debug_mode = debug_mode
        self.auto_quit_seconds = auto_quit_seconds
        self.screenshot_after_seconds = screenshot_after_seconds
        self.open_screenshot = open_screenshot
        self.logger = logging.getLogger("par_term_emu_tui_rust.app") if debug_mode else None
        self.screenshot_path: Path | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield TerminalHeader()
        yield TerminalWidget(
            id="terminal",
            shell_command=self.shell_command,
            shell_path=self.shell_path,
            config=self.config,
        )
        # Always yield status bar, but hide it if disabled in config
        status_bar = StatusBar()
        if not self.config.show_status_bar:
            status_bar.styles.display = "none"
        yield status_bar
        yield FlashLine()
        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted.

        Sets focus to the terminal widget so it receives keyboard input.
        If auto_quit_seconds is set, schedules automatic exit.
        If screenshot_after_seconds is set, schedules screenshot capture.
        """
        # Schedule screenshot if provided
        if self.screenshot_after_seconds is not None:
            self.set_timer(self.screenshot_after_seconds, self._take_screenshot)

        # Schedule auto-quit if provided
        if self.auto_quit_seconds is not None:
            self.set_timer(self.auto_quit_seconds, self._auto_quit)

    def _take_screenshot(self) -> None:
        """Take a screenshot of the terminal buffer after specified delay.

        Uses the shared ScreenshotManager logic to capture the current terminal
        view, including scrollback offset, and saves it to the directory selected
        by TuiConfig and shell integration:

        1. Config screenshot_directory (if set)
        2. Shell CWD from OSC 7 (if available)
        3. XDG_PICTURES_DIR/Screenshots or ~/Pictures/Screenshots
        4. Home directory

        Logs the screenshot path if debug mode is enabled and optionally opens
        it with the system default application.
        """
        try:
            # Get the terminal widget
            terminal = self.query_one(TerminalWidget)

            # Use the same screenshot path and format logic as the widget action
            manager = ScreenshotManager(
                term=terminal.term,
                config=self.config,
                get_scroll_offset=lambda: terminal.scroll_offset.y,
            )
            screenshot_str, error = manager.save()
            if not screenshot_str or error:
                if self.logger:
                    self.logger.error("Failed to capture screenshot: %s", error or "unknown error")
                return

            screenshot_path = Path(screenshot_str)
            # Store screenshot path for later display (e.g., on exit)
            self.screenshot_path = screenshot_path

            if self.logger:
                self.logger.info("Screenshot saved to: %s", screenshot_path)

            # Open screenshot with default viewer if requested
            # Check both CLI flag and config option
            if self.open_screenshot or self.config.open_screenshot_after_capture:
                if open_with_default_app(screenshot_path):
                    if self.logger:
                        self.logger.info("Opened screenshot with default viewer")
                elif self.logger:
                    self.logger.error("Failed to open screenshot with default viewer")

        except Exception:
            if self.logger:
                self.logger.exception("Failed to capture screenshot")

    def _auto_quit(self) -> None:
        """Automatically quit the application after specified delay.

        Called by timer when auto_quit_seconds has elapsed.
        Logs the exit if debug mode is enabled.
        """
        if self.logger:
            self.logger.info("Auto-quitting after %s seconds", self.auto_quit_seconds)

        self.exit()

    @on(messages.Flash)
    def on_flash(self, event: messages.Flash) -> None:
        event.stop()
        self.flash(event.content, duration=event.duration, style=event.style)

    @on(messages.DirectoryChanged)
    def on_directory_changed(self, event: messages.DirectoryChanged) -> None:
        """Handle directory change from shell integration (OSC 7)."""
        event.stop()
        # Only update status bar if it's enabled in config
        if not self.config.show_status_bar:
            return

        # Update status bar with current directory
        # Shorten home directory to ~
        directory = event.directory
        home = str(Path.home())
        if directory.startswith(home):
            directory = "~" + directory[len(home) :]

        status_bar = self.query_one(StatusBar)
        status_bar.update_content(f"📁 {directory}", style="default")
        # Make sure status bar is displayed when updating content
        status_bar.styles.display = "block"
        status_bar.styles.visibility = "visible"

    @on(messages.TitleChanged)
    def on_title_changed(self, event: messages.TitleChanged) -> None:
        """Handle terminal title change from OSC 0/1/2."""
        event.stop()
        # Update app subtitle with the terminal title
        if event.title:
            self.sub_title = event.title
        else:
            # Reset to default subtitle if title is empty
            self.sub_title = ""

    def flash(
        self,
        content: str | Content,
        *,
        duration: float | None = None,
        style: Literal["default", "warning", "error", "success"] = "default",
    ) -> None:
        """Flash a single-line message to the user.

        Args:
            content: Content to flash.
            style: A semantic style.
            duration: Duration in seconds of the flash, or `None` to use default in settings.
        """
        self.query_one(FlashLine).flash(content, duration=duration, style=style, location="top")

    async def action_edit_config(self) -> None:
        """Open the config file editor dialog."""
        from par_term_emu_tui_rust.dialogs import ConfigEditDialog

        await self.push_screen(ConfigEditDialog())


def main(
    shell_command: str | None = None,
    shell_path: str | None = None,
    config: TuiConfig | None = None,
) -> None:
    """Run the terminal app.

    Args:
        shell_command: Optional command to pass to TerminalApp. If None, will parse
                      from command-line arguments.
        shell_path: Optional path to shell executable. If None, will parse from
                   command-line arguments or use default.
        config: Optional TUI configuration. If None, loads from default config file.
    """
    # Handle install subcommand before argparse
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        from par_term_emu_tui_rust.installer import handle_install_command

        exit_code = handle_install_command(sys.argv[2:])
        sys.exit(exit_code)

    parsed_args = False
    theme_override = None
    log_file = None

    # Only parse arguments if shell_command wasn't provided directly
    if shell_command is None and shell_path is None:
        parsed_args = True
        parser = argparse.ArgumentParser(
            description="PAR Terminal Emulator - Rust backend with Python TUI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"Configuration file: {TuiConfig.default_config_path()}",
        )
        parser.add_argument(
            "--debug",
            "-d",
            action="store_true",
            help="Enable debug logging to timestamped file in debug_logs/",
        )
        parser.add_argument(
            "--shell",
            "-s",
            default=None,
            help="Shell to execute (default: $SHELL on Unix, PowerShell/cmd.exe on Windows)",
        )
        parser.add_argument(
            "--command",
            "-c",
            type=str,
            default=None,
            help="Command to inject into prompt after 1 second delay",
        )
        parser.add_argument(
            "--auto-quit",
            "-q",
            type=float,
            default=None,
            metavar="SECONDS",
            help="Automatically quit after specified seconds",
        )
        parser.add_argument(
            "--screenshot",
            type=float,
            default=None,
            metavar="SECONDS",
            help="Take screenshot of terminal buffer after specified seconds",
        )
        parser.add_argument(
            "--open-screenshot",
            action="store_true",
            help="Open screenshot with default system viewer after capture",
        )
        parser.add_argument(
            "--init-config",
            action="store_true",
            help="Create default config.yaml in the XDG config directory and exit",
        )
        parser.add_argument(
            "--export-theme",
            metavar="NAME",
            type=str,
            default=None,
            help="Export the current theme as NAME and exit",
        )
        parser.add_argument(
            "--apply-theme",
            metavar="NAME",
            type=str,
            default=None,
            help="Apply a built-in theme NAME to config.yaml and exit",
        )
        parser.add_argument(
            "--list-themes",
            action="store_true",
            help="List available built-in themes and exit",
        )
        parser.add_argument(
            "--apply-theme-from",
            metavar="FILE",
            type=str,
            default=None,
            help="Apply a theme from a YAML file path to config.yaml and exit",
        )
        parser.add_argument(
            "--theme",
            type=str,
            help="Color theme to use for this session (overrides config file)",
            default=None,
        )
        args = parser.parse_args()

        # Setup debug logging if requested
        if args.debug:
            log_file = setup_debug_logging()

        # Handle CLI utility modes that don't launch the TUI
        if args.init_config:
            try:
                from rich.console import Console

                console = Console()
                cfg_path = TuiConfig.default_config_path()
                if cfg_path.exists():
                    console.print(f"[yellow]Config file already exists:[/yellow] {cfg_path}")
                else:
                    TuiConfig().save(cfg_path)
                    console.print(f"[green]Created default config file:[/green] {cfg_path}")
                return
            except Exception as e:
                from rich.console import Console

                console = Console()
                console.print(f"[red]Failed to initialize config:[/red] {e}")
                return

        if args.list_themes:
            try:
                from rich.console import Console

                console = Console()
                console.print("[bold]Available themes:[/bold]")
                for theme_name in list_themes():
                    console.print(f" • {theme_name}")
            except Exception:  # Printing theme list is best-effort; fall through to exit
                pass
            return

        if args.export_theme:
            try:
                from dataclasses import asdict

                from .themes import get_theme

                cfg_path = TuiConfig.default_config_path()
                cfg = TuiConfig.load(cfg_path) if cfg_path.exists() else TuiConfig()

                # Get current theme from config
                theme = get_theme(cfg.theme)

                # Create themes directory in XDG config
                themes_dir = cfg_path.parent / "themes"
                themes_dir.mkdir(parents=True, exist_ok=True)

                # Export theme to YAML file
                import yaml

                # Export all theme fields so the file can be re-imported
                theme_data = asdict(theme)
                theme_data["name"] = args.export_theme

                theme_path = themes_dir / f"{args.export_theme}.yaml"
                with theme_path.open("w", encoding="utf-8") as f:
                    yaml.safe_dump(theme_data, f, default_flow_style=False, sort_keys=False)

                try:
                    from rich.console import Console

                    console = Console()
                    console.print(f"[green]Exported theme to:[/green] {theme_path}")
                except Exception:
                    # If rich isn't available, silently succeed
                    pass

                return
            except Exception as e:
                try:
                    from rich.console import Console

                    console = Console(stderr=True)
                    console.print(f"[red]Failed to export theme:[/red] {e}")
                except Exception:
                    pass
                return

        if args.apply_theme:
            try:
                from rich.console import Console

                from .themes import get_theme

                cfg_path = TuiConfig.default_config_path()
                cfg = TuiConfig.load(cfg_path) if cfg_path.exists() else TuiConfig()

                # Validate theme exists
                get_theme(args.apply_theme)  # Raises ValueError if not found

                # Apply theme to config
                cfg.theme = args.apply_theme
                cfg.save(cfg_path)

                console = Console()
                console.print(
                    f"[green]Applied theme '{args.apply_theme}' to config:[/green] {cfg_path}",
                )
                return
            except Exception as e:
                try:
                    from rich.console import Console

                    console = Console(stderr=True)
                    console.print(f"[red]Failed to apply theme '{args.apply_theme}':[/red] {e}")
                except Exception:
                    pass
                return

        if args.apply_theme_from:
            try:
                import yaml
                from rich.console import Console

                from .themes import Theme

                cfg_path = TuiConfig.default_config_path()
                cfg = TuiConfig.load(cfg_path) if cfg_path.exists() else TuiConfig()

                # Load theme from file
                theme_file = Path(args.apply_theme_from)
                if not theme_file.exists():
                    console = Console(stderr=True)
                    console.print(f"[red]Theme file not found:[/red] {theme_file}")
                    return

                with theme_file.open(encoding="utf-8") as f:
                    theme_data = yaml.safe_load(f)

                # Validate theme data
                if not isinstance(theme_data, dict):
                    console = Console(stderr=True)
                    console.print(f"[red]Theme file must contain a mapping (YAML object):[/red] {theme_file}")
                    return

                # Require all Theme fields so we can fully validate and round-trip
                from dataclasses import fields

                required_keys = {field.name for field in fields(Theme)}
                missing_keys = required_keys - set(theme_data.keys())
                if missing_keys:
                    console = Console(stderr=True)
                    missing = ", ".join(sorted(missing_keys))
                    console.print(
                        f"[red]Theme file is missing required keys:[/red] {missing}\nFile: {theme_file}",
                    )
                    return

                # Validate theme
                Theme(**theme_data)

                # Save theme to user themes directory
                themes_dir = cfg_path.parent / "themes"
                themes_dir.mkdir(parents=True, exist_ok=True)

                theme_name = theme_data["name"].lower().replace(" ", "-")
                theme_path = themes_dir / f"{theme_name}.yaml"

                with theme_path.open("w", encoding="utf-8") as f:
                    yaml.safe_dump(theme_data, f, default_flow_style=False, sort_keys=False)

                # Apply to config
                cfg.theme = theme_name
                cfg.save(cfg_path)

                # Inform user and exit
                console = Console()
                console.print(
                    f"[green]Imported theme '{theme_data['name']}' "
                    f"and saved as key '{theme_name}' in:[/green] {themes_dir}",
                )
                console.print(
                    f"[green]Updated config theme to:[/green] {theme_name} ({cfg_path})",
                )

                return
            except Exception as e:
                try:
                    from rich.console import Console

                    console = Console(stderr=True)
                    console.print(f"[red]Failed to apply theme from file:[/red] {e}")
                except Exception:
                    pass
                return

        if shell_command is None:
            shell_command = args.command
        if shell_path is None:
            shell_path = args.shell
        theme_override = args.theme
        auto_quit_seconds = args.auto_quit
        screenshot_after_seconds = args.screenshot
        open_screenshot = args.open_screenshot
        debug_mode = args.debug
    else:
        # Parameters were provided directly, use defaults for others
        auto_quit_seconds = None
        screenshot_after_seconds = None
        open_screenshot = False
        debug_mode = False

    # Load config if not provided
    if config is None:
        config = TuiConfig.load()

    # Override theme from command line if provided
    if parsed_args and theme_override is not None:
        config.theme = theme_override

    app = TerminalApp(
        shell_command=shell_command,
        shell_path=shell_path,
        config=config,
        debug_mode=debug_mode,
        auto_quit_seconds=auto_quit_seconds,
        screenshot_after_seconds=screenshot_after_seconds,
        open_screenshot=open_screenshot,
    )
    try:
        app.run()
    finally:
        if log_file is not None:
            try:
                from rich.console import Console

                console = Console()
                console.print(f"[blue]Debug log:[/blue] {log_file}")
                if app.screenshot_path:
                    console.print(f"[blue]Last screenshot:[/blue] {app.screenshot_path}")
            except Exception:
                # If rich isn't available or the console fails, don't crash application shutdown
                pass


if __name__ == "__main__":
    main()
