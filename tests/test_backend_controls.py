"""Tests for backend helper functions that bridge TUI config to the Rust core."""

from __future__ import annotations

from par_term_emu_tui_rust.config import TuiConfig
from par_term_emu_tui_rust.terminal_widget.backend_controls import (
    apply_clipboard_limits,
    apply_notification_settings,
    get_shell_stats_summary,
)


class _FakeTerm:
    def __init__(self) -> None:
        self.notification_config = None
        self.max_notifications = None
        self.clipboard_events = None
        self.clipboard_bytes = None
        self.shell_stats = type(
            "Stats",
            (),
            {
                "total_commands": 12,
                "failed_commands": 2,
                "avg_duration_ms": 45.5,
            },
        )()

    def set_notification_config(self, config) -> None:  # noqa: ANN001 - dynamic from stub
        self.notification_config = config

    def set_max_notifications(self, max_entries: int) -> None:
        self.max_notifications = max_entries

    def set_max_clipboard_sync_events(self, count: int) -> None:
        self.clipboard_events = count

    def set_max_clipboard_event_bytes(self, size: int) -> None:
        self.clipboard_bytes = size

    def get_shell_integration_stats(self) -> object:
        return self.shell_stats


def test_apply_notification_settings_populates_backend() -> None:
    cfg = TuiConfig()
    cfg.notification_bell_desktop = True
    cfg.notification_bell_sound = 42
    cfg.notification_bell_visual = False
    cfg.notification_activity_enabled = True
    cfg.notification_activity_threshold = 15
    cfg.notification_silence_enabled = True
    cfg.notification_silence_threshold = 600
    cfg.notification_max_buffer = 99

    term = _FakeTerm()
    apply_notification_settings(term, cfg)

    assert term.max_notifications == 99
    assert term.notification_config is not None
    assert term.notification_config.bell_desktop is True
    assert term.notification_config.bell_sound == 42
    assert term.notification_config.bell_visual is False
    assert term.notification_config.activity_enabled is True
    assert term.notification_config.activity_threshold == 15
    assert term.notification_config.silence_enabled is True
    assert term.notification_config.silence_threshold == 600


def test_apply_clipboard_limits_sets_caps() -> None:
    cfg = TuiConfig()
    cfg.clipboard_max_sync_events = 10
    cfg.clipboard_max_event_bytes = 128

    term = _FakeTerm()
    apply_clipboard_limits(term, cfg)

    assert term.clipboard_events == 10
    assert term.clipboard_bytes == 128


def test_get_shell_stats_summary_formats_counts() -> None:
    summary = get_shell_stats_summary(_FakeTerm())
    assert summary == "cmds 12 | 2 fail | avg 46ms"
