"""
Pytest configuration and shared fixtures.

This file:
- Provides a lightweight stub for the `par_term_emu_core_rust` module so tests
  can import `par_term_emu_tui_rust.app` and related modules without requiring
  the Rust core library to be installed.
- Redirects XDG config home to a per-test temporary directory so config-related
  tests don't touch real user configuration.
"""

from __future__ import annotations

import sys
import types
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


def _install_par_term_core_stub() -> None:
    """Install a stub implementation of `par_term_emu_core_rust` into sys.modules.

    The application imports:
    - `par_term_emu_core_rust.CursorStyle`
    - `par_term_emu_core_rust.PtyTerminal`
    - `par_term_emu_core_rust.debug.*`

    For the CLI-oriented tests in this suite, we don't construct a real
    `PtyTerminal` or use the debug functions, so a minimal stub is sufficient.
    """
    if "par_term_emu_core_rust" in sys.modules:
        # Assume a real or stub implementation is already present
        return

    core = types.ModuleType("par_term_emu_core_rust")

    class DummyPtyTerminal:
        """Minimal stand-in for PtyTerminal used in non-interactive tests.

        For unit tests that need richer behavior (for example, selection or
        screenshot tests), a more capable test double is constructed directly
        in the test module instead of relying on this stub.
        """

        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            self._buffer: dict[tuple[int, int], str] = {}
            self._notification_config = None
            self._max_notifications = 0
            self._max_clipboard_sync_events = 0
            self._max_clipboard_event_bytes = 0
            self._activity_updates = 0
            self._shell_stats = None

        # SelectionManager expects these on the terminal
        def get_word_at(self, col: int, row: int, word_chars: str) -> str:
            return ""

        def create_snapshot(self) -> object:
            """Return a trivial snapshot with size, get_line, and wrapped_lines."""

            class Snapshot:
                def __init__(self, buffer: dict[tuple[int, int], str]) -> None:
                    self._buffer = buffer
                    # Minimal size; tests that need specific sizes should use their own doubles
                    self.size = (80, 24)
                    self.wrapped_lines: list[bool] = [False] * self.size[1]

                def get_line(self, row: int) -> list[tuple[str, None, None, None]]:
                    return [(self._buffer.get((col, row), " "), None, None, None) for col in range(self.size[0])]

            return Snapshot(self._buffer)

        def get_char(self, col: int, row: int) -> str:
            return self._buffer.get((col, row), "")

        # ClipboardManager expects this on the terminal
        def paste(self, content: str) -> None:
            """Consume pasted content (no-op in stub)."""
            _ = content

        # Notification / clipboard helpers invoked by backend_controls
        def set_notification_config(self, config) -> None:  # noqa: ANN001 - matches native signature
            self._notification_config = config

        def set_max_notifications(self, count: int) -> None:
            self._max_notifications = count

        def set_max_clipboard_sync_events(self, count: int) -> None:
            self._max_clipboard_sync_events = count

        def set_max_clipboard_event_bytes(self, size: int) -> None:
            self._max_clipboard_event_bytes = size

        def update_activity(self) -> None:
            self._activity_updates += 1

        def check_silence(self) -> None:
            return

        def check_activity(self) -> None:
            return

        def get_shell_integration_stats(self) -> None:
            return self._shell_stats

    class DummyCursorStyle:
        """Simple container for cursor style constants used in comparisons."""

        BlinkingBlock = 1
        SteadyBlock = 2
        BlinkingUnderline = 3
        SteadyUnderline = 4
        BlinkingBar = 5
        SteadyBar = 6

    core.PtyTerminal = DummyPtyTerminal  # type: ignore[attr-defined]
    core.CursorStyle = DummyCursorStyle  # type: ignore[attr-defined]

    class NotificationConfig:
        def __init__(self) -> None:
            self.bell_desktop = False
            self.bell_sound = 0
            self.bell_visual = True
            self.activity_enabled = False
            self.activity_threshold = 10
            self.silence_enabled = False
            self.silence_threshold = 300

    core.NotificationConfig = NotificationConfig  # type: ignore[attr-defined]

    # Add stub for adjust_contrast_rgb used by rendering.py
    def adjust_contrast_rgb(
        fg_r: int,
        fg_g: int,
        fg_b: int,
        bg_r: int,  # noqa: ARG001
        bg_g: int,  # noqa: ARG001
        bg_b: int,  # noqa: ARG001
        min_contrast: float,  # noqa: ARG001
    ) -> tuple[int, int, int]:
        """Stub for adjust_contrast_rgb - returns input color unchanged."""
        return (fg_r, fg_g, fg_b)

    core.adjust_contrast_rgb = adjust_contrast_rgb  # type: ignore[attr-defined]

    debug = types.ModuleType("par_term_emu_core_rust.debug")

    def _noop(*_args, **_kwargs) -> None:  # noqa: ANN002, ANN003
        return

    # Debug API surface used by the TUI code
    debug.debug_log = _noop  # type: ignore[attr-defined]
    debug.debug_trace = _noop  # type: ignore[attr-defined]
    debug.log_generation_check = _noop  # type: ignore[attr-defined]
    debug.log_widget_lifecycle = _noop  # type: ignore[attr-defined]
    debug.log_render_call = _noop  # type: ignore[attr-defined]
    debug.log_render_content = _noop  # type: ignore[attr-defined]
    debug.log_screen_corruption = _noop  # type: ignore[attr-defined]

    class DebugLevel:
        """Placeholder for DebugLevel enum used in type hints."""

        INFO = 1
        TRACE = 2

    debug.DebugLevel = DebugLevel  # type: ignore[attr-defined]
    debug.is_enabled = lambda *_args, **_kwargs: False  # type: ignore[attr-defined]

    sys.modules["par_term_emu_core_rust"] = core
    sys.modules["par_term_emu_core_rust.debug"] = debug


_install_par_term_core_stub()


@pytest.fixture(autouse=True)
def xdg_config_home_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect XDG config home to a per-test temporary directory.

    This ensures that tests which exercise TuiConfig and CLI helpers that touch
    the config file do not read or modify the user's real configuration.
    """
    xdg_dir = tmp_path / "xdg-config"
    xdg_dir.mkdir(exist_ok=True)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_dir))
