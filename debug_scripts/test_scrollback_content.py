#!/usr/bin/env python3
"""Test scrollback content with text before Sixel."""

from par_term_emu_core_rust import Terminal

print("=== Testing Scrollback Content ===\n")

term = Terminal(80, 40, 10000)

# Fill terminal with some content first
print("1. Adding 20 lines of text...")
for i in range(20):
    term.process(f"Line {i:02d}: This is some test content\n".encode())

print(f"   Cursor: {term.cursor_position()}")
print(f"   Scrollback len: {term.scrollback_len()}")

# Now load Sixel
print("\n2. Loading Sixel...")
with open("images/snake.sixel", "rb") as f:
    term.process(f.read())

print(f"   Cursor: {term.cursor_position()}")
print(f"   Scrollback len: {term.scrollback_len()}")
print(f"   Graphics count: {term.graphics_count()}")
if term.graphics_count() > 0:
    g = term.graphics()[0]
    print(f"   Graphic at row {g.position[1]}, scroll_offset: {g.scroll_offset_rows}")

# Show what can be scrolled back
print("\n3. Scrollback content (first 5 lines):")
for i in range(min(5, term.scrollback_len())):
    line = term.scrollback_line(i)
    if line:
        text = "".join(cell[0] for cell in line).rstrip()
        print(f"   Scrollback[{i}]: '{text}'")

print("\n=== Test Complete ===")
