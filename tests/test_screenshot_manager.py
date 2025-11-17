"""Tests for ScreenshotManager directory selection and path formatting."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from par_term_emu_tui_rust.config import TuiConfig
from par_term_emu_tui_rust.terminal_widget.screenshot import ScreenshotManager

if TYPE_CHECKING:
    import pytest


class _DummyTermNoShellState:
    """Dummy terminal that does not provide shell integration state."""

    def shell_integration_state(self) -> None:
        """Raise to simulate lack of shell integration."""
        msg = "shell integration not available"
        raise RuntimeError(msg)


class _DummyTermWithShellState:
    """Dummy terminal that returns a shell integration state with a CWD."""

    def __init__(self, cwd: Path) -> None:
        self._cwd = cwd

    def shell_integration_state(self) -> object:
        """Return an object with a cwd attribute."""
        return type("ShellState", (), {"cwd": str(self._cwd)})()


def _make_manager(term: object, cfg: TuiConfig) -> ScreenshotManager:
    """Helper to create a ScreenshotManager with a trivial scroll offset callable."""
    return ScreenshotManager(term=term, config=cfg, get_scroll_offset=lambda: 0)


def test_get_directory_uses_existing_config_directory(tmp_path: Path) -> None:
    """If screenshot_directory exists, get_directory should return it."""
    cfg = TuiConfig()
    screenshot_dir = tmp_path / "shots"
    screenshot_dir.mkdir()
    cfg.screenshot_directory = str(screenshot_dir)

    mgr = _make_manager(_DummyTermNoShellState(), cfg)
    result = Path(mgr.get_directory())

    assert result == screenshot_dir
    assert screenshot_dir.is_dir()


def test_get_directory_creates_missing_config_directory(tmp_path: Path) -> None:
    """If screenshot_directory does not exist, get_directory should create it."""
    cfg = TuiConfig()
    screenshot_dir = tmp_path / "shots-new"
    cfg.screenshot_directory = str(screenshot_dir)

    mgr = _make_manager(_DummyTermNoShellState(), cfg)
    result = Path(mgr.get_directory())

    assert result == screenshot_dir
    assert screenshot_dir.is_dir()


def test_get_directory_uses_shell_cwd_when_config_not_set(tmp_path: Path) -> None:
    """When no config directory is set, shell CWD from OSC 7 should be used."""
    cfg = TuiConfig()
    cfg.screenshot_directory = None

    shell_dir = tmp_path / "shell-cwd"
    shell_dir.mkdir()

    mgr = _make_manager(_DummyTermWithShellState(shell_dir), cfg)
    result = mgr.get_directory()

    assert result == str(shell_dir)


def test_get_directory_uses_xdg_pictures_when_shell_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When config and shell CWD are unavailable, use XDG_PICTURES_DIR/Screenshots."""
    cfg = TuiConfig()
    cfg.screenshot_directory = None

    xdg_pictures = tmp_path / "pictures-root"
    monkeypatch.setenv("XDG_PICTURES_DIR", str(xdg_pictures))

    mgr = _make_manager(_DummyTermNoShellState(), cfg)
    result = Path(mgr.get_directory())

    expected = xdg_pictures.expanduser() / "Screenshots"
    assert result == expected
    assert expected.is_dir()


def test_format_path_for_display_relative_and_absolute(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """format_path_for_display should return relative paths inside CWD and absolute otherwise."""
    cwd = tmp_path / "project"
    cwd.mkdir()
    monkeypatch.chdir(cwd)

    inside_dir = cwd / "subdir"
    inside_dir.mkdir()
    inside_file = inside_dir / "file.txt"
    inside_file.write_text("test", encoding="utf-8")

    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    outside_file = outside_dir / "other.txt"
    outside_file.write_text("test", encoding="utf-8")

    rel = ScreenshotManager.format_path_for_display(str(inside_file))
    abs_path = ScreenshotManager.format_path_for_display(str(outside_file))

    # Inside CWD should be reported relative
    assert rel == str(inside_file.relative_to(cwd))
    # Outside CWD should remain absolute
    assert abs_path == str(outside_file)
