"""Text selection logic for terminal widget."""

from typing import TYPE_CHECKING, Any

from par_term_emu_core_rust.debug import debug_log

if TYPE_CHECKING:
    from collections.abc import Callable

    from par_term_emu_core_rust import PtyTerminal

    from par_term_emu_tui_rust.config import TuiConfig


class SelectionManager:
    """Manages text selection in the terminal widget."""

    def __init__(
        self,
        term: PtyTerminal,
        config: TuiConfig,
        get_terminal_cols: Callable[[], int],
    ) -> None:
        """Initialize selection manager.

        Args:
            term: Terminal instance
            config: TUI configuration
            get_terminal_cols: Callable that returns current terminal columns
        """
        self.term = term
        self.config = config
        self.get_terminal_cols = get_terminal_cols

        # Selection state
        self.start: tuple[int, int] | None = None  # (col, row) or None
        self.end: tuple[int, int] | None = None  # (col, row) or None
        self.selecting = False  # True when mouse drag in progress

    def clear(self) -> None:
        """Clear the current selection."""
        self.start = None
        self.end = None
        self.selecting = False

    def select_word_at(self, col: int, row: int, frame_snapshot: Any) -> None:
        """Select the word at the given position.

        Uses the native terminal's word detection via get_word_at(), which respects
        the configured word character boundaries.

        Args:
            col: Column position
            row: Row position
            frame_snapshot: Terminal snapshot to get line content for finding word bounds
        """
        try:
            # Use native terminal word detection to get the word text
            word_text = self.term.get_word_at(col, row, self.config.word_characters)
            if not word_text:
                debug_log("SELECT", f"No word found at ({col},{row})")
                return

            # Ensure we have a snapshot to find word boundaries
            if not frame_snapshot:
                frame_snapshot = self.term.create_snapshot()

            # Get the line content
            line_cells = frame_snapshot.get_line(row)
            if not line_cells:
                return

            # Extract just the characters from the line
            line_text = "".join(char for char, _, _, _ in line_cells)

            # Find the word boundaries by searching for the word in the line
            # Start from the clicked column and search backwards/forwards
            word_start = line_text.find(word_text, max(0, col - len(word_text)))
            if word_start == -1:
                # Fallback: search from beginning of line
                word_start = line_text.find(word_text)
            if word_start == -1:
                debug_log("SELECT", f"Could not find word '{word_text}' in line")
                return

            word_end = word_start + len(word_text) - 1

            debug_log(
                "SELECT",
                f"Selected word '{word_text}' at ({col},{row}): cols {word_start}-{word_end}",
            )

            # Set selection bounds
            self.start = (word_start, row)
            self.end = (word_end, row)

        except Exception as e:
            debug_log("SELECT", f"Error in select_word_at({col},{row}): {e}")
            # Fall back to clearing selection on error
            return

    def select_line_at(self, row: int, frame_snapshot: Any) -> None:
        """Select the entire line at the given row.

        Respects config.triple_click_selects_wrapped_lines setting (default: True).
        When enabled, follows line wrapping to select the complete logical line.

        Args:
            row: Row position
            frame_snapshot: Terminal snapshot to use for selection
        """
        # Ensure we have a snapshot - create one if needed
        if not frame_snapshot:
            frame_snapshot = self.term.create_snapshot()
            debug_log("SELECT", f"Created snapshot for line selection at row {row}")

        cols, rows = frame_snapshot.size

        # Determine start and end rows based on config
        if self.config.triple_click_selects_wrapped_lines:
            # Follow wrapped lines backwards to find the real start
            start_row = row
            while start_row > 0:
                # Check if the previous line wraps to this line
                prev_row = start_row - 1
                if prev_row < len(frame_snapshot.wrapped_lines):
                    if frame_snapshot.wrapped_lines[prev_row]:
                        start_row = prev_row
                        debug_log(
                            "SELECT",
                            f"Line {prev_row} wraps, extending selection backwards",
                        )
                    else:
                        break  # Previous line doesn't wrap, we found the start
                else:
                    break

            # Follow wrapped lines forwards to find the real end
            end_row = row
            while end_row < rows - 1:
                # Check if this line wraps to the next line
                if end_row < len(frame_snapshot.wrapped_lines):
                    if frame_snapshot.wrapped_lines[end_row]:
                        end_row += 1
                        debug_log(
                            "SELECT",
                            f"Line {end_row - 1} wraps, extending selection forwards",
                        )
                    else:
                        break  # This line doesn't wrap, we found the end
                else:
                    break

            debug_log(
                "SELECT",
                f"Wrapped line selection: rows {start_row}-{end_row} (clicked {row})",
            )
        else:
            # Just select the single visible line
            start_row = row
            end_row = row
            debug_log("SELECT", f"Single line selection at row {row}")

        # Select from beginning of start row to end of end row
        self.start = (0, start_row)
        self.end = (cols - 1, end_row)

    def is_cell_selected(self, col: int, row: int) -> bool:
        """Check if a cell is within the current selection.

        Args:
            col: Column position
            row: Row position

        Returns:
            True if cell is selected, False otherwise
        """
        if not self.start or not self.end:
            return False

        # Normalize selection bounds
        start_col, start_row = self.start
        end_col, end_row = self.end

        # Ensure start is before end
        if start_row > end_row or (start_row == end_row and start_col > end_col):
            start_col, start_row, end_col, end_row = (
                end_col,
                end_row,
                start_col,
                start_row,
            )

        # Check if cell is within selection bounds
        if row < start_row or row > end_row:
            return False

        if row == start_row and row == end_row:
            # Single line selection
            return start_col <= col <= end_col
        if row == start_row:
            # First line of multi-line selection
            return col >= start_col
        if row == end_row:
            # Last line of multi-line selection
            return col <= end_col
        # Middle lines
        return True

    def get_selected_text(self) -> str:
        """Extract text from terminal between selection points.

        Respects config.copy_trailing_newline setting (default: True).
        When True, adds a trailing newline to the copied text.

        Returns:
            Selected text as string, empty if no selection
        """
        if not self.start or not self.end:
            return ""

        # Normalize selection bounds (top-left to bottom-right)
        start_col, start_row = self.start
        end_col, end_row = self.end

        # Ensure start is before end
        if start_row > end_row or (start_row == end_row and start_col > end_col):
            start_col, start_row, end_col, end_row = (
                end_col,
                end_row,
                start_col,
                start_row,
            )

        terminal_cols = self.get_terminal_cols()
        lines = []
        for row in range(start_row, end_row + 1):
            line_text = ""
            # Determine column range for this row
            if row == start_row and row == end_row:
                # Single line selection
                col_start, col_end = start_col, end_col
            elif row == start_row:
                # First line of multi-line selection
                col_start, col_end = start_col, terminal_cols - 1
            elif row == end_row:
                # Last line of multi-line selection
                col_start, col_end = 0, end_col
            else:
                # Middle lines
                col_start, col_end = 0, terminal_cols - 1

            # Extract characters from this row
            for col in range(col_start, col_end + 1):
                char = self.term.get_char(col, row)
                if char:
                    line_text += char
                else:
                    line_text += " "

            # Remove trailing spaces
            line_text = line_text.rstrip()
            lines.append(line_text)

        result = "\n".join(lines)

        # Add trailing newline if configured (default: True, like iTerm2)
        if self.config.copy_trailing_newline and result:
            result += "\n"

        return result
