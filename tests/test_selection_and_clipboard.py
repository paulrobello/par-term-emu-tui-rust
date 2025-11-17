"""Tests for SelectionManager and ClipboardManager using test doubles."""

from __future__ import annotations

import pytest

from par_term_emu_tui_rust.config import TuiConfig
from par_term_emu_tui_rust.terminal_widget.clipboard import ClipboardManager
from par_term_emu_tui_rust.terminal_widget.selection import SelectionManager


class _SelectionTestTerminal:
    """Test double for PtyTerminal focusing on get_char/get_word_at/create_snapshot."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    def get_char(self, col: int, row: int) -> str:
        if 0 <= row < len(self._lines) and 0 <= col < len(self._lines[row]):
            return self._lines[row][col]
        return ""

    def get_word_at(self, col: int, row: int, word_chars: str) -> str:
        """Return word at given position based on simple whitespace splitting."""
        if row < 0 or row >= len(self._lines):
            return ""
        line = self._lines[row]
        if not (0 <= col < len(line)):
            return ""
        # Find start of word
        start = col
        while start > 0 and not line[start - 1].isspace():
            start -= 1
        end = col
        while end < len(line) and not line[end].isspace():
            end += 1
        return line[start:end]

    def create_snapshot(self) -> object:
        """Return snapshot with size, get_line, and wrapped_lines attributes."""

        class Snapshot:
            def __init__(self, lines: list[str]) -> None:
                self._lines = lines
                cols = max((len(line) for line in lines), default=0)
                self.size = (max(cols, 1), len(lines) or 1)
                self.wrapped_lines = [False] * self.size[1]

            def get_line(self, row: int) -> list[tuple[str, None, None, None]]:
                if not (0 <= row < len(self._lines)):
                    return []
                line = self._lines[row]
                return [(ch, None, None, None) for ch in line]

        return Snapshot(self._lines)


def test_selection_manager_get_selected_text_single_line() -> None:
    """SelectionManager should extract the right substring for a single line."""
    term = _SelectionTestTerminal(["hello world"])

    cfg = TuiConfig()
    cfg.copy_trailing_newline = False

    manager = SelectionManager(term=term, config=cfg, get_terminal_cols=lambda: 20)
    manager.start = (0, 0)
    manager.end = (4, 0)  # 'hello'

    text = manager.get_selected_text()
    assert text == "hello"


def test_selection_manager_get_selected_text_multi_line_with_trailing_newline() -> None:
    """Multi-line selection should join lines with \\n and honor copy_trailing_newline."""
    term = _SelectionTestTerminal(["first line", "second line"])

    cfg = TuiConfig()
    cfg.copy_trailing_newline = True

    manager = SelectionManager(term=term, config=cfg, get_terminal_cols=lambda: 20)
    # Select from "first" (col 0 row 0) through "second" line partially
    manager.start = (0, 0)
    manager.end = (4, 1)  # 'secon' (columns 0-4 inclusive = 5 chars)

    text = manager.get_selected_text()
    # first line\nsecon\n (no trailing spaces due to rstrip)
    assert text == "first line\nsecon\n"


def test_selection_manager_select_word_at_uses_get_word_at() -> None:
    """select_word_at should set selection bounds for the detected word."""
    term = _SelectionTestTerminal(["foo bar baz"])

    cfg = TuiConfig()
    cfg.word_characters = "/-+\\_."  # not used by this simple test double

    manager = SelectionManager(term=term, config=cfg, get_terminal_cols=lambda: 20)
    snapshot = term.create_snapshot()

    # Click somewhere in 'bar'
    manager.select_word_at(col=5, row=0, frame_snapshot=snapshot)
    assert manager.start == (4, 0)
    assert manager.end == (6, 0)


class _ClipboardTestTerminal:
    """Test double that records pasted content for verification."""

    def __init__(self) -> None:
        self.pasted: list[str] = []

    def paste(self, content: str) -> None:
        self.pasted.append(content)


@pytest.mark.asyncio
async def test_clipboard_manager_paste_chunking(monkeypatch: pytest.MonkeyPatch) -> None:
    """ClipboardManager should chunk large pastes when configured to do so."""
    term = _ClipboardTestTerminal()
    cfg = TuiConfig()
    cfg.paste_chunk_size = 4
    cfg.paste_chunk_delay_ms = 0
    cfg.paste_warn_size = 1  # force warning even for very small content

    manager = ClipboardManager(term=term, config=cfg)

    # Stub pyperclip.paste to return deterministic text without requiring pyperclip to be installed
    import sys as _sys

    fake_pyperclip = type("M", (), {"paste": staticmethod(lambda: "abcdefgh")})
    monkeypatch.setitem(_sys.modules, "pyperclip", fake_pyperclip)

    success, message = await manager.paste_from_clipboard()

    assert success is True
    # 8 characters, chunk size 4 -> 2 chunks
    assert term.pasted == ["abcd", "efgh"]
    # Warning message should be present due to low paste_warn_size
    assert "Pasting large content" in (message or "")
