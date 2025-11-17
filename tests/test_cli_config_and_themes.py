"""CLI-oriented tests for config and theme commands.

These tests exercise the argument-handling paths in `app.main` that execute
and return before the Textual TUI is started. They rely on the stub
`par_term_emu_core_rust` module installed by `tests/conftest.py` to avoid
requiring the Rust core library during testing.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from par_term_emu_tui_rust import app
from par_term_emu_tui_rust.config import TuiConfig

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _run_main_with_args(args: list[str]) -> None:
    """Invoke app.main() with a temporary sys.argv."""
    original_argv = sys.argv
    try:
        sys.argv = ["par-term-emu-tui-rust", *args]
        app.main()
    finally:
        sys.argv = original_argv


def test_cli_init_config_creates_config_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`--init-config` should create a default config file at the XDG path."""
    xdg_dir = tmp_path / "xdg-config-cli"
    xdg_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_dir))

    cfg_path = TuiConfig.default_config_path()
    assert not cfg_path.exists()

    _run_main_with_args(["--init-config"])

    assert cfg_path.exists()
    # The resulting file should be loadable as a TuiConfig
    loaded = TuiConfig.load(cfg_path)
    assert isinstance(loaded, TuiConfig)


def test_cli_list_themes_outputs_names(capsys: pytest.CaptureFixture[str]) -> None:
    """`--list-themes` should print a human-readable list of themes."""
    _run_main_with_args(["--list-themes"])
    captured = capsys.readouterr()

    # Header line
    assert "Available themes" in captured.out
    # At least one known theme name should be present
    assert "Dark Background" in captured.out or "dark background" in captured.out.lower()


def test_cli_export_and_apply_theme_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Export a theme and then apply it back using `--apply-theme-from`."""
    xdg_dir = tmp_path / "xdg-config-cli-themes"
    xdg_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_dir))

    cfg_path = TuiConfig.default_config_path()
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure a config exists; default theme is fine
    TuiConfig().save(cfg_path)

    export_name = "MyCustomTheme"

    # Export the current theme under a new name
    _run_main_with_args(["--export-theme", export_name])

    themes_dir = cfg_path.parent / "themes"
    exported_path = themes_dir / f"{export_name}.yaml"
    assert exported_path.exists()

    # Apply the theme back from the exported file
    _run_main_with_args(["--apply-theme-from", str(exported_path)])

    # Config should now reference the normalized key derived from export_name
    cfg_after = TuiConfig.load(cfg_path)
    expected_key = export_name.lower().replace(" ", "-")
    assert cfg_after.theme == expected_key
