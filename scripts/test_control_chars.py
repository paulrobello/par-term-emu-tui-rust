#!/usr/bin/env python3
"""Interactive test script for control character functionality.

This script demonstrates all 11 implemented control characters.
Run with: uv run python scripts/test_control_chars.py
"""

import sys
from pathlib import Path

# Add project root to Python path so we can import from tests/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from par_terminal.backend import TerminalBackend
from tests.fixtures.mock_delegate import MockDelegate


def test_vt_ff():
    """Test VT (0x0B) and FF (0x0C) - should behave like LF."""
    print("\n=== Test 1: VT and FF (Vertical Tab and Form Feed) ===")
    delegate = MockDelegate()
    backend = TerminalBackend(delegate, width=80, height=24)

    # Test VT
    backend.feed(b"Line 1\x0bLine 2\x0bLine 3")
    print(f"After VT: cursor at row {backend.cursor.y} (should be 2)")

    # Test FF
    backend.feed(b"\x0cLine 4")
    print(f"After FF: cursor at row {backend.cursor.y} (should be 3)")
    print("✅ PASS" if backend.cursor.y == 3 else "❌ FAIL")


def test_so_si():
    """Test SO (0x0E) and SI (0x0F) - character set switching."""
    print("\n=== Test 2: SO/SI (Shift Out/Shift In) - DEC Special Graphics ===")
    delegate = MockDelegate()
    backend = TerminalBackend(delegate, width=80, height=24)

    # Activate G1 (DEC Special Graphics)
    backend.feed(b"\x0e")
    print(f"After SO: G1 active = {backend.charset_state.is_g1_active}")

    # Write line-drawing characters
    backend.feed(b"lqqqqk")  # top border
    line = backend.read_line(0)

    # Check if characters were translated
    print(f"First character: '{line.cells[0].char}' (should be '┌')")
    print(f"Second character: '{line.cells[1].char}' (should be '─')")

    # Deactivate G1 (back to ASCII)
    backend.feed(b"\x0f")
    print(f"After SI: G1 active = {backend.charset_state.is_g1_active}")

    # Verify characters were translated
    is_box_char = line.cells[0].char == "┌"
    is_line_char = line.cells[1].char == "─"
    print("✅ PASS" if (is_box_char and is_line_char) else "❌ FAIL")


def test_ignored_chars():
    """Test characters that should be silently ignored."""
    print("\n=== Test 3: Ignored Characters (NUL, XON, XOFF, CAN, SUB, DEL) ===")
    delegate = MockDelegate()
    backend = TerminalBackend(delegate, width=80, height=24)

    # Write text with ignored characters interspersed
    backend.feed(b"Hello\x00\x11\x13\x18\x1a\x7fWorld")

    line = backend.read_line(0)
    result = "".join(cell.char for cell in line.cells[:10]).strip()

    print(f"Result: '{result}' (should be 'HelloWorld')")
    print("✅ PASS" if result == "HelloWorld" else "❌ FAIL")


def test_enq():
    """Test ENQ (0x05) - answerback transmission."""
    print("\n=== Test 4: ENQ (Enquiry) - Answerback ===")
    delegate = MockDelegate()
    backend = TerminalBackend(delegate, width=80, height=24)

    # Configure answerback
    backend.configure_answerback("VT100")

    # Send ENQ
    backend.feed(b"\x05")

    # Check if answerback was transmitted
    print(f"Responses sent: {delegate.responses}")
    print(f"Answerback: {delegate.responses[0] if delegate.responses else 'None'}")
    print("✅ PASS" if delegate.responses == [b"VT100"] else "❌ FAIL")


def test_dec_graphics():
    """Test DEC Special Graphics character mapping."""
    print("\n=== Test 5: DEC Special Graphics Character Map ===")
    delegate = MockDelegate()
    backend = TerminalBackend(delegate, width=80, height=24)

    # Activate G1
    backend.feed(b"\x0e")

    # Test specific mappings
    test_chars = {
        0x60: ("◆", "diamond"),
        0x6A: ("┘", "lower right corner"),
        0x71: ("─", "horizontal line"),
        0x78: ("│", "vertical line"),
    }

    all_pass = True
    for byte_val, (expected_char, desc) in test_chars.items():
        backend.feed(bytes([byte_val]))

    line = backend.read_line(0)

    for i, (byte_val, (expected_char, desc)) in enumerate(test_chars.items()):
        actual = line.cells[i].char
        matches = actual == expected_char
        print(f"  {desc}: '{actual}' (expected '{expected_char}') {'✅' if matches else '❌'}")
        all_pass = all_pass and matches

    print("✅ PASS" if all_pass else "❌ FAIL")


def test_integration():
    """Test control characters with other features."""
    print("\n=== Test 6: Integration - Control Chars + SGR Formatting ===")
    delegate = MockDelegate()
    backend = TerminalBackend(delegate, width=80, height=24)

    # Bold + red text
    backend.feed(b"\x1b[1;31m")

    # Activate G1 and write line-drawing chars
    backend.feed(b"\x0e")
    backend.feed(b"qqq")  # horizontal lines

    # Back to G0
    backend.feed(b"\x0f")
    backend.feed(b"ABC")

    line = backend.read_line(0)

    # Check character translation
    char0_is_line = line.cells[0].char == "─"
    char3_is_normal = line.cells[3].char == "A"

    # Check formatting persists
    char0_bold = line.cells[0].bold
    char0_red = line.cells[0].fg_color.r_or_index == 1
    char3_bold = line.cells[3].bold
    char3_red = line.cells[3].fg_color.r_or_index == 1

    print(f"  Line drawing char: '{line.cells[0].char}' (expected '─') {'✅' if char0_is_line else '❌'}")
    print(f"  Normal char: '{line.cells[3].char}' (expected 'A') {'✅' if char3_is_normal else '❌'}")
    print(f"  Formatting persists: bold={char3_bold}, red={char3_red} {'✅' if (char3_bold and char3_red) else '❌'}")

    all_pass = char0_is_line and char3_is_normal and char3_bold and char3_red
    print("✅ PASS" if all_pass else "❌ FAIL")


if __name__ == "__main__":
    print("=" * 70)
    print("Control Character Functionality Tests")
    print("=" * 70)

    test_vt_ff()
    test_so_si()
    test_ignored_chars()
    test_enq()
    test_dec_graphics()
    test_integration()

    print("\n" + "=" * 70)
    print("All tests complete! Run 'uv run pytest tests/unit/test_control_characters.py -v'")
    print("for comprehensive automated testing.")
    print("=" * 70)
