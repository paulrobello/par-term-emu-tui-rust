"""Screenshot capture and management for terminal widget."""

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from par_term_emu_core_rust.debug import debug_log

if TYPE_CHECKING:
    from collections.abc import Callable

    from par_term_emu_core_rust import PtyTerminal

    from par_term_emu_tui_rust.config import TuiConfig


class ScreenshotManager:
    """Manages screenshot capture and file management."""

    def __init__(
        self,
        term: PtyTerminal,
        config: TuiConfig,
        get_scroll_offset: Callable[[], int],
    ) -> None:
        """Initialize screenshot manager.

        Args:
            term: Terminal instance
            config: TUI configuration
            get_scroll_offset: Callable that returns current scroll offset
        """
        self.term = term
        self.config = config
        self.get_scroll_offset = get_scroll_offset

    def get_directory(self) -> str:
        """Determine the best directory to save screenshots.

        Priority order:
        1. Config screenshot_directory (if set)
        2. Shell's current working directory (from OSC 7)
        3. XDG_PICTURES_DIR/Screenshots or ~/Pictures/Screenshots
        4. Home directory

        Returns:
            Path to directory where screenshot should be saved
        """
        # 1. Check if user configured a specific directory
        if self.config and self.config.screenshot_directory:
            config_dir = Path(self.config.screenshot_directory).expanduser()
            if config_dir.is_dir():
                return str(config_dir)
            # Create it if it doesn't exist
            try:
                config_dir.mkdir(parents=True, exist_ok=True)
                return str(config_dir)
            except OSError:
                pass  # Fall through to next option

        # 2. Try to get shell's current working directory from OSC 7
        try:
            shell_state = self.term.shell_integration_state()
            if shell_state.cwd and Path(shell_state.cwd).is_dir():
                debug_log("SCREENSHOT", f"Using shell CWD from OSC 7: {shell_state.cwd}")
                return shell_state.cwd
        except Exception:
            pass  # Fall through to next option

        # 3. Try XDG Pictures/Screenshots or ~/Pictures/Screenshots
        # Check XDG_PICTURES_DIR environment variable first
        xdg_pictures = os.environ.get("XDG_PICTURES_DIR")
        if xdg_pictures:
            screenshots_dir = Path(xdg_pictures).expanduser() / "Screenshots"
        else:
            # Fall back to ~/Pictures/Screenshots
            screenshots_dir = Path.home() / "Pictures" / "Screenshots"

        try:
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            debug_log("SCREENSHOT", f"Using screenshots directory: {screenshots_dir}")
            return str(screenshots_dir)
        except OSError:
            pass  # Fall through to final fallback

        # 4. Final fallback: home directory
        home_dir = Path.home()
        debug_log("SCREENSHOT", f"Falling back to home directory: {home_dir}")
        return str(home_dir)

    def save(self) -> tuple[str | None, str | None]:
        """Save a screenshot of the current terminal state.

        Uses configured screenshot_format (default: PNG) with timestamp-based filename.

        Returns:
            Tuple of (filepath, error_message). If successful, filepath is set and
            error_message is None. If failed, filepath is None and error_message is set.
        """
        try:
            # Get screenshot format from config
            screenshot_format = self.config.screenshot_format if self.config else "png"

            # Generate filename with timestamp
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"terminal_screenshot_{timestamp}.{screenshot_format}"

            # Determine save directory
            save_dir = self.get_directory()
            filepath = Path(save_dir) / filename

            # Save screenshot based on format
            scroll_offset = self.get_scroll_offset()
            if screenshot_format == "html":
                # Use export_html for HTML format
                html_content = self.term.export_html(include_styles=True)
                with filepath.open("w", encoding="utf-8") as f:
                    f.write(html_content)
                debug_log("SCREENSHOT", "Exported HTML screenshot")
            else:
                # Use screenshot_to_file for image formats
                self.term.screenshot_to_file(
                    str(filepath),
                    format=screenshot_format,
                    scrollback_offset=scroll_offset,
                )
                debug_log(
                    "SCREENSHOT",
                    f"Capturing screenshot with scroll_offset={scroll_offset}",
                )

            debug_log("SCREENSHOT", f"Saved screenshot to {filepath}")
            return str(filepath), None

        except Exception as e:
            error_msg = f"Failed to save screenshot: {e}"
            debug_log("SCREENSHOT", f"Screenshot error: {e}")
            return None, error_msg

    @staticmethod
    def format_path_for_display(filepath: str) -> str:
        """Format filepath for display, showing relative path if in current directory.

        Args:
            filepath: Absolute path to file

        Returns:
            Relative path if in current directory, otherwise absolute path
        """
        try:
            cwd = Path.cwd()
            file_path = Path(filepath)
            if file_path.is_relative_to(cwd):
                return str(file_path.relative_to(cwd))
            return filepath
        except (ValueError, OSError):
            # Different drives on Windows or other path issues
            return filepath
