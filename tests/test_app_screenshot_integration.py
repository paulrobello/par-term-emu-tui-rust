"""Tests for TerminalApp screenshot integration with ScreenshotManager."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from par_term_emu_tui_rust.app import TerminalApp
from par_term_emu_tui_rust.config import TuiConfig

if TYPE_CHECKING:
    import pytest


class _DummyTerminalWidget:
    """Minimal stand-in for TerminalWidget for _take_screenshot tests."""

    def __init__(self, scroll_y: int = 0) -> None:
        self.term = object()

        class _Offset:
            def __init__(self, y: int) -> None:
                self.y = y

        self.scroll_offset = _Offset(scroll_y)


def test_app_take_screenshot_uses_screenshot_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """_take_screenshot should delegate to ScreenshotManager and update screenshot_path."""
    cfg = TuiConfig()
    cfg.open_screenshot_after_capture = False

    app = TerminalApp(shell_command=None, shell_path=None, config=cfg)
    app.open_screenshot = False

    dummy_widget = _DummyTerminalWidget(scroll_y=5)

    # Ensure TerminalApp.query_one(TerminalWidget) returns our dummy widget
    monkeypatch.setattr(app, "query_one", lambda *_args, **_kwargs: dummy_widget)

    called: dict[str, object] = {}

    class FakeScreenshotManager:
        def __init__(self, term, config, get_scroll_offset) -> None:  # noqa: ANN001
            called["term"] = term
            called["config"] = config
            # Capture scroll offset immediately to verify wiring
            called["scroll_offset"] = get_scroll_offset()

        def save(self) -> tuple[str, str | None]:
            path = tmp_path / "terminal_screenshot_20250101_000000.png"
            path.write_text("dummy", encoding="utf-8")
            return str(path), None

    # Patch ScreenshotManager used inside app._take_screenshot
    monkeypatch.setattr(
        "par_term_emu_tui_rust.app.ScreenshotManager",
        FakeScreenshotManager,
    )

    app._take_screenshot()

    # Ensure ScreenshotManager received the correct arguments
    assert called["config"] is cfg
    assert called["term"] is dummy_widget.term
    assert called["scroll_offset"] == 5

    # Ensure TerminalApp recorded the screenshot path
    assert isinstance(app.screenshot_path, Path)
    assert app.screenshot_path.name == "terminal_screenshot_20250101_000000.png"


def test_app_take_screenshot_handles_save_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """_take_screenshot should handle ScreenshotManager.save errors gracefully."""
    cfg = TuiConfig()
    cfg.open_screenshot_after_capture = False

    app = TerminalApp(shell_command=None, shell_path=None, config=cfg)
    app.open_screenshot = False

    dummy_widget = _DummyTerminalWidget(scroll_y=0)
    monkeypatch.setattr(app, "query_one", lambda *_args, **_kwargs: dummy_widget)

    class FailingScreenshotManager:
        def __init__(self, term, config, get_scroll_offset) -> None:  # noqa: ANN001
            # Ensure we can still call get_scroll_offset without issue
            _ = (term, config, get_scroll_offset())

        def save(self) -> tuple[str | None, str | None]:
            return None, "simulated error"

    monkeypatch.setattr(
        "par_term_emu_tui_rust.app.ScreenshotManager",
        FailingScreenshotManager,
    )

    # Should not raise even though save() "fails"
    app._take_screenshot()

    # screenshot_path should remain None when save() fails
    assert app.screenshot_path is None
