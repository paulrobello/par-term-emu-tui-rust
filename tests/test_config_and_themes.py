"""Tests for TuiConfig and theme utilities.

These tests avoid starting the Textual TUI or touching the Rust core by
focusing on pure-Python components: configuration loading/saving and theme
lookup/normalization.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from par_term_emu_tui_rust.config import TuiConfig
from par_term_emu_tui_rust.themes import THEMES, get_theme, list_theme_keys, list_themes

if TYPE_CHECKING:
    from pathlib import Path


def test_config_save_and_load_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TuiConfig.save() and TuiConfig.load() round-trip through YAML."""
    # Ensure this test uses an isolated XDG config home
    xdg_dir = tmp_path / "xdg-config-override"
    xdg_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_dir))

    cfg_path = TuiConfig.default_config_path()
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    original = TuiConfig()
    original.theme = "solarized-dark"
    original.scrollback_lines = 12345
    original.save(cfg_path)

    loaded = TuiConfig.load(cfg_path)
    assert loaded.theme == "solarized-dark"
    assert loaded.scrollback_lines == 12345


@pytest.mark.parametrize(
    ("name_variant", "expected_key"),
    [
        ("Dark Background", "dark-background"),
        ("dark-background", "dark-background"),
        ("DARK_BACKGROUND", "dark-background"),
    ],
)
def test_get_theme_normalizes_names(name_variant: str, expected_key: str) -> None:
    """get_theme() should resolve different textual variants to the same theme key."""
    theme = get_theme(name_variant)
    # THEMES keys are normalized lowercase-with-hyphens
    assert expected_key in THEMES
    assert theme == THEMES[expected_key]


def test_get_theme_raises_for_unknown_theme() -> None:
    """get_theme() should raise ValueError for unknown themes."""
    with pytest.raises(ValueError, match=r"Theme .* not found"):
        get_theme("this-theme-does-not-exist")


def test_list_themes_and_keys_are_consistent() -> None:
    """list_themes() and list_theme_keys() should reflect the THEMES mapping."""
    theme_keys = set(list_theme_keys())
    assert theme_keys == set(THEMES.keys())

    theme_display_names = set(list_themes())
    # All display names should correspond to some Theme.name in THEMES
    names_from_map = {theme.name for theme in THEMES.values()}
    assert theme_display_names == names_from_map
