"""Helpers for bridging TUI configuration to backend runtime options."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from par_term_emu_tui_rust.config import TuiConfig

try:  # pragma: no cover - exercised when the native core is present
    from par_term_emu_core_rust import NotificationConfig as CoreNotificationConfig  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - fallback for tests without the core
    CoreNotificationConfig = None  # type: ignore[assignment]


def _safe_call(method_name: str, term: Any, *args: Any, **kwargs: Any) -> None:
    """Invoke a backend method if it exists, ignoring missing attributes."""

    method = getattr(term, method_name, None)
    if callable(method):  # pragma: no branch - simple guard
        method(*args, **kwargs)


def apply_notification_settings(term: Any, config: TuiConfig) -> None:
    """Configure notification preferences and buffer limits on the backend."""

    notification_obj = None
    if CoreNotificationConfig is not None:
        notification_obj = CoreNotificationConfig()  # type: ignore[call-arg]
        notification_obj.bell_desktop = config.notification_bell_desktop
        notification_obj.bell_sound = int(max(0, min(100, config.notification_bell_sound)))
        notification_obj.bell_visual = config.notification_bell_visual
        notification_obj.activity_enabled = config.notification_activity_enabled
        notification_obj.activity_threshold = max(0, config.notification_activity_threshold)
        notification_obj.silence_enabled = config.notification_silence_enabled
        notification_obj.silence_threshold = max(0, config.notification_silence_threshold)

    if notification_obj is not None:
        _safe_call("set_notification_config", term, notification_obj)

    _safe_call("set_max_notifications", term, max(0, config.notification_max_buffer))


def apply_clipboard_limits(term: Any, config: TuiConfig) -> None:
    """Apply clipboard event buffer limits introduced in core 0.7.0."""

    _safe_call("set_max_clipboard_sync_events", term, max(0, config.clipboard_max_sync_events))
    _safe_call("set_max_clipboard_event_bytes", term, max(0, config.clipboard_max_event_bytes))


def mark_terminal_activity(term: Any) -> None:
    """Forward a user activity signal so silence/activity detectors reset."""

    _safe_call("update_activity", term)


def run_activity_checks(term: Any, config: TuiConfig) -> None:
    """Ask the backend to evaluate silence/activity triggers when enabled."""

    if config.notification_silence_enabled:
        _safe_call("check_silence", term)
    if config.notification_activity_enabled:
        _safe_call("check_activity", term)


def get_shell_stats_summary(term: Any) -> str | None:
    """Return a compact textual summary of shell integration statistics."""

    get_stats = getattr(term, "get_shell_integration_stats", None)
    if not callable(get_stats):
        return None
    try:
        stats = get_stats()
    except Exception:  # pragma: no cover - backend failure logged elsewhere
        return None
    if stats is None:
        return None

    total = getattr(stats, "total_commands", 0)
    failed = getattr(stats, "failed_commands", 0)
    avg_ms = getattr(stats, "avg_duration_ms", 0.0)

    if not total:
        return None

    parts = [f"cmds {total}"]
    if failed:
        parts.append(f"{failed} fail")
    avg_display = round(avg_ms)
    if avg_display:
        parts.append(f"avg {avg_display}ms")
    return " | ".join(parts)
