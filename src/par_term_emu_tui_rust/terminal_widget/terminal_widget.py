"""
Custom Textual widget that wraps par_term_emu.PtyTerminal for interactive shell sessions.
"""

from __future__ import annotations

import logging
import time
import webbrowser
from typing import TYPE_CHECKING, ClassVar

from par_term_emu_core_rust import CursorStyle, PtyTerminal
from par_term_emu_core_rust.debug import (
    debug_log,
    debug_trace,
    log_generation_check,
    log_widget_lifecycle,
)
from textual.geometry import Offset
from textual.reactive import reactive
from textual.widget import Widget

from par_term_emu_tui_rust import messages
from par_term_emu_tui_rust.config import TuiConfig

# Import managers and utilities
from par_term_emu_tui_rust.terminal_widget import theme_manager
from par_term_emu_tui_rust.terminal_widget.clipboard import ClipboardManager
from par_term_emu_tui_rust.terminal_widget.rendering import Renderer
from par_term_emu_tui_rust.terminal_widget.screenshot import ScreenshotManager
from par_term_emu_tui_rust.terminal_widget.selection import SelectionManager
from par_term_emu_tui_rust.utils import open_with_default_app
from par_term_emu_tui_rust.widgets.terminal_header import TerminalHeader

if TYPE_CHECKING:
    from textual.events import (
        Blur,
        Enter,
        Focus,
        Key,
        MouseDown,
        MouseMove,
        MouseScrollDown,
        MouseScrollUp,
        MouseUp,
        Resize,
    )
    from textual.strip import Strip


class TerminalWidget(Widget, can_focus=True):
    """An interactive terminal emulator widget with PTY support using par_term_emu.

    Threading Model:
    ----------------
    This widget is designed to work safely with Textual's async rendering:

    1. PTY Reader Thread (Rust):
       - Runs in background, reads PTY output
       - Only updates atomic counter (update_generation)
       - Never touches UI directly

    2. Textual Main Thread (asyncio event loop):
       - _poll_updates() runs via set_interval() in event loop
       - Checks generation counter and calls refresh() when needed
       - All mouse/key event handlers are async
       - All refresh() calls run in the event loop

    3. Rendering:
       - Textual coalesces multiple refresh() calls automatically
       - render_line() is called by Textual's rendering system
       - Only dirty regions are repainted

    This design ensures:
    - No race conditions (only atomic reads/writes between threads)
    - All UI updates happen in the correct thread
    - Efficient rendering (only when content changes)
    - Responsive input handling (mouse and keyboard)
    """

    DEFAULT_CSS = """
    TerminalWidget {
        width: 1fr;
        height: 1fr;
        color: white;
        padding: 0;
        margin: 0;
    }

    """

    # Key bindings
    BINDINGS: ClassVar = [
        ("ctrl+shift+c", "copy_selection", "Copy"),
        ("ctrl+shift+v", "paste_clipboard", "Paste"),
        ("ctrl+shift+s", "save_screenshot", "Screenshot"),
        ("ctrl+shift+pageup", "scroll_up", "Scroll Up"),
        ("ctrl+shift+pagedown", "scroll_down", "Scroll Down"),
        ("shift+home", "scroll_top", "Scroll to Top"),
        ("shift+end", "scroll_bottom", "Scroll to Bottom"),
    ]

    # Reactive attributes
    terminal_cols = reactive(80)
    terminal_rows = reactive(24)

    def __init__(
        self,
        cols: int = 80,
        rows: int = 24,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        shell_command: str | None = None,
        shell_path: str | None = None,
        config: TuiConfig | None = None,
    ) -> None:
        """Initialize the terminal widget.

        Args:
            cols: Number of columns in the terminal
            rows: Number of rows in the terminal
            name: The name of the widget
            id: The ID of the widget in the DOM
            classes: The CSS classes for the widget
            shell_command: Optional command to send to the shell after a 1-second delay
            shell_path: Optional path to shell executable (default: $SHELL or /bin/bash)
            config: Optional TUI configuration. If None, loads from default config file.
        """
        # Establish resizing guard before any reactive assignments that may trigger watchers
        self._resizing = True

        super().__init__(name=name, id=id, classes=classes)

        # Load configuration (from file if not provided)
        self.config = config if config is not None else TuiConfig.load()

        self.terminal_cols = cols
        self.terminal_rows = rows

        # Calculate scrollback lines (0 means unlimited, capped by max_scrollback_lines)
        scrollback = self.config.scrollback_lines
        if scrollback == 0:
            scrollback = self.config.max_scrollback_lines

        self.term = PtyTerminal(cols, rows, scrollback)

        # Apply theme colors BEFORE spawning shell so terminal starts with correct colors
        theme_bg = theme_manager.apply_theme(self.term, self.config)
        if theme_bg:
            debug_log("THEME", f"Applied theme in __init__, bg={theme_bg}")

        # Configure terminal security and feature settings based on config
        self.term.set_allow_clipboard_read(self.config.expose_system_clipboard)
        self.term.set_accept_osc7(self.config.accept_osc7)
        self.term.set_disable_insecure_sequences(self.config.disable_insecure_sequences)
        self.last_update_generation = 0
        self.render_generation = 0  # Generation snapshot for rendering (prevents stale rendering)
        self.last_bell_count = 0  # Track last bell count for detecting new bell events
        self._poll_interval = None
        self._mouse_button_state = None  # Track which button is pressed (None = no button)
        self._last_mouse_pos = (0, 0)  # Track last mouse position
        self._rendering_ready = False  # Prevent rendering before widget is fully initialized
        self._was_alt_screen = False  # Track alternate screen state
        self._alt_screen_switch_gen = None  # Generation when alt screen switched
        self._shell_command = shell_command  # Command to send after startup delay
        self._shell_path = shell_path  # Custom shell path (None = use default)
        self._command_timer = None  # Timer for delayed command sending
        self._pending_refresh = False  # Track if refresh is pending
        self._refresh_timer = None  # Timer for debounced refresh

        # Double/triple click tracking
        self._last_click_time = 0.0
        self._last_click_pos: tuple[int, int] | None = None
        self._click_count = 0

        # Cursor blink state
        self._cursor_blink_visible = True  # Current blink visibility state
        self._cursor_blink_timer = None  # Timer for cursor blinking

        # Scrollback state
        self._scroll_offset = 0  # Lines scrolled up from bottom (0 = at bottom)
        self._at_bottom = True  # True if viewing live terminal (not scrolled up)

        # Shell integration state tracking
        self._last_known_directory: str | None = None  # Track directory from OSC 7
        self._last_known_title: str = ""  # Track terminal title from OSC 0/1/2

        # Initialize managers
        self.selection = SelectionManager(
            term=self.term,
            config=self.config,
            get_terminal_cols=lambda: self.terminal_cols,
        )

        self.clipboard = ClipboardManager(
            term=self.term,
            config=self.config,
        )

        self.screenshot = ScreenshotManager(
            term=self.term,
            config=self.config,
            get_scroll_offset=lambda: self._scroll_offset,
        )

        self.renderer = Renderer(
            term=self.term,
            config=self.config,
            get_terminal_cols=lambda: self.terminal_cols,
            get_terminal_rows=lambda: self.terminal_rows,
            get_scroll_offset=lambda: self._scroll_offset,
            get_selection_start=lambda: self.selection.start,
            get_selection_end=lambda: self.selection.end,
            get_cursor_blink_visible=lambda: self._cursor_blink_visible,
        )

        # Set renderer default background from theme
        if theme_bg:
            self.renderer.set_default_background(theme_bg)
            debug_log("THEME", f"Set renderer default background in __init__: {theme_bg}")

        # End initial guarded section; watchers can run after init completes
        self._resizing = False  # Suppress watcher-triggered partial resizes

    @property
    def scroll_offset(self) -> Offset:
        """Get the current scrollback offset.

        Returns:
            Offset with y as number of lines scrolled up from the bottom (0 = at bottom, viewing live terminal)
        """
        return Offset(0, self._scroll_offset)

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        widget_id = str(self.id) if self.id else "unknown"
        log_widget_lifecycle(widget_id, f"mount size=({self.size.width}x{self.size.height})")
        try:
            # Resize terminal to match actual widget size before spawning
            # This ensures the terminal is the correct size from the start
            if self.size.width > 0 and self.size.height > 0:
                # Batch update to avoid watcher-triggered partial resizes (e.g. 190x24)
                self._resizing = True
                try:
                    self.terminal_cols = self.size.width
                    self.terminal_rows = self.size.height
                    # Compute pixel size if cell metrics available
                    px_w, px_h = self._get_cell_metrics()
                    if px_w and px_h:
                        self.term.resize_pixels(
                            self.size.width,
                            self.size.height,
                            self.size.width * px_w,
                            self.size.height * px_h,
                        )
                    else:
                        self.term.resize(self.size.width, self.size.height)
                    debug_log(
                        "LIFECYCLE",
                        f"resized terminal to {self.size.width}x{self.size.height}",
                    )
                finally:
                    self._resizing = False

            # Spawn an interactive shell
            # Note: The Rust PTY implementation automatically filters COLUMNS/LINES
            # from the child environment (see src/pty_session.rs:151-162)
            if self._shell_path:
                # Use custom shell path via spawn() method
                self.term.spawn(self._shell_path, None, None, None)
                debug_log(
                    "LIFECYCLE",
                    f"spawned custom shell '{self._shell_path}' for widget {widget_id}",
                )
            else:
                # Use default shell via spawn_shell() method
                self.term.spawn_shell()
                debug_log("LIFECYCLE", f"spawned default shell for widget {widget_id}")

            # Theme was already applied in __init__, just get the background color for widget styles
            # Re-apply theme to get the background color (theme_manager.apply_theme is idempotent)
            theme_bg = theme_manager.apply_theme(self.term, self.config)

            # Update widget background to match theme (can only be done after mount)
            logger = logging.getLogger("par_term_emu_tui_rust.terminal_widget")
            if theme_bg is not None:
                logger.info("Setting widget background to %s in on_mount", theme_bg)
                self.styles.background = theme_bg
                logger.info("Widget background set. Current value: %s", self.styles.background)
                debug_log("THEME", f"Set widget background in on_mount: {theme_bg}")
            else:
                logger.warning("theme_bg is None, not setting widget background")

            # Apply cursor style from config
            theme_manager.apply_cursor_style(self.term, self.config)

            # Set hyperlink color if clickable URLs are enabled
            if self.config.clickable_urls:
                r, g, b = self.config.link_color
                self.term.set_link_color(r, g, b)
                debug_log("HYPERLINKS", f"Set link color to RGB({r}, {g}, {b})")

            # Set search match highlight color (prepares for future search feature)
            r, g, b = self.config.search_match_color
            self.term.set_match_color(r, g, b)
            debug_log("SEARCH", f"Set search match color to RGB({r}, {g}, {b})")

            # Track initial generation
            self.last_update_generation = self.term.update_generation()
            self.render_generation = self.last_update_generation  # Initialize snapshot for first render
            debug_log("LIFECYCLE", f"initial generation: {self.last_update_generation}")

            # Set up polling interval to check for PTY updates
            # Poll every 16ms (~60Hz) for responsive updates and smooth scrollbar rendering
            # Higher polling rate reduces chance of capturing partial updates during scrollbar drags
            self._poll_interval = self.set_interval(0.016, self._poll_updates)

            # Check for initial directory from shell integration (OSC 7)
            # This will display the directory if shell integration is already active
            if self.config.accept_osc7:
                try:
                    shell_state = self.term.shell_integration_state()
                    if shell_state.cwd:
                        self._last_known_directory = shell_state.cwd
                        self.post_message(messages.DirectoryChanged(directory=shell_state.cwd))
                        debug_log("SHELL_INTEGRATION", f"Initial directory: {shell_state.cwd}")
                except Exception as e:
                    debug_log("SHELL_INTEGRATION", f"Error getting initial directory: {e}")

            # Mark rendering readiness
            # If size is unknown (0x0), defer rendering until first real on_resize
            if self.size.width > 0 and self.size.height > 0:
                self._rendering_ready = True
                debug_log("LIFECYCLE", "rendering ready - widget fully initialized")
            else:
                self._rendering_ready = False
                debug_log(
                    "LIFECYCLE",
                    "rendering deferred until first non-zero widget size",
                )

            # If a shell command was provided, schedule it to be sent after 1 second
            if self._shell_command:
                self._command_timer = self.set_timer(1.0, self._send_shell_command)
                debug_log(
                    "LIFECYCLE",
                    f"scheduled command '{self._shell_command}' for 1 second delay",
                )

            # Start cursor blink timer if enabled
            if self.config.cursor_blink_enabled:
                self._cursor_blink_timer = self.set_interval(
                    self.config.cursor_blink_rate,
                    self._toggle_cursor_blink,
                )
                debug_log(
                    "LIFECYCLE",
                    f"started cursor blink timer at {self.config.cursor_blink_rate}s interval",
                )

        except Exception as e:
            # If shell spawn fails, show error
            self.log(f"Failed to spawn shell: {e}")

    def on_unmount(self) -> None:
        """Called when the widget is unmounted."""
        widget_id = str(self.id) if self.id else "unknown"
        log_widget_lifecycle(widget_id, "unmount")
        # Stop polling
        if self._poll_interval is not None:
            self._poll_interval.stop()

        # Stop cursor blink timer
        if self._cursor_blink_timer is not None:
            self._cursor_blink_timer.stop()
            debug_log("LIFECYCLE", "stopped cursor blink timer")

        # Kill the shell process if still running
        if self.term.is_running():
            try:
                self.term.kill()
                debug_log("LIFECYCLE", f"killed shell for widget {widget_id}")
            except Exception as e:
                self.log(f"Error killing shell: {e}")

    def _send_shell_command(self) -> None:
        """Send the scheduled shell command to the PTY.

        This is called by the timer after a 1-second delay to allow the shell to settle.
        """
        if self._shell_command and self.term.is_running():
            debug_log("LIFECYCLE", f"sending command to shell: '{self._shell_command}'")
            # Send the command
            self.term.write_str(self._shell_command)
            # Send Enter key to execute the command
            self.term.write_str("\r")
            debug_log("LIFECYCLE", "command sent successfully")

    def _toggle_cursor_blink(self) -> None:
        """Toggle cursor blink visibility.

        This is called by the timer at regular intervals (cursor_blink_rate).
        Only toggles for blinking cursor styles (BlinkingBlock, BlinkingUnderline, BlinkingBar).
        Steady cursor styles (SteadyBlock, SteadyUnderline, SteadyBar) remain always visible.
        """
        if not self.config.cursor_blink_enabled:
            # Blinking disabled - cursor always visible
            self._cursor_blink_visible = True
            return

        # Get current cursor style
        cursor_style = self.term.cursor_style()
        cursor_style_int = int(cursor_style)

        # Only blink for blinking cursor styles
        is_blinking_style = cursor_style_int in (
            int(CursorStyle.BlinkingBlock),
            int(CursorStyle.BlinkingUnderline),
            int(CursorStyle.BlinkingBar),
        )

        if is_blinking_style:
            # Toggle visibility for blinking styles
            self._cursor_blink_visible = not self._cursor_blink_visible
            # Request a refresh to update the display
            self.refresh()
        # Steady cursor - always visible
        elif not self._cursor_blink_visible:
            self._cursor_blink_visible = True
            self.refresh()

    def on_resize(self, event: Resize) -> None:
        """Called when the widget is resized.

        Args:
            event: The resize event containing new dimensions
        """
        widget_id = str(self.id) if self.id else "unknown"
        # Update terminal dimensions based on widget's content area size
        # Use self.size which is the actual renderable area (excludes borders, scrollbars, etc.)
        # Each character cell is 1 column wide and 1 row tall
        new_cols = max(1, self.size.width)
        new_rows = max(1, self.size.height)

        # Only resize if dimensions changed and we have a terminal
        if hasattr(self, "term") and (new_cols != self.terminal_cols or new_rows != self.terminal_rows):
            log_widget_lifecycle(
                widget_id,
                f"resize {self.terminal_cols}x{self.terminal_rows} -> {new_cols}x{new_rows}",
            )

            # Update reactive properties
            # Batch update to prevent watcher-triggered partial resizes
            self._resizing = True
            try:
                self.terminal_cols = new_cols
                self.terminal_rows = new_rows
            finally:
                self._resizing = False

            # Resize the PTY terminal
            try:
                debug_log(
                    "RESIZE",
                    f"widget={widget_id} calling term.resize({new_cols}, {new_rows})",
                )
                # Compute pixel size if cell metrics available
                px_w, px_h = self._get_cell_metrics()
                if px_w and px_h:
                    self.term.resize_pixels(
                        new_cols,
                        new_rows,
                        new_cols * px_w,
                        new_rows * px_h,
                    )
                else:
                    self.term.resize(new_cols, new_rows)
                debug_log(
                    "RESIZE",
                    f"widget={widget_id} PTY resize successful, SIGWINCH sent to child process",
                )

                # Create a fresh snapshot at the new size for the renderer
                self.renderer.prepare_frame(widget_id)
                debug_log(
                    "RESIZE",
                    f"widget={widget_id} renderer prepared frame at new size",
                )

                # Note: We used to send Ctrl+L here to trigger redraw, but shells echo it
                # back as ^L which gets rendered as visible text. SIGWINCH is sufficient
                # to notify the child process of the resize.

                # Force a refresh to show the resized content
                # The snapshot we just created will be used for this render
                self.refresh()
                debug_log("RESIZE", f"widget={widget_id} refresh scheduled")

                # If rendering was deferred at mount (0x0 size), enable it now
                if not self._rendering_ready and new_cols > 0 and new_rows > 0:
                    self._rendering_ready = True
                    debug_log("LIFECYCLE", "rendering ready after first non-zero resize")
            except Exception as e:
                debug_log("RESIZE", f"widget={widget_id} resize FAILED: {e}")
                import traceback

                debug_log("RESIZE", f"Traceback: {traceback.format_exc()}")

    def _get_cell_metrics(self) -> tuple[int | None, int | None]:
        """Return (cell_px_w, cell_px_h) from env if provided, else (None, None).

        Users can export PAR_TERM_CELL_PX_W and PAR_TERM_CELL_PX_H to enable
        XTWINOPS 14 pixel reporting. If unset, we fall back to character-only
        resizes and Rust will approximate.
        """
        import os

        try:
            w = int(os.environ.get("PAR_TERM_CELL_PX_W", "0"))
            h = int(os.environ.get("PAR_TERM_CELL_PX_H", "0"))
            return w if w > 0 else None, h if h > 0 else None
        except Exception:
            return None, None

    def _poll_updates(self) -> None:
        """Poll for PTY updates and refresh if content changed.

        IMPORTANT: This method includes special handling for alternate screen switches
        to prevent capturing snapshots before content has been drawn. After switching
        to alternate screen, we wait for additional generation changes before refreshing,
        ensuring the screen has actual content.
        """
        widget_id = str(self.id) if self.id else "unknown"
        # Check if process has exited
        if not self.term.is_running():
            exit_code = self.term.try_wait()
            if exit_code is not None:
                self.log(f"Shell process exited with code: {exit_code}")
                debug_log("LIFECYCLE", f"shell exited with code {exit_code}")
                # Stop polling since process is dead
                if self._poll_interval is not None:
                    self._poll_interval.stop()
                # Exit TUI if configured to do so
                if self.config.exit_on_shell_exit:
                    debug_log("LIFECYCLE", "exit_on_shell_exit=True, exiting TUI")
                    self.app.exit()
            return

        # Check if there are updates using generation tracking
        current_gen = self.term.update_generation()
        if self.term.has_updates_since(self.last_update_generation):
            # Check if alternate screen status changed
            is_alt_screen = self.term.is_alt_screen_active()

            # Detect transition TO alternate screen
            if is_alt_screen and not self._was_alt_screen:
                # Just switched to alternate screen - record the generation
                self._was_alt_screen = True
                self._alt_screen_switch_gen = current_gen
                self.last_update_generation = current_gen
                debug_log(
                    "ALT_SCREEN",
                    f"widget={widget_id} switched to alternate at gen={current_gen}, waiting for content...",
                )
                # Don't refresh yet - wait for content to arrive
                return

            # If we recently switched to alt screen, wait for more changes
            if self._alt_screen_switch_gen is not None:
                gen_since_switch = current_gen - self._alt_screen_switch_gen
                if gen_since_switch < 2:
                    # Still too early - likely just mode changes, not actual content
                    self.last_update_generation = current_gen
                    debug_log(
                        "ALT_SCREEN",
                        f"widget={widget_id} gen delta={gen_since_switch}, still waiting...",
                    )
                    return
                # Enough generations passed, content likely arrived
                debug_log(
                    "ALT_SCREEN",
                    f"widget={widget_id} gen delta={gen_since_switch}, content ready",
                )
                self._alt_screen_switch_gen = None  # Clear the wait state

            # Detect transition FROM alternate screen
            if not is_alt_screen and self._was_alt_screen:
                self._was_alt_screen = False
                self._alt_screen_switch_gen = None
                debug_log("ALT_SCREEN", f"widget={widget_id} switched to primary")

            # Update our generation counter
            old_gen = self.last_update_generation
            self.last_update_generation = current_gen

            # CRITICAL: Snapshot the generation we're about to render
            # This prevents stale rendering if PTY updates during the render cycle
            self.render_generation = current_gen

            log_generation_check(widget_id, old_gen, current_gen)

            # Check for synchronized update mode and flush if active
            # This handles DEC 2026 synchronized update mode for smooth rendering
            if self.term.synchronized_updates():
                try:
                    self.term.flush_synchronized_updates()
                    debug_log("SYNC_UPDATES", f"flushed synchronized updates for widget {widget_id}")
                except Exception as e:
                    debug_log("SYNC_UPDATES", f"error flushing synchronized updates: {e}")

            # Debounce refresh to allow rapid successive updates to complete
            # This prevents partial rendering of scrollbar drags and other rapid updates
            if self._refresh_timer is not None:
                self._refresh_timer.stop()

            # Schedule refresh after a tiny delay (5ms) to batch rapid updates
            self._refresh_timer = self.set_timer(0.005, self._do_refresh)
            debug_trace("POLL", f"scheduled debounced refresh for widget {widget_id}")

        # Check for notifications (OSC 9/777) and display them
        if self.config.show_notifications and self.term.has_notifications():
            notifications = self.term.drain_notifications()
            for title, message in notifications:
                # Format notification based on whether it has a title
                notification_text = f"{title}: {message}" if title else message

                # Display using Textual's notification system
                self.notify(
                    notification_text,
                    timeout=self.config.notification_timeout,
                )
                debug_log(
                    "NOTIFICATION",
                    f"Displayed notification: title={title!r}, message={message!r}",
                )

        # Check for directory changes (OSC 7 shell integration)
        if self.config.accept_osc7:
            try:
                shell_state = self.term.shell_integration_state()
                current_dir = shell_state.cwd if shell_state.cwd else None

                # If directory changed, post message to app
                if current_dir and current_dir != self._last_known_directory:
                    self._last_known_directory = current_dir
                    self.post_message(messages.DirectoryChanged(directory=current_dir))
                    debug_log("SHELL_INTEGRATION", f"Directory changed to: {current_dir}")
            except Exception as e:
                debug_log("SHELL_INTEGRATION", f"Error checking directory: {e}")

        # Check for title changes (OSC 0/1/2)
        try:
            current_title = self.term.title()

            # If title changed, post message to app
            if current_title != self._last_known_title:
                self._last_known_title = current_title
                self.post_message(messages.TitleChanged(title=current_title))
                debug_log("TITLE", f"Title changed to: {current_title!r}")
        except Exception as e:
            debug_log("TITLE", f"Error checking title: {e}")

        # Check for bell events (BEL/\x07) if visual bell is enabled
        if self.config.visual_bell_enabled:
            try:
                current_bell_count = self.term.bell_count()

                # If bell count increased, show bell icon in header
                if current_bell_count > self.last_bell_count:
                    self.last_bell_count = current_bell_count
                    # Get the header widget and show bell icon
                    header = self.app.query_one(TerminalHeader)
                    header.show_bell()
                    debug_log("BELL", f"Bell event detected, count={current_bell_count}")
            except Exception as e:
                debug_log("BELL", f"Error checking bell: {e}")

    def _clear_bell(self) -> None:
        """Clear the bell icon from the header on user interaction."""
        try:
            header = self.app.query_one(TerminalHeader)
            header.hide_bell()
        except Exception as e:
            debug_log("BELL", f"Error clearing bell: {e}")

    def _do_refresh(self) -> None:
        """Execute the actual refresh after debounce delay."""
        widget_id = str(self.id) if self.id else "unknown"
        debug_trace("REFRESH", f"executing debounced refresh for widget {widget_id}")
        self._refresh_timer = None

        # CRITICAL: Prepare a fresh frame in the renderer before calling refresh()
        # This ensures all render_line() calls use the same atomic snapshot
        self.renderer.prepare_frame(widget_id)

        # Now trigger the actual refresh
        self.refresh()

    def render_line(self, y: int) -> Strip:
        """Render a line using the renderer.

        Args:
            y: The row index to render (0-based from top of widget)

        Returns:
            A Strip containing the rendered line
        """
        widget_id = str(self.id) if self.id else "unknown"
        return self.renderer.render_line(y, widget_id, self.size, self._rendering_ready)

    async def on_key(self, event: Key) -> None:
        """Handle key presses and send them to the PTY.

        Args:
            event: The key event
        """
        # Clear bell icon on any key press
        self._clear_bell()

        # Don't send keys if process isn't running
        if not self.term.is_running():
            return

        key = event.key
        debug_trace("KEY_EVENT", f"key={key} character={event.character}")

        # Let app-level keybindings pass through (don't consume them)
        # These are handled by the app, not the terminal widget
        app_level_keys = {
            "alt+ctrl+shift+c",  # Config editor
            "ctrl+shift+q",  # Quit
        }
        if key in app_level_keys:
            debug_log("KEY", f"Allowing app-level keybinding to pass through: {key}")
            return

        # Check for copy/paste shortcuts before processing other keys
        # Support standard OS shortcuts: Cmd+C/V (macOS) and Ctrl+C/V (Windows/Linux)
        # Note: Ctrl+Shift+C/V are also handled by BINDINGS for traditional terminal convention
        # In Textual, modifiers are encoded in the key string (e.g., "ctrl+v", "cmd+v")
        if key == "cmd+c":
            # Cmd+C on macOS
            debug_log("KEY", "cmd+c detected - triggering copy action")
            self.action_copy_selection()
            event.prevent_default()
            event.stop()
            return
        if key == "cmd+v":
            # Cmd+V on macOS
            debug_log("KEY", "cmd+v detected - triggering paste action")
            await self.action_paste_clipboard()
            event.prevent_default()
            event.stop()
            return
        if key == "ctrl+c":
            # Ctrl+C (without shift) - check if we have a selection
            # If we have a selection, copy it; otherwise send SIGINT to PTY
            if self.selection.start and self.selection.end:
                debug_log("KEY", "ctrl+c with selection - triggering copy action")
                self.action_copy_selection()
                event.prevent_default()
                event.stop()
                return
            # Otherwise, let it fall through to send Ctrl+C to PTY (SIGINT)
        elif key == "ctrl+v":
            # Ctrl+V (without shift) - standard paste shortcut
            # This takes precedence over sending Ctrl+V to the PTY
            debug_log("KEY", "ctrl+v detected - triggering paste action")
            await self.action_paste_clipboard()
            event.prevent_default()
            event.stop()
            return

        # Track if we handled the key
        handled = False

        # Clear selection on any input event (like iTerm2)
        # This happens when user types, but not for copy shortcuts
        # The selection remains visible only until user interacts with the terminal
        if self.selection.start or self.selection.end:
            debug_log("KEY", f"Clearing selection on input: {key}")
            self.selection.clear()
            self.refresh()

        try:
            # Map special keys to escape sequences
            if key == "enter":
                self.term.write_str("\r")
                handled = True
            elif key == "backspace":
                self.term.write_str("\x7f")  # DEL character (most shells expect this)
                handled = True
            elif key == "delete":
                self.term.write_str("\x1b[3~")
                handled = True
            elif key == "tab":
                self.term.write_str("\t")
                handled = True
            elif key == "space":
                self.term.write_str(" ")
                handled = True
            elif key == "ctrl+space":
                # Ctrl+Space sends NUL (0x00), same as Ctrl+@
                self.term.write_str("\x00")
                handled = True
                debug_log("KEY", "Sent Ctrl+Space as NUL (\\x00)")
            elif key in {"ctrl+left_square_bracket", "ctrl+["}:
                # Ctrl+[ is same as ESC (0x1b)
                self.term.write_str("\x1b")
                handled = True
                debug_log("KEY", "Sent Ctrl+[ as ESC (\\x1b)")
            elif key in {"ctrl+backslash", "ctrl+\\"}:
                # Ctrl+\ sends FS (0x1c) - SIGQUIT signal in Unix
                self.term.write_str("\x1c")
                handled = True
                debug_log("KEY", "Sent Ctrl+\\ as FS (\\x1c)")
            elif key in {"ctrl+right_square_bracket", "ctrl+]"}:
                # Ctrl+] sends GS (0x1d)
                self.term.write_str("\x1d")
                handled = True
                debug_log("KEY", "Sent Ctrl+] as GS (\\x1d)")
            elif key in {"ctrl+circumflex_accent", "ctrl+^", "ctrl+6"}:
                # Ctrl+^ or Ctrl+Shift+6 sends RS (0x1e)
                self.term.write_str("\x1e")
                handled = True
                debug_log("KEY", "Sent Ctrl+^ as RS (\\x1e)")
            elif key in {"ctrl+underscore", "ctrl+_", "ctrl+minus"}:
                # Ctrl+_ or Ctrl+Shift+- sends US (0x1f) - undo in some editors
                self.term.write_str("\x1f")
                handled = True
                debug_log("KEY", "Sent Ctrl+_ as US (\\x1f)")
            elif key == "escape":
                self.term.write_str("\x1b")
                handled = True
            elif key == "up":
                self.term.write_str("\x1b[A")
                handled = True
            elif key == "down":
                self.term.write_str("\x1b[B")
                handled = True
            elif key == "right":
                self.term.write_str("\x1b[C")
                handled = True
            elif key == "left":
                self.term.write_str("\x1b[D")
                handled = True
            elif key == "home":
                self.term.write_str("\x1b[H")
                handled = True
            elif key == "end":
                self.term.write_str("\x1b[F")
                handled = True
            elif key == "pageup":
                self.term.write_str("\x1b[5~")
                handled = True
            elif key == "pagedown":
                self.term.write_str("\x1b[6~")
                handled = True
            elif key == "insert":
                self.term.write_str("\x1b[2~")
                handled = True
            # Function keys
            elif key == "f1":
                self.term.write_str("\x1bOP")
                handled = True
            elif key == "f2":
                self.term.write_str("\x1bOQ")
                handled = True
            elif key == "f3":
                self.term.write_str("\x1bOR")
                handled = True
            elif key == "f4":
                self.term.write_str("\x1bOS")
                handled = True
            elif key == "f5":
                self.term.write_str("\x1b[15~")
                handled = True
            elif key == "f6":
                self.term.write_str("\x1b[17~")
                handled = True
            elif key == "f7":
                self.term.write_str("\x1b[18~")
                handled = True
            elif key == "f8":
                self.term.write_str("\x1b[19~")
                handled = True
            elif key == "f9":
                self.term.write_str("\x1b[20~")
                handled = True
            elif key == "f10":
                self.term.write_str("\x1b[21~")
                handled = True
            elif key == "f11":
                self.term.write_str("\x1b[23~")
                handled = True
            elif key == "f12":
                self.term.write_str("\x1b[24~")
                handled = True
            # Handle Ctrl+letter combinations (Ctrl+A through Ctrl+Z)
            # These produce control characters (ASCII 1-26)
            elif key.startswith("ctrl+") and len(key) == 6 and key[5].isalpha():
                letter = key[5].lower()
                # Calculate control character: Ctrl+A=1, Ctrl+B=2, ..., Ctrl+Z=26
                ctrl_char = chr(ord(letter) - ord("a") + 1)
                self.term.write_str(ctrl_char)
                handled = True
                debug_log(
                    "KEY",
                    f"Sent control character: Ctrl+{letter.upper()} = \\x{ord(ctrl_char):02x}",
                )
            # Handle printable characters
            elif event.character and len(event.character) == 1:
                self.term.write_str(event.character)
                handled = True

            if handled:
                debug_trace("KEY", f"sent to terminal: {key}")
        except Exception as e:
            self.log(f"Error handling key: {e}")

    def _calculate_modifiers(self, shift: bool, meta: bool, ctrl: bool) -> int:
        """Calculate modifier bitfield from boolean flags.

        The modifiers are encoded as a bitfield that gets shifted left by 2:
        - Shift: 1 (becomes 4 when encoded)
        - Meta/Alt: 2 (becomes 8 when encoded)
        - Control: 4 (becomes 16 when encoded)

        Args:
            shift: True if shift key is pressed
            meta: True if meta/alt key is pressed
            ctrl: True if ctrl key is pressed

        Returns:
            Integer bitfield combining all modifiers
        """
        modifiers = 0
        if shift:
            modifiers |= 1
        if meta:
            modifiers |= 2
        if ctrl:
            modifiers |= 4
        return modifiers

    def _send_mouse_event(
        self,
        button: int,
        col: int,
        row: int,
        pressed: bool,
        modifiers: int = 0,
    ) -> None:
        """Send a mouse event to the PTY using SGR (1006) encoding.

        Args:
            button: Mouse button code (0=left, 1=middle, 2=right)
            col: Column position (0-indexed, will be converted to 1-indexed)
            row: Row position (0-indexed, will be converted to 1-indexed)
            pressed: True for press/drag, False for release
            modifiers: Modifier bitfield (shift=1, meta=2, ctrl=4)
        """
        if not self.term.is_running():
            debug_log("MOUSE", "Not sending - terminal not running")
            return

        # Only send mouse events if mouse tracking is enabled
        mouse_mode = self.term.mouse_mode()
        if mouse_mode == "off":
            debug_log("MOUSE", f"Not sending - mouse mode is off (mode={mouse_mode})")
            return

        try:
            # Convert to 1-indexed coordinates for terminal
            x = col + 1
            y = row + 1

            # Clamp to valid range
            x = max(1, min(x, self.terminal_cols))
            y = max(1, min(y, self.terminal_rows))

            # Encode modifiers into button code (modifiers are shifted left by 2)
            button_code = button | (modifiers << 2)

            # SGR encoding: \x1b[<button;x;y;M for press, m for release
            final_char = "M" if pressed else "m"
            sequence = f"\x1b[<{button_code};{x};{y}{final_char}"

            debug_log(
                "MOUSE",
                f"Sending: mode={mouse_mode} button={button} pos=({col},{row}) pressed={pressed} seq={sequence!r}",
            )
            self.term.write_str(sequence)

        except Exception as e:
            self.log(f"Error sending mouse event: {e}")

    async def on_mouse_down(self, event: MouseDown) -> None:
        """Handle mouse button press.

        Args:
            event: The mouse down event
        """
        # Clear bell icon on any mouse click
        self._clear_bell()

        # Detect double and triple clicks for word/line selection
        current_time = time.time()
        current_pos = (event.x, event.y)
        double_click_threshold = 0.5  # 500ms
        position_tolerance = 2  # Allow 2 pixel tolerance for position matching

        # Check if this is a continuation of previous clicks
        # Use position tolerance to allow for slight mouse movement
        position_matches = False
        if self._last_click_pos is not None:
            dx = abs(current_pos[0] - self._last_click_pos[0])
            dy = abs(current_pos[1] - self._last_click_pos[1])
            position_matches = dx <= position_tolerance and dy <= position_tolerance

        time_matches = (current_time - self._last_click_time) < double_click_threshold

        if event.button == 1 and position_matches and time_matches:
            self._click_count += 1
            debug_log(
                "CLICK",
                f"Multi-click detected: count={self._click_count} pos={current_pos} last_pos={self._last_click_pos}",
            )
        else:
            self._click_count = 1
            debug_log(
                "CLICK",
                f"Single click: pos={current_pos} last_pos={self._last_click_pos} "
                f"pos_match={position_matches} time_match={time_matches}",
            )

        self._last_click_time = current_time
        self._last_click_pos = current_pos

        # Handle double-click (word selection)
        if event.button == 1 and self._click_count == 2:
            self.selection.select_word_at(event.x, event.y, self.renderer._frame_snapshot)
            self.selection.selecting = False
            # Auto-copy if configured (default: True)
            if self.config.auto_copy_selection:
                selected_text = self.selection.get_selected_text()
                if selected_text:
                    # Keep selection visible if configured (default: True, like iTerm2)
                    clear_after_copy = not self.config.keep_selection_after_copy
                    success, _ = self.clipboard.copy_to_clipboard(
                        selected_text,
                        to_primary=True,
                    )
                    if success and clear_after_copy:
                        self.selection.clear()
            self.refresh()
            event.stop()
            return

        # Handle triple-click (line selection)
        if event.button == 1 and self._click_count >= 3:
            self.selection.select_line_at(event.y, self.renderer._frame_snapshot)
            self.selection.selecting = False
            self._click_count = 3  # Cap at 3 to avoid overflow
            # Auto-copy if configured (default: True)
            if self.config.auto_copy_selection:
                selected_text = self.selection.get_selected_text()
                if selected_text:
                    # Keep selection visible if configured (default: True, like iTerm2)
                    clear_after_copy = not self.config.keep_selection_after_copy
                    success, _error = self.clipboard.copy_to_clipboard(
                        selected_text,
                        to_primary=True,
                    )
                    if success and clear_after_copy:
                        self.selection.clear()
            self.refresh()
            event.stop()
            return

        # Handle clickable URLs (single click only)
        if event.button == 1 and self._click_count == 1 and self.config.clickable_urls:
            # Check if required modifier key is pressed
            modifier_required = self.config.url_modifier.lower()
            modifier_pressed = False

            if modifier_required == "none":
                modifier_pressed = True
            elif modifier_required == "ctrl":
                modifier_pressed = event.ctrl
            elif modifier_required == "shift":
                modifier_pressed = event.shift
            elif modifier_required == "alt":
                modifier_pressed = event.meta

            if modifier_pressed:
                # Get terminal coordinates
                col = event.x
                row = event.y

                # Try OSC 8 hyperlink first
                url = self.term.get_hyperlink(col, row)
                if url:
                    debug_log("HYPERLINKS", f"OSC 8 hyperlink detected at ({col}, {row}): {url}")
                else:
                    # Fall back to auto-detected plain text URL
                    url = self.term.get_url_at(col, row)
                    if url:
                        debug_log("HYPERLINKS", f"Plain URL detected at ({col}, {row}): {url}")

                if url:
                    # Open URL in browser
                    try:
                        webbrowser.open(url)
                        debug_log("HYPERLINKS", f"Opened URL in browser: {url}")
                    except Exception as e:
                        debug_log("HYPERLINKS", f"Failed to open URL: {e}")

                    event.stop()
                    return

        # Check for selection mode (shift + left click)
        if event.shift and event.button == 1:
            # Start selection
            self.selection.start = (event.x, event.y)
            self.selection.end = (event.x, event.y)
            self.selection.selecting = True
            self.refresh()
            event.stop()
            return

        # Handle middle-click paste (button 2 in Textual)
        if event.button == 2 and self.config.middle_click_paste:
            # Paste from PRIMARY selection
            debug_log("MOUSE", "Middle-click paste triggered")
            await self.clipboard.paste_from_primary()
            event.stop()
            return

        # Clear selection on single click (like iTerm2)
        # Single click without shift means user is clicking somewhere else
        if event.button == 1 and self._click_count == 1 and not event.shift:
            if self.selection.start or self.selection.end:
                debug_log("MOUSE", "Clearing selection on single click")
                self.selection.clear()
                self.refresh()

        # Map Textual button to terminal button code
        # button=1 is left, button=2 is middle, button=3 is right in Textual
        button_map = {1: 0, 2: 1, 3: 2}  # Textual -> Terminal mapping
        button = button_map.get(event.button, 0)

        # Get widget-relative position
        col = event.x
        row = event.y

        # Calculate modifiers
        modifiers = self._calculate_modifiers(event.shift, event.meta, event.ctrl)

        self._mouse_button_state = button
        self._last_mouse_pos = (col, row)

        debug_log(
            "MOUSE_DOWN",
            f"button={event.button}→{button} pos=({col},{row}) state={self._mouse_button_state}",
        )

        self._send_mouse_event(button, col, row, pressed=True, modifiers=modifiers)

        # Capture mouse to ensure we get move/up events even if cursor leaves widget
        self.capture_mouse()

    async def on_mouse_up(self, event: MouseUp) -> None:
        """Handle mouse button release.

        Args:
            event: The mouse up event
        """
        # Finalize selection if in selection mode
        if self.selection.selecting:
            self.selection.selecting = False
            # Auto-copy if configured (default: True)
            if self.config.auto_copy_selection:
                if self.selection.start and self.selection.end:
                    selected_text = self.selection.get_selected_text()
                    if selected_text:
                        # Keep selection visible if configured (default: True, like iTerm2)
                        clear_after_copy = not self.config.keep_selection_after_copy
                        success, _error = self.clipboard.copy_to_clipboard(
                            selected_text,
                            to_primary=True,
                        )
                        if success and clear_after_copy:
                            self.selection.clear()
            self.refresh()
            event.stop()
            return

        # Map Textual button to terminal button code
        button_map = {1: 0, 2: 1, 3: 2}
        button = button_map.get(event.button, 0)

        # Get widget-relative position
        col = event.x
        row = event.y

        # Calculate modifiers
        modifiers = self._calculate_modifiers(event.shift, event.meta, event.ctrl)

        debug_log("MOUSE_UP", f"button={event.button}→{button} pos=({col},{row})")

        self._send_mouse_event(button, col, row, pressed=False, modifiers=modifiers)
        self._mouse_button_state = None  # Clear button state

        # Release mouse capture
        self.release_mouse()

    async def on_mouse_move(self, event: MouseMove) -> None:
        """Handle mouse movement and dragging.

        Sends motion events based on the mouse tracking mode:
        - ButtonEvent mode (1002): Only when a button is pressed (drag)
        - AnyEvent mode (1003): All mouse motion, even without button pressed

        Args:
            event: The mouse move event
        """
        # Update selection end while dragging
        if self.selection.selecting:
            self.selection.end = (event.x, event.y)
            self.refresh()
            event.stop()
            return

        col = event.x
        row = event.y

        # Calculate modifiers
        modifiers = self._calculate_modifiers(event.shift, event.meta, event.ctrl)

        # Get current mouse mode
        mouse_mode = self.term.mouse_mode()

        debug_log(
            "MOUSE_MOVE",
            f"pos=({col},{row}) button_state={self._mouse_button_state} mode={mouse_mode}",
        )

        # Send move events based on mode
        if self._mouse_button_state is not None and mouse_mode in ("button", "any"):
            # Dragging - send move event with button code + 32 (motion flag)
            # ButtonEvent (1002) and AnyEvent (1003) modes support drag
            motion_button = self._mouse_button_state + 32
            debug_log(
                "MOUSE_DRAG",
                f"Dragging with button={self._mouse_button_state} motion_button={motion_button}",
            )
            self._send_mouse_event(motion_button, col, row, pressed=True, modifiers=modifiers)
        elif mouse_mode == "any":
            # AnyEvent mode - send motion even without button pressed
            # Use button code 35 (3 + 32) for motion without button
            self._send_mouse_event(35, col, row, pressed=True, modifiers=modifiers)

        self._last_mouse_pos = (col, row)

    async def on_mouse_scroll_up(self, event: MouseScrollUp) -> None:
        """Handle mouse wheel scroll up.

        When mouse tracking is off, scrolls the scrollback buffer.
        When mouse tracking is on, sends scroll event to terminal application.

        Args:
            event: The scroll up event
        """
        # Check if mouse tracking is enabled
        mouse_mode = self.term.mouse_mode()

        if mouse_mode == "off":
            # Mouse tracking is off - use wheel for scrollback
            # Scroll up by configured number of lines
            self._scroll_by(self.config.mouse_wheel_scroll_lines)
        else:
            # Mouse tracking is on - send event to application
            col = event.x
            row = event.y

            # Calculate modifiers
            modifiers = self._calculate_modifiers(event.shift, event.meta, event.ctrl)

            # Scroll up button code is 64
            self._send_mouse_event(64, col, row, pressed=True, modifiers=modifiers)
            # Immediately send release
            self._send_mouse_event(64, col, row, pressed=False, modifiers=modifiers)

    async def on_mouse_scroll_down(self, event: MouseScrollDown) -> None:
        """Handle mouse wheel scroll down.

        When mouse tracking is off, scrolls the scrollback buffer.
        When mouse tracking is on, sends scroll event to terminal application.

        Args:
            event: The scroll down event
        """
        # Check if mouse tracking is enabled
        mouse_mode = self.term.mouse_mode()

        if mouse_mode == "off":
            # Mouse tracking is off - use wheel for scrollback
            # Scroll down by configured number of lines (negative for down)
            self._scroll_by(-self.config.mouse_wheel_scroll_lines)
        else:
            # Mouse tracking is on - send event to application
            col = event.x
            row = event.y

            # Calculate modifiers
            modifiers = self._calculate_modifiers(event.shift, event.meta, event.ctrl)

            # Scroll down button code is 65
            self._send_mouse_event(65, col, row, pressed=True, modifiers=modifiers)
            # Immediately send release
            self._send_mouse_event(65, col, row, pressed=False, modifiers=modifiers)

    async def on_focus(self, event: Focus) -> None:
        """Handle widget gaining focus.

        Sends focus in event if focus tracking mode is enabled.

        Args:
            event: The focus event
        """
        if not self.term.is_running():
            return

        # Check if focus tracking is enabled
        if self.term.focus_tracking():
            try:
                # Get the focus in event sequence from terminal
                focus_seq = self.term.get_focus_in_event()
                if focus_seq:
                    self.term.write_str(focus_seq)
                    debug_log("FOCUS", f"sent focus in event: {focus_seq!r}")
            except Exception as e:
                self.log(f"Error sending focus in event: {e}")

    async def on_blur(self, event: Blur) -> None:
        """Handle widget losing focus.

        Sends focus out event if focus tracking mode is enabled.

        Args:
            event: The blur event
        """
        if not self.term.is_running():
            return

        # Check if focus tracking is enabled
        if self.term.focus_tracking():
            try:
                # Get the focus out event sequence from terminal
                focus_seq = self.term.get_focus_out_event()
                if focus_seq:
                    self.term.write_str(focus_seq)
                    debug_log("FOCUS", f"sent focus out event: {focus_seq!r}")
            except Exception as e:
                self.log(f"Error sending focus out event: {e}")

    async def on_enter(self, event: Enter) -> None:
        """Handle mouse entering the widget.

        Respects config.focus_follows_mouse setting (default: False).
        When enabled, automatically focuses the terminal when mouse enters.

        Args:
            event: The enter event
        """
        if self.config.focus_follows_mouse:
            self.focus()
            debug_log("FOCUS", "auto-focused on mouse enter")

    def action_copy_selection(self) -> None:
        """Copy selected text to clipboard using pyperclip (cross-platform).

        Respects config.keep_selection_after_copy setting (default: True).
        When True, selection remains visible until next input event or new selection (like iTerm2).
        """
        if not self.selection.start or not self.selection.end:
            self.notify("No text selected", severity="warning")
            return

        # Get selected content from terminal
        selected_text = self.selection.get_selected_text()

        # Copy to clipboard
        success, error = self.clipboard.copy_to_clipboard(selected_text, to_primary=True)

        if success:
            self.notify(f"Copied {len(selected_text)} characters")
            # Keep selection visible if configured (default: True)
            if not self.config.keep_selection_after_copy:
                self.selection.clear()
                self.refresh()
        else:
            self.notify(f"Failed to copy: {error}", severity="error")

    async def action_paste_clipboard(self) -> None:
        """Paste clipboard content to terminal using pyperclip (cross-platform).

        Respects config settings:
        - paste_warn_size: Warns before pasting large content
        - paste_chunk_size: Splits paste into chunks if > 0
        - paste_chunk_delay_ms: Delay between chunks
        """
        success, message = await self.clipboard.paste_from_clipboard()

        if success:
            if message:
                # Show message (could be warning or success message)
                self.notify(message)
        # Show error
        elif message:
            self.notify(message, severity="error")

    def action_save_screenshot(self) -> None:
        """Save a screenshot of the current terminal state.

        Directory selection priority:
        1. Config screenshot_directory (if set)
        2. Shell's current working directory (from OSC 7)
        3. XDG_PICTURES_DIR/Screenshots or ~/Pictures/Screenshots
        4. Home directory

        Uses configured screenshot_format (default: PNG) with timestamp-based filename.
        """
        filepath, error = self.screenshot.save()

        if filepath:
            # Format path for display
            display_path = ScreenshotManager.format_path_for_display(filepath)
            self.post_message(messages.Flash(f"Screenshot saved: {display_path}", "default", 5.0))
            debug_log("SCREENSHOT", f"Saved screenshot to {filepath}")

            # Open screenshot with default viewer if configured
            if self.config and self.config.open_screenshot_after_capture:
                if open_with_default_app(filepath):
                    debug_log("SCREENSHOT", "Opened screenshot with default viewer")
                else:
                    debug_log("SCREENSHOT", "Failed to open screenshot with default viewer")
        elif error:
            self.notify(error, severity="error")
        else:
            self.notify("Failed to save screenshot", severity="error")

    def action_scroll_up(self) -> None:
        """Scroll up one page in scrollback."""
        scroll_amount = max(1, self.terminal_rows - 1)  # Scroll almost a full page
        self._scroll_by(scroll_amount)

    def action_scroll_down(self) -> None:
        """Scroll down one page in scrollback."""
        scroll_amount = max(1, self.terminal_rows - 1)  # Scroll almost a full page
        self._scroll_by(-scroll_amount)

    def action_scroll_top(self) -> None:
        """Scroll to top of scrollback."""
        scrollback_len = self.term.scrollback_len()
        if scrollback_len > 0:
            # Scroll to show oldest scrollback line
            self._scroll_offset = scrollback_len
            self._at_bottom = False
            self.refresh()
            debug_log("SCROLL", f"Scrolled to top: offset={self._scroll_offset}")

    def action_scroll_bottom(self) -> None:
        """Scroll to bottom (live terminal view)."""
        if not self._at_bottom:
            self._scroll_offset = 0
            self._at_bottom = True
            self.refresh()
            debug_log("SCROLL", "Scrolled to bottom (live view)")

    def _scroll_by(self, lines: int) -> None:
        """Scroll by a number of lines (positive = up, negative = down).

        Args:
            lines: Number of lines to scroll (positive scrolls up into history)
        """
        scrollback_len = self.term.scrollback_len()
        if scrollback_len == 0 and lines > 0:
            # No scrollback available
            return

        # Calculate new offset
        new_offset = self._scroll_offset + lines

        # Clamp to valid range: [0, scrollback_len]
        new_offset = max(0, min(new_offset, scrollback_len))

        if new_offset != self._scroll_offset:
            self._scroll_offset = new_offset
            self._at_bottom = new_offset == 0
            self.refresh()
            debug_log(
                "SCROLL",
                f"Scrolled by {lines}: new offset={self._scroll_offset}, at_bottom={self._at_bottom}",
            )

    def resize_terminal(self, cols: int, rows: int) -> None:
        """Resize the terminal and send SIGWINCH to the shell process.

        Args:
            cols: New number of columns
            rows: New number of rows
        """
        try:
            self.term.resize(cols, rows)
            self.terminal_cols = cols
            self.terminal_rows = rows
            # CRITICAL: Invalidate the renderer's snapshot so next render creates a new one at the new size
            self.renderer._frame_snapshot = None
            self.renderer._frame_lines = []
            self.renderer._frame_hyperlink_cache.clear()
            self.refresh()
        except Exception as e:
            self.log(f"Error resizing terminal: {e}")

    def watch_terminal_cols(self, new_cols: int) -> None:
        """React to terminal_cols changes."""
        # Skip if we're batching a resize (on_resize/on_mount)
        if getattr(self, "_resizing", False):
            return
        if hasattr(self, "term") and self.terminal_rows > 0:
            self.resize_terminal(new_cols, self.terminal_rows)

    def watch_terminal_rows(self, new_rows: int) -> None:
        """React to terminal_rows changes."""
        # Skip if we're batching a resize (on_resize/on_mount)
        if getattr(self, "_resizing", False):
            return
        if hasattr(self, "term") and self.terminal_cols > 0:
            self.resize_terminal(self.terminal_cols, new_rows)
