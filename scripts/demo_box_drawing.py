#!/usr/bin/env python3
"""Visual demo of DEC Special Graphics (box-drawing characters).

This demonstrates the SO/SI charset switching functionality.
Run with: uv run python scripts/demo_box_drawing.py
"""

import sys
from pathlib import Path

# Add project root to Python path so we can import from tests/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from par_terminal.backend import TerminalBackend
from tests.fixtures.mock_delegate import MockDelegate


def draw_box(backend, width, height, title="", at_row=None, at_col=None):
    """Draw a box using DEC Special Graphics characters.

    Args:
        backend: TerminalBackend instance
        width: Box width in characters
        height: Box height in characters
        title: Optional title for the box
        at_row: Optional starting row (1-indexed, like cursor positioning)
        at_col: Optional starting column (1-indexed, like cursor positioning)
    """
    # Get current cursor position if not specified
    if at_row is None:
        at_row = backend.cursor.y + 1  # Convert to 1-indexed
    if at_col is None:
        at_col = backend.cursor.x + 1  # Convert to 1-indexed

    # Activate G1 (DEC Special Graphics)
    backend.feed(b"\x0e")

    # Top border
    backend.feed(f"\x1b[{at_row};{at_col}H".encode())  # Position cursor
    backend.feed(b"l")  # top-left corner
    backend.feed(b"q" * (width - 2))  # horizontal line
    backend.feed(b"k")  # top-right corner

    current_row = at_row + 1

    # Title if provided
    if title:
        backend.feed(f"\x1b[{current_row};{at_col}H".encode())
        backend.feed(b"x")  # vertical line
        backend.feed(b"\x0f")  # SI - switch to ASCII for title
        backend.feed(f" {title}".encode())
        backend.feed(b" " * (width - len(title) - 3))
        backend.feed(b"\x0e")  # SO - back to graphics
        backend.feed(b"x")  # vertical line
        current_row += 1

    # Middle rows
    for _ in range(height - 2 - (1 if title else 0)):
        backend.feed(f"\x1b[{current_row};{at_col}H".encode())
        backend.feed(b"x")  # vertical line
        backend.feed(b" " * (width - 2))
        backend.feed(b"x")  # vertical line
        current_row += 1

    # Bottom border
    backend.feed(f"\x1b[{current_row};{at_col}H".encode())
    backend.feed(b"m")  # bottom-left corner
    backend.feed(b"q" * (width - 2))  # horizontal line
    backend.feed(b"j")  # bottom-right corner

    # Deactivate G1 (back to ASCII)
    backend.feed(b"\x0f")


def print_terminal_buffer(backend, rows=None):
    """Print the terminal buffer content."""
    if rows is None:
        rows = backend.height

    for y in range(rows):
        line = backend.read_line(y)
        chars = "".join(cell.char for cell in line.cells[: backend.width])
        print(chars.rstrip())


if __name__ == "__main__":
    print("=" * 70)
    print("DEC Special Graphics Demo - Box Drawing")
    print("=" * 70)
    print()

    # Create terminal backend
    delegate = MockDelegate()
    backend = TerminalBackend(delegate, width=60, height=20)

    # Draw a simple box
    print("1. Simple Box (10x5):")
    draw_box(backend, width=10, height=5, at_row=1, at_col=1)
    print_terminal_buffer(backend, rows=5)
    print()

    # Clear and draw a box with title
    backend = TerminalBackend(delegate, width=60, height=20)
    print("2. Box with Title (30x7):")
    draw_box(backend, width=30, height=7, title="Control Characters", at_row=1, at_col=1)
    print_terminal_buffer(backend, rows=7)
    print()

    # Draw nested boxes
    backend = TerminalBackend(delegate, width=60, height=20)
    print("3. Nested Boxes:")
    draw_box(backend, width=40, height=10, title="Outer Box", at_row=1, at_col=1)
    # Draw inner box at row 3, column 5 (inside the outer box)
    draw_box(backend, width=32, height=6, title="Inner Box", at_row=3, at_col=5)

    print_terminal_buffer(backend, rows=10)
    print()

    # Show all DEC Special Graphics characters
    backend = TerminalBackend(delegate, width=60, height=20)
    print("4. All DEC Special Graphics Characters (0x60-0x7E):")
    print()

    backend.feed(b"\x0e")  # Activate G1

    char_map = {
        0x60: "◆ diamond",
        0x61: "▒ checkerboard",
        0x6A: "┘ lower right",
        0x6B: "┐ upper right",
        0x6C: "┌ upper left",
        0x6D: "└ lower left",
        0x6E: "┼ crossing",
        0x71: "─ horizontal",
        0x74: "├ left tee",
        0x75: "┤ right tee",
        0x76: "┴ bottom tee",
        0x77: "┬ top tee",
        0x78: "│ vertical",
    }

    for byte_val, description in char_map.items():
        backend.feed(bytes([byte_val]))
        line = backend.read_line(backend.cursor.y)
        char = line.cells[backend.cursor.x - 1].char
        print(f"  0x{byte_val:02X}: {char}  ({description})")
        backend.feed(b"\r\n")

    backend.feed(b"\x0f")  # Deactivate G1

    print()
    print("=" * 70)
    print("Demo complete! These characters are used by applications like:")
    print("  - vim (for drawing windows and splits)")
    print("  - tmux (for pane borders)")
    print("  - htop (for UI elements)")
    print("  - midnight commander (for file manager UI)")
    print("=" * 70)
