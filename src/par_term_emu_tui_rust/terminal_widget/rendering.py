"""Rendering logic for terminal widget."""

from functools import lru_cache
from typing import TYPE_CHECKING, Any

from par_term_emu_core_rust import CursorStyle
from par_term_emu_core_rust.debug import (
    DebugLevel,
    debug_log,
    debug_trace,
    is_enabled,
    log_render_call,
    log_render_content,
    log_screen_corruption,
)
from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

if TYPE_CHECKING:
    from collections.abc import Callable

    from par_term_emu_core_rust import PtyTerminal

    from par_term_emu_tui_rust.config import TuiConfig


@lru_cache(maxsize=1024)
def _rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex color string with caching.

    Caches up to 256 color conversions to avoid repeated string formatting
    in the render loop. Most terminal color palettes use 256 colors or less,
    so this cache size provides excellent hit rates.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Hex color string in format "#rrggbb"
    """
    return f"#{r:02x}{g:02x}{b:02x}"


@lru_cache(maxsize=512)
def _create_style(
    color: str | None = None,
    bgcolor: str | None = None,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    dim: bool = False,
    blink: bool = False,
    strike: bool = False,
) -> Style:
    """Create a Rich Style object with caching.

    Caches up to 512 unique style combinations to avoid repeated Style object
    construction in the render loop. Common attribute combinations (e.g.,
    bold white on black, underlined blue, etc.) are reused across frames.

    Args:
        color: Foreground color (hex string like "#rrggbb" or None)
        bgcolor: Background color (hex string like "#rrggbb" or None)
        bold: Bold attribute
        italic: Italic attribute
        underline: Underline attribute
        dim: Dim attribute
        blink: Blink attribute
        strike: Strikethrough attribute

    Returns:
        Rich Style object with the specified attributes
    """
    kwargs = {}
    if color is not None:
        kwargs["color"] = color
    if bgcolor is not None:
        kwargs["bgcolor"] = bgcolor
    if bold:
        kwargs["bold"] = True
    if italic:
        kwargs["italic"] = True
    if underline:
        kwargs["underline"] = True
    if dim:
        kwargs["dim"] = True
    if blink:
        kwargs["blink"] = True
    if strike:
        kwargs["strike"] = True
    return Style(**kwargs)


class Renderer:
    """Handles rendering of terminal content to Rich segments."""

    def __init__(
        self,
        term: PtyTerminal,
        config: TuiConfig,
        get_terminal_cols: Callable[[], int],
        get_terminal_rows: Callable[[], int],
        get_scroll_offset: Callable[[], int],
        get_selection_start: Callable[[], tuple[int, int] | None],
        get_selection_end: Callable[[], tuple[int, int] | None],
        get_cursor_blink_visible: Callable[[], bool],
    ) -> None:
        """Initialize the renderer with dependencies.

        Args:
            term: Terminal instance
            config: TUI configuration
            get_terminal_cols: Callable that returns current terminal columns
            get_terminal_rows: Callable that returns current terminal rows
            get_scroll_offset: Callable that returns current scroll offset
            get_selection_start: Callable that returns selection start (col, row) or None
            get_selection_end: Callable that returns selection end (col, row) or None
            get_cursor_blink_visible: Callable that returns cursor blink visibility state
        """
        self.term = term
        self.config = config

        # Callables to get current widget state
        self._get_terminal_cols = get_terminal_cols
        self._get_terminal_rows = get_terminal_rows
        self._get_scroll_offset = get_scroll_offset
        self._get_selection_start = get_selection_start
        self._get_selection_end = get_selection_end
        self._get_cursor_blink_visible = get_cursor_blink_visible

        # Frame-level state (set by prepare_frame, used by render_line)
        self._frame_snapshot = None
        self._frame_lines = []
        self._frame_hyperlink_cache = {}

        # Default background color from theme (hex string like "#2e3436")
        self._default_bg_color: str | None = None

    def set_default_background(self, bg_color: str) -> None:
        """Set the default background color to use when cells have no explicit background.

        Args:
            bg_color: Hex color string like "#rrggbb"
        """
        self._default_bg_color = bg_color

    def prepare_frame(self, widget_id: str) -> None:
        """Prepare frame state for rendering.

        Creates an atomic snapshot of the terminal state and pre-fetches all lines
        to ensure consistent rendering across all render_line calls.

        Args:
            widget_id: Widget identifier for debug logging
        """
        # Create atomic snapshot for this frame
        self._frame_snapshot = self.term.create_snapshot()
        debug_log(
            "SNAPSHOT",
            f"widget={widget_id} created snapshot: gen={self._frame_snapshot.generation}",
        )

        # OPTIMIZATION: Pre-fetch ALL lines from snapshot to avoid per-line cloning
        # This is much faster than calling get_line() separately in render_line()
        # because it reduces the number of Rust->Python FFI calls and cloning operations
        _term_cols, term_rows = self._frame_snapshot.size
        self._frame_lines = [self._frame_snapshot.get_line(y) for y in range(term_rows)]
        debug_trace(
            "OPTIMIZE",
            f"widget={widget_id} pre-fetched {len(self._frame_lines)} lines for frame",
        )

        # OPTIMIZATION: Clear hyperlink cache for new frame
        # Shared across all render_line() calls in this frame to avoid dict allocations
        self._frame_hyperlink_cache.clear()

    def _render_graphic_line(self, graphic: Any, row: int, term_cols: int) -> list[Segment]:
        """Render a line of a Sixel graphic using Unicode half-blocks.

        Uses the upper half block character '▀' (U+2580) to display graphics:
        - Foreground color = top pixel
        - Background color = bottom pixel
        - Achieves 2:1 vertical compression

        Args:
            graphic: The Graphic object to render
            row: The terminal row being rendered
            term_cols: Number of terminal columns

        Returns:
            List of Segment objects for this line, or empty list if no overlap
        """
        _gfx_col, gfx_row = graphic.position
        gfx_width = graphic.width
        gfx_height = graphic.height

        # Calculate which pixel rows of the graphic correspond to this terminal row
        # Each terminal row displays 2 pixel rows (using half blocks)
        pixel_row_start = (row - gfx_row) * 2

        # Check if this row overlaps the graphic
        if pixel_row_start < 0 or pixel_row_start >= gfx_height:
            return []

        segments = []
        for x in range(gfx_width):
            # Get top pixel (for foreground)
            top_pixel = graphic.get_pixel(x, pixel_row_start) if pixel_row_start < gfx_height else None
            # Get bottom pixel (for background)
            bottom_pixel = graphic.get_pixel(x, pixel_row_start + 1) if pixel_row_start + 1 < gfx_height else None

            # Build style for this half-block
            style_kwargs = {}

            if top_pixel:
                r, g, b, a = top_pixel
                if a > 0:  # Only if not fully transparent
                    style_kwargs["color"] = _rgb_to_hex(r, g, b)

            if bottom_pixel:
                r, g, b, a = bottom_pixel
                if a > 0:  # Only if not fully transparent
                    style_kwargs["bgcolor"] = _rgb_to_hex(r, g, b)

            # Use upper half block character
            char = "▀" if top_pixel or bottom_pixel else " "

            if style_kwargs:
                # Use cached style creation for better performance
                style = _create_style(
                    color=style_kwargs.get("color"),
                    bgcolor=style_kwargs.get("bgcolor"),
                )
                segments.append(Segment(char, style))
            else:
                segments.append(Segment(char))

        return segments

    def render_line(self, y: int, widget_id: str, widget_size: Any, rendering_ready: bool) -> Strip:
        """Render a line using ATOMIC snapshot to prevent race conditions.

        IMPORTANT: This method uses a complete snapshot of the terminal state
        created by prepare_frame(). All line renders use this immutable snapshot,
        preventing race conditions where alternate screen switches happen between
        individual line renders.

        Args:
            y: The row index to render (0-based from top of widget)
            widget_id: Widget identifier for debug logging
            widget_size: Widget size for dimension checks
            rendering_ready: Whether the widget is ready for rendering

        Returns:
            A Strip containing the rendered line
        """
        # Get current state from callables
        terminal_cols = self._get_terminal_cols()
        terminal_rows = self._get_terminal_rows()
        scroll_offset = self._get_scroll_offset()
        selection_start = self._get_selection_start()
        selection_end = self._get_selection_end()
        cursor_blink_visible = self._get_cursor_blink_visible()

        # CRITICAL: Don't render before widget is fully initialized
        # This prevents corruption from rendering during startup before sizes are synced
        if not rendering_ready:
            if y == 0:
                debug_log("RENDER", "not ready - returning blank (widget not initialized)")
            return Strip.blank(widget_size.width if widget_size.width > 0 else 1)

        # Debug: Log render call with widget size info
        if y == 0:
            debug_log(
                "RENDER_SIZE",
                f"widget={widget_id} render_line called: y={y} widget.size={widget_size} "
                f"terminal_size=({terminal_cols}x{terminal_rows})",
            )

        # CRITICAL: Check if widget size matches terminal size
        # During Textual's startup, render_line can be called before on_mount/on_resize completes
        # If sizes don't match, return blank to avoid rendering with wrong buffer size
        if widget_size.width != terminal_cols or widget_size.height != terminal_rows:
            if y == 0:
                debug_log(
                    "SIZE_MISMATCH",
                    f"widget={widget_id} size mismatch: widget={widget_size.width}x{widget_size.height} "
                    f"terminal={terminal_cols}x{terminal_rows} - returning blank",
                )
            return Strip.blank(widget_size.width)

        # Log if we're being asked to render beyond terminal height
        if y >= terminal_rows:
            debug_log(
                "RENDER_OOB",
                f"widget={widget_id} render_line called for y={y} but terminal only has {terminal_rows} rows!",
            )
            return Strip.blank(widget_size.width)

        # Use the snapshot created in prepare_frame()
        # CRITICAL: Since Textual renders lines asynchronously and in arbitrary order,
        # we MUST NOT create snapshots during rendering. The snapshot is created
        # atomically in prepare_frame() to ensure all lines come from the same state.
        if self._frame_snapshot is None:
            # Emergency fallback - create snapshot if we don't have one
            # This shouldn't happen if prepare_frame() is working correctly
            self._frame_snapshot = self.term.create_snapshot()
            # Also pre-fetch lines for emergency case
            _term_cols_temp, term_rows_temp = self._frame_snapshot.size
            self._frame_lines = [self._frame_snapshot.get_line(y_temp) for y_temp in range(term_rows_temp)]
            # Clear hyperlink cache for emergency snapshot
            self._frame_hyperlink_cache.clear()
            debug_log(
                "SNAPSHOT",
                f"widget={widget_id} EMERGENCY snapshot on line {y}: gen={self._frame_snapshot.generation}",
            )

        snapshot = self._frame_snapshot

        # Log if PTY advanced during render (informational only)
        current_gen = self.term.update_generation()
        if y == 0 and current_gen != snapshot.generation:
            debug_log(
                "RENDER",
                f"PTY advanced during render: snapshot={snapshot.generation} current={current_gen}",
            )

        # Get terminal size from snapshot
        term_cols, term_rows = snapshot.size
        # If snapshot size doesn't match widget size, skip this frame and force refresh
        if (term_cols != terminal_cols) or (term_rows != terminal_rows):
            if y == 0:
                debug_log(
                    "SIZE_MISMATCH",
                    f"widget={widget_id} snapshot.size={term_cols}x{term_rows} "
                    f"!= terminal={terminal_cols}x{terminal_rows} - returning blank",
                )
            return Strip.blank(widget_size.width)

        # If row is out of bounds, return blank
        if y < 0 or y >= term_rows:
            debug_trace("RENDER", f"line {y} out of bounds (term_rows={term_rows})")
            return Strip.blank(widget_size.width)

        # Get cursor from snapshot
        cursor_col, cursor_row = snapshot.cursor_pos
        # Use the terminal's cursor visibility state
        # The terminal tracks cursor visibility via DECTCEM sequences (CSI ?25h/l)
        cursor_visible = snapshot.cursor_visible
        cursor_style = snapshot.cursor_style

        # Get line cells from SNAPSHOT or SCROLLBACK
        log_render_call(widget_id, y, snapshot.generation)

        # Determine if we should fetch from scrollback or live terminal
        if scroll_offset > 0:
            # We're scrolled up - need to fetch from scrollback
            scrollback_len = self.term.scrollback_len()
            # Calculate which line to fetch:
            # scrollback[scrollback_len-1] is most recent (just above live terminal)
            # scrollback[0] is oldest
            # When scroll_offset = N, we want to show scrollback lines starting from
            # scrollback[scrollback_len - N]
            scrollback_start_idx = scrollback_len - scroll_offset
            line_idx = scrollback_start_idx + y

            if line_idx < scrollback_len:
                # Fetch from scrollback
                scrollback_line = self.term.scrollback_line(line_idx)
                if scrollback_line is not None:
                    line_cells = scrollback_line
                else:
                    # Scrollback line doesn't exist (shouldn't happen), use blank
                    line_cells = []
            else:
                # Fetch from live terminal (we're showing some scrollback + some live)
                terminal_row = line_idx - scrollback_len
                # OPTIMIZATION: Use pre-fetched lines from _frame_lines
                if terminal_row < len(self._frame_lines):
                    line_cells = self._frame_lines[terminal_row]
                else:
                    # Out of bounds
                    line_cells = []
        # OPTIMIZATION: Not scrolled up - use pre-fetched line from _frame_lines
        # This avoids per-line cloning from Rust snapshot
        elif y < len(self._frame_lines):
            line_cells = self._frame_lines[y]
        else:
            # Fallback for edge cases
            line_cells = []

        # OPTIMIZATION: Check for corruption ONLY when debug is enabled
        # This eliminates overhead in production (string joins, pattern matching, etc.)
        if is_enabled(DebugLevel.DEBUG) and y < 5:  # Check top 5 lines where corruption typically appears
            raw_line = "".join(char for char, _, _, _ in line_cells if char)
            # Look for definitive corruption patterns
            definitive_patterns = [
                "\x1b",  # Literal escape character (should never be in cells)
                "○,○,○",  # Circle artifacts from handoff.md
                "CSI",  # Literal escape sequence names
            ]
            # Check for multiple semicolons + 'm' which suggests SGR fragments
            has_corruption = any(pattern in raw_line for pattern in definitive_patterns)

            if not has_corruption:
                # Check for SGR fragment patterns (multiple ; and m in first 20 chars)
                first_20 = raw_line[:20]
                if first_20.count(";") >= 2 and "m" in first_20:
                    has_corruption = True

            if has_corruption:
                # Log with hex representation for non-printable chars
                hex_line = " ".join(f"{ord(c):02x}" for c in raw_line[:40])
                debug_log(
                    "CORRUPTION",
                    f"line={y} raw={raw_line[:60]!r} hex=[{hex_line}]",
                )
                log_screen_corruption(widget_id, y, raw_line[:60])

        # Build segments with proper colors and attributes
        segments = []
        visual_width = 0  # Track actual visual width (accounting for wide chars)

        # Pre-compute cursor rendering flags for this line (optimization)
        # These flags only depend on row, not column, so compute once per line
        line_has_cursor = cursor_visible and scroll_offset == 0 and y == cursor_row
        cursor_as_reverse = False  # Block styles use reverse video
        cursor_as_underline = False  # Underline styles use underline
        cursor_as_bar = False  # Bar styles replace character with bar
        cursor_char = None  # Character to use for bar cursor

        if line_has_cursor:
            # Map cursor style to rendering technique (once per line)
            cursor_style_int = int(cursor_style)

            # Check if this is a blinking cursor style
            is_blinking_style = cursor_style_int in (
                int(CursorStyle.BlinkingBlock),
                int(CursorStyle.BlinkingUnderline),
                int(CursorStyle.BlinkingBar),
            )

            # Apply blink state if this is a blinking cursor and blinking is enabled
            if is_blinking_style and self.config.cursor_blink_enabled:
                # Use blink state to determine visibility
                line_has_cursor = cursor_blink_visible

            # Only compute cursor rendering flags if cursor is still visible after blink check
            if line_has_cursor:
                if cursor_style_int in (
                    int(CursorStyle.BlinkingBlock),
                    int(CursorStyle.SteadyBlock),
                ):
                    cursor_as_reverse = True
                elif cursor_style_int in (
                    int(CursorStyle.BlinkingUnderline),
                    int(CursorStyle.SteadyUnderline),
                ):
                    cursor_as_underline = True
                elif cursor_style_int in (
                    int(CursorStyle.BlinkingBar),
                    int(CursorStyle.SteadyBar),
                ):
                    cursor_as_bar = True
                    cursor_char = "▎"  # Use left bar character for bar cursor

        # OPTIMIZATION: Pre-compute selection column range for this row
        # This eliminates 1920+ function calls per frame (for 80x24 terminal)
        # by computing the range once per line instead of checking per cell
        selection_cols = None
        if selection_start and selection_end:
            start_col, start_row = selection_start
            end_col, end_row = selection_end

            # Normalize selection bounds (ensure start is before end)
            if start_row > end_row or (start_row == end_row and start_col > end_col):
                start_col, start_row, end_col, end_row = (
                    end_col,
                    end_row,
                    start_col,
                    start_row,
                )

            # Check if this row is within selection bounds
            if start_row <= y <= end_row:
                if y == start_row and y == end_row:
                    # Single line selection
                    selection_cols = range(start_col, end_col + 1)
                elif y == start_row:
                    # First line of multi-line selection
                    selection_cols = range(start_col, term_cols)
                elif y == end_row:
                    # Last line of multi-line selection
                    selection_cols = range(end_col + 1)
                else:
                    # Middle lines - all columns selected
                    selection_cols = range(term_cols)

        for col, (char, fg_rgb, bg_rgb, attrs) in enumerate(line_cells):
            # Track visual width BEFORE skipping spacers
            # Wide char spacers don't create segments, but they do occupy terminal columns
            if attrs and attrs.wide_char_spacer:
                # Spacer takes 1 column but creates no segment (it's part of the previous wide char)
                visual_width += 1
                continue

            # Track visual width for actual characters
            if attrs and attrs.wide_char:
                visual_width += 1  # Wide char creates 1 segment but we already counted the spacer
            else:
                visual_width += 1  # Normal char takes 1 column

            # Handle hidden attribute (conceal text)
            if attrs and attrs.hidden:
                char = " "  # Hide the character

            # NOTE: Control character filtering (< 32, except space/tab) is now done
            # in Rust (src/lib.rs PyScreenSnapshot::get_line()) for better performance

            # Create Rich style from terminal cell attributes
            style_kwargs = {}

            # Check if this is the cursor position (using pre-computed flags)
            is_cursor = line_has_cursor and col == cursor_col

            # Apply bar cursor character replacement if needed
            if is_cursor and cursor_as_bar and cursor_char is not None:
                char = cursor_char

            # OPTIMIZATION: Check if this cell is in the selection using pre-computed range
            # This replaces a function call with O(1) range membership check
            is_selected = selection_cols is not None and col in selection_cols

            # Check if reverse video is enabled (swap fg/bg)
            has_reverse = attrs and attrs.reverse
            is_reverse = (is_cursor and cursor_as_reverse) or has_reverse or is_selected

            if is_reverse:
                # Draw with reverse video (swap fg/bg)
                style_kwargs["color"] = _rgb_to_hex(*bg_rgb) if bg_rgb else (self._default_bg_color or "#000000")
                style_kwargs["bgcolor"] = (
                    _rgb_to_hex(*fg_rgb) if fg_rgb else "#ffffff"  # Default to white if no fg specified
                )
            else:
                # Normal cell rendering
                if fg_rgb:
                    # Always honor explicit black (0,0,0). Treat absence only as default.
                    style_kwargs["color"] = _rgb_to_hex(*fg_rgb)

                # Check if cell has explicit background color
                # Treat (0,0,0) as "use default" unless theme is actually black
                if bg_rgb and (bg_rgb != (0, 0, 0) or not self._default_bg_color):
                    style_kwargs["bgcolor"] = _rgb_to_hex(*bg_rgb)
                elif self._default_bg_color:
                    # Use theme's default background when cell has no explicit background
                    # or when cell has (0,0,0) and theme has a different background
                    style_kwargs["bgcolor"] = self._default_bg_color

            if attrs:
                if attrs.bold:
                    style_kwargs["bold"] = True
                if attrs.italic:
                    style_kwargs["italic"] = True
                if attrs.underline:
                    style_kwargs["underline"] = True
                if attrs.dim:
                    style_kwargs["dim"] = True
                if attrs.blink:
                    style_kwargs["blink"] = True
                if attrs.strikethrough:
                    style_kwargs["strike"] = True

            # Apply cursor underline style if needed
            if is_cursor and cursor_as_underline:
                style_kwargs["underline"] = True
                # Also apply reverse video to make the underline cursor more visible
                if not is_reverse:
                    is_reverse = True
                    # Re-apply reverse colors for underline cursor
                    style_kwargs["color"] = _rgb_to_hex(*bg_rgb) if bg_rgb else (self._default_bg_color or "#000000")
                    style_kwargs["bgcolor"] = _rgb_to_hex(*fg_rgb) if fg_rgb else "#ffffff"

            # Apply bar cursor styling if needed
            if is_cursor and cursor_as_bar:
                # Bar cursor also uses reverse video for visibility
                if not is_reverse:
                    is_reverse = True
                    style_kwargs["color"] = _rgb_to_hex(*bg_rgb) if bg_rgb else (self._default_bg_color or "#000000")
                    style_kwargs["bgcolor"] = _rgb_to_hex(*fg_rgb) if fg_rgb else "#ffffff"

            # OPTIMIZATION: Check for hyperlink and apply styling
            # Uses shared frame-level cache to avoid dict allocations per line
            if attrs and attrs.hyperlink_id is not None:
                # Get URL from shared cache or fetch it from terminal
                if attrs.hyperlink_id not in self._frame_hyperlink_cache:
                    # Use terminal.get_hyperlink() not snapshot.get_hyperlink()
                    url = self.term.get_hyperlink(col, y)
                    self._frame_hyperlink_cache[attrs.hyperlink_id] = url
                else:
                    url = self._frame_hyperlink_cache[attrs.hyperlink_id]

                # Apply link color styling if clickable URLs are enabled
                # Only apply if we have a valid URL
                if url and self.config.clickable_urls and not is_reverse:
                    # Override foreground color with link color
                    r, g, b = self.config.link_color
                    style_kwargs["color"] = _rgb_to_hex(r, g, b)
                    # Add underline to make links more visible
                    style_kwargs["underline"] = True

            # Create the segment (ensure char is never None)
            char_text = char if char is not None else " "
            if style_kwargs:
                # Use cached style creation for better performance
                style = _create_style(
                    color=style_kwargs.get("color"),
                    bgcolor=style_kwargs.get("bgcolor"),
                    bold=style_kwargs.get("bold", False),
                    italic=style_kwargs.get("italic", False),
                    underline=style_kwargs.get("underline", False),
                    dim=style_kwargs.get("dim", False),
                    blink=style_kwargs.get("blink", False),
                    strike=style_kwargs.get("strike", False),
                )
                segments.append(Segment(char_text, style))
            else:
                segments.append(Segment(char_text))

        # NOTE: Control character filtering debug logging removed - filtering now done in Rust

        # Log rendered content at trace level (after filtering)
        line_text = "".join(seg.text for seg in segments)
        log_render_content(widget_id, y, line_text)

        # Render Sixel graphics overlaid on text
        # Graphics are rendered using Unicode half-blocks for 2:1 vertical compression
        graphics_at_row = self.term.graphics_at_row(y)
        if graphics_at_row:
            for graphic in graphics_at_row:
                gfx_segments = self._render_graphic_line(graphic, y, term_cols)
                if gfx_segments:
                    gfx_col, _ = graphic.position
                    # Overlay graphic segments onto text segments at the graphic's column position
                    # Ensure we don't go out of bounds
                    for i, gfx_seg in enumerate(gfx_segments):
                        col_idx = gfx_col + i
                        if col_idx < len(segments):
                            segments[col_idx] = gfx_seg
                        elif col_idx < term_cols:
                            # Extend segments list if needed
                            while len(segments) <= col_idx:
                                segments.append(Segment(" "))
                            segments[col_idx] = gfx_seg

        # Ensure strip is exactly the right width by padding if needed
        # Use visual_width which accounts for wide characters taking 2 columns
        if visual_width < term_cols:
            # Pad with spaces to fill the line
            padding_needed = term_cols - visual_width
            segments.append(Segment(" " * padding_needed))
        elif visual_width > term_cols:
            # This shouldn't happen, but log it if it does
            debug_log(
                "WIDTH_ERROR",
                f"widget={widget_id} line={y} visual_width={visual_width} > term_cols={term_cols}",
            )

        # Return Strip with correct width
        return Strip(segments)
