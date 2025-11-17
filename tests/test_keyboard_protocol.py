"""
Test KITTY keyboard protocol integration.

Tests the conversion of Textual Key events to KITTY protocol sequences
and protocol activation on the PTY terminal.
"""

from __future__ import annotations

import sys

import pytest

# Skip stub for these tests - we need the real PtyTerminal
if "par_term_emu_core_rust" in sys.modules:
    del sys.modules["par_term_emu_core_rust"]

from par_term_emu_core_rust import Terminal
from textual.events import Key

from par_term_emu_tui_rust.config import TuiConfig


class MockTerminalWidget:
    """Minimal mock of TerminalWidget for testing keyboard protocol methods."""

    def __init__(self) -> None:
        """Initialize mock widget."""
        # Import the actual methods from the real widget
        from par_term_emu_tui_rust.terminal_widget.terminal_widget import TerminalWidget

        self._key_to_unicode = TerminalWidget._key_to_unicode.__get__(self)
        self._key_event_to_kitty_sequence = TerminalWidget._key_event_to_kitty_sequence.__get__(self)


class TestKeyboardProtocolCore:
    """Test keyboard protocol at the terminal emulator core level."""

    def test_protocol_activation(self) -> None:
        """Test that protocol can be activated on terminal."""
        term = Terminal(80, 24)

        # Initially disabled
        assert term.keyboard_flags() == 0

        # Enable flag 1 (disambiguate)
        term.set_keyboard_flags(1, mode=1)
        assert term.keyboard_flags() == 1

        # Query returns correct value
        term.query_keyboard_flags()
        response = term.drain_responses()
        assert response == b"\x1b[?1u"

    def test_stack_operations(self) -> None:
        """Test push/pop work correctly."""
        term = Terminal(80, 24)

        # Set initial flags
        term.set_keyboard_flags(1, mode=1)

        # Push new flags
        term.push_keyboard_flags(3)
        assert term.keyboard_flags() == 3

        # Pop back
        term.pop_keyboard_flags(1)
        assert term.keyboard_flags() == 1

    def test_protocol_flags_combinations(self) -> None:
        """Test different flag combinations."""
        term = Terminal(80, 24)

        # Test flag 1 (disambiguate)
        term.set_keyboard_flags(1, mode=1)
        assert term.keyboard_flags() == 1

        # Test flag 3 (disambiguate + events)
        term.set_keyboard_flags(3, mode=1)
        assert term.keyboard_flags() == 3

        # Test flag 7 (disambiguate + events + alternate)
        term.set_keyboard_flags(7, mode=1)
        assert term.keyboard_flags() == 7

    def test_reset_clears_protocol(self) -> None:
        """Test that terminal reset clears protocol state."""
        term = Terminal(80, 24)

        term.set_keyboard_flags(15, mode=1)
        assert term.keyboard_flags() == 15

        term.reset()
        assert term.keyboard_flags() == 0


class TestKeyToUnicode:
    """Test _key_to_unicode helper method."""

    def test_single_character_keys(self) -> None:
        """Test single character to Unicode conversion."""
        widget = MockTerminalWidget()

        assert widget._key_to_unicode("a") == 97
        assert widget._key_to_unicode("z") == 122
        assert widget._key_to_unicode("A") == 65
        assert widget._key_to_unicode("Z") == 90
        assert widget._key_to_unicode("0") == 48
        assert widget._key_to_unicode("9") == 57
        assert widget._key_to_unicode(" ") == 32

    def test_functional_keys(self) -> None:
        """Test functional keys to Unicode conversion."""
        widget = MockTerminalWidget()

        # Common keys
        assert widget._key_to_unicode("escape") == 27
        assert widget._key_to_unicode("enter") == 13
        assert widget._key_to_unicode("tab") == 9
        assert widget._key_to_unicode("backspace") == 127

        # KITTY extended codes
        assert widget._key_to_unicode("delete") == 57426
        assert widget._key_to_unicode("up") == 57419
        assert widget._key_to_unicode("down") == 57420
        assert widget._key_to_unicode("left") == 57417
        assert widget._key_to_unicode("right") == 57418

        # Function keys
        assert widget._key_to_unicode("f1") == 57376
        assert widget._key_to_unicode("f12") == 57387

    def test_unknown_keys(self) -> None:
        """Test that unknown keys return None."""
        widget = MockTerminalWidget()

        assert widget._key_to_unicode("unknown_key") is None
        assert widget._key_to_unicode("ctrl+a") is None  # Modifier combo, not single key


class TestKeyEventToKittySequence:
    """Test _key_event_to_kitty_sequence converter method."""

    def test_simple_keys_no_modifiers(self) -> None:
        """Test simple keys without modifiers."""
        widget = MockTerminalWidget()

        # Single character
        event = Key("a", "a")
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[97u"

        # Tab
        event = Key("tab", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[9u"

        # Enter
        event = Key("enter", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[13u"

        # Escape
        event = Key("escape", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[27u"

    def test_keys_with_ctrl(self) -> None:
        """Test keys with Ctrl modifier."""
        widget = MockTerminalWidget()

        # Ctrl+A
        event = Key("ctrl+a", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[97;5u"

        # Ctrl+I
        event = Key("ctrl+i", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[105;5u"

        # Ctrl+M
        event = Key("ctrl+m", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[109;5u"

    def test_keys_with_shift(self) -> None:
        """Test keys with Shift modifier."""
        widget = MockTerminalWidget()

        # Shift+A (capital A)
        event = Key("shift+a", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[97;2u"

        # Shift+Tab
        event = Key("shift+tab", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[9;2u"

    def test_keys_with_multiple_modifiers(self) -> None:
        """Test keys with multiple modifiers."""
        widget = MockTerminalWidget()

        # Ctrl+Shift+A
        # modifiers: ctrl(4) | shift(1) = 5, +1 = 6
        event = Key("ctrl+shift+a", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[97;6u"

        # Ctrl+Alt+A
        # modifiers: ctrl(4) | alt(2) = 6, +1 = 7
        event = Key("ctrl+alt+a", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[97;7u"

        # Shift+Alt+Tab
        # modifiers: shift(1) | alt(2) = 3, +1 = 4
        event = Key("shift+alt+tab", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[9;4u"

    def test_function_keys(self) -> None:
        """Test function keys."""
        widget = MockTerminalWidget()

        # F1
        event = Key("f1", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[57376u"

        # Ctrl+F1
        event = Key("ctrl+f1", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[57376;5u"

    def test_arrow_keys(self) -> None:
        """Test arrow keys."""
        widget = MockTerminalWidget()

        # Up arrow
        event = Key("up", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[57419u"

        # Ctrl+Up
        event = Key("ctrl+up", None)
        assert widget._key_event_to_kitty_sequence(event) == "\x1b[57419;5u"


class TestDisambiguation:
    """Test that ambiguous keys produce different sequences."""

    def test_ctrl_i_vs_tab(self) -> None:
        """Ctrl+I and Tab should produce different sequences."""
        widget = MockTerminalWidget()

        ctrl_i = widget._key_event_to_kitty_sequence(Key("ctrl+i", None))
        tab = widget._key_event_to_kitty_sequence(Key("tab", None))

        # They must be different!
        assert ctrl_i != tab
        assert ctrl_i == "\x1b[105;5u"  # Ctrl+I
        assert tab == "\x1b[9u"  # Tab

    def test_ctrl_m_vs_enter(self) -> None:
        """Ctrl+M and Enter should produce different sequences."""
        widget = MockTerminalWidget()

        ctrl_m = widget._key_event_to_kitty_sequence(Key("ctrl+m", None))
        enter = widget._key_event_to_kitty_sequence(Key("enter", None))

        # They must be different!
        assert ctrl_m != enter
        assert ctrl_m == "\x1b[109;5u"  # Ctrl+M
        assert enter == "\x1b[13u"  # Enter

    def test_ctrl_h_vs_backspace(self) -> None:
        """Ctrl+H and Backspace should produce different sequences."""
        widget = MockTerminalWidget()

        ctrl_h = widget._key_event_to_kitty_sequence(Key("ctrl+h", None))
        backspace = widget._key_event_to_kitty_sequence(Key("backspace", None))

        # They must be different!
        assert ctrl_h != backspace
        assert ctrl_h == "\x1b[104;5u"  # Ctrl+H
        assert backspace == "\x1b[127u"  # Backspace


class TestConfiguration:
    """Test keyboard protocol configuration."""

    def test_config_defaults(self) -> None:
        """Test that config has correct defaults."""
        config = TuiConfig()

        # Should be disabled by default
        assert config.keyboard_protocol_enabled is False
        # Default flags should be 1 (disambiguate)
        assert config.keyboard_protocol_flags == 1
        # Auto-detect should be disabled by default
        assert config.keyboard_protocol_auto_detect is False

    def test_config_override(self) -> None:
        """Test that config can be overridden."""
        config = TuiConfig()

        # Enable protocol
        config.keyboard_protocol_enabled = True
        assert config.keyboard_protocol_enabled is True

        # Change flags
        config.keyboard_protocol_flags = 3  # disambiguate + events
        assert config.keyboard_protocol_flags == 3

        # Enable auto-detect
        config.keyboard_protocol_auto_detect = True
        assert config.keyboard_protocol_auto_detect is True


class TestSmartDetection:
    """Test keyboard protocol smart detection (Option B)."""

    def test_protocol_state_tracking(self) -> None:
        """Test that terminal keyboard flags can be tracked."""
        term = Terminal(80, 24)

        # Initially no flags
        assert term.keyboard_flags() == 0

        # Simulate app requesting protocol (like what an app would send)
        term.set_keyboard_flags(1, mode=1)
        assert term.keyboard_flags() == 1

        # Simulate app disabling protocol
        term.set_keyboard_flags(0, mode=1)
        assert term.keyboard_flags() == 0

    def test_protocol_push_pop(self) -> None:
        """Test protocol stack operations for smart detection."""
        term = Terminal(80, 24)

        # Simulate app pushing protocol (like neovim does)
        term.push_keyboard_flags(1)
        assert term.keyboard_flags() == 1

        # Pop to disable
        term.pop_keyboard_flags(1)
        assert term.keyboard_flags() == 0

    def test_config_auto_detect_mode(self) -> None:
        """Test auto-detect configuration."""
        config = TuiConfig()

        # Manual mode (default)
        assert config.keyboard_protocol_enabled is False
        assert config.keyboard_protocol_auto_detect is False

        # Enable auto-detect
        config.keyboard_protocol_auto_detect = True
        assert config.keyboard_protocol_auto_detect is True

        # Can have both enabled
        config.keyboard_protocol_enabled = True
        assert config.keyboard_protocol_enabled is True
        assert config.keyboard_protocol_auto_detect is True


class TestModifierEncoding:
    """Test modifier encoding correctness."""

    def test_single_modifiers(self) -> None:
        """Test each modifier individually."""
        widget = MockTerminalWidget()

        # Shift = 1, +1 = 2
        event = Key("shift+a", None)
        seq = widget._key_event_to_kitty_sequence(event)
        assert seq is not None
        assert ";2u" in seq

        # Alt = 2, +1 = 3
        event = Key("alt+a", None)
        seq = widget._key_event_to_kitty_sequence(event)
        assert seq is not None
        assert ";3u" in seq

        # Ctrl = 4, +1 = 5
        event = Key("ctrl+a", None)
        seq = widget._key_event_to_kitty_sequence(event)
        assert seq is not None
        assert ";5u" in seq

        # Super = 8, +1 = 9
        event = Key("super+a", None)
        seq = widget._key_event_to_kitty_sequence(event)
        assert seq is not None
        assert ";9u" in seq

    def test_modifier_combinations(self) -> None:
        """Test modifier combinations."""
        widget = MockTerminalWidget()

        # Shift(1) + Ctrl(4) = 5, +1 = 6
        event = Key("ctrl+shift+a", None)
        seq = widget._key_event_to_kitty_sequence(event)
        assert seq is not None
        assert ";6u" in seq

        # Alt(2) + Ctrl(4) = 6, +1 = 7
        event = Key("alt+ctrl+a", None)
        seq = widget._key_event_to_kitty_sequence(event)
        assert seq is not None
        assert ";7u" in seq

        # Shift(1) + Alt(2) + Ctrl(4) = 7, +1 = 8
        event = Key("alt+ctrl+shift+a", None)
        seq = widget._key_event_to_kitty_sequence(event)
        assert seq is not None
        assert ";8u" in seq


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
