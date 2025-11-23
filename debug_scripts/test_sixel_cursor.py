#!/usr/bin/env python3
"""Test to check cursor position and scrollback after Sixel load."""

from par_term_emu_core_rust import Terminal

print("=== Testing Cursor Position After Sixel ===\n")

# Create terminal with scrollback
term = Terminal(80, 40, 10000)  # 80x40 with 10k scrollback
print(f"Terminal: {term.size()}, Scrollback limit: 10000")

# Simulate shell prompt
prompt = "user@host:~$ "
term.process(prompt.encode())
print("\n1. After initial prompt:")
print(f"   Cursor: {term.cursor_position()}")
print(f"   Scrollback len: {term.scrollback_len()}")

# Load snake.sixel
print("\n2. Loading images/snake.sixel...")
with open("images/snake.sixel", "rb") as f:
    term.process(f.read())

print(f"   Cursor: {term.cursor_position()}")
print(f"   Scrollback len: {term.scrollback_len()}")
print(f"   Graphics count: {term.graphics_count()}")
if term.graphics_count() > 0:
    g = term.graphics()[0]
    print(f"   Graphic at row {g.position[1]}, scroll_offset: {g.scroll_offset_rows}")

# Simulate shell outputting next prompt
print("\n3. Adding next prompt:")
term.process(b"\n")
term.process(prompt.encode())

print(f"   Cursor: {term.cursor_position()}")
print(f"   Scrollback len: {term.scrollback_len()}")

# Show what's on screen at bottom
print("\n4. Bottom 5 rows of screen:")
for row in range(35, 40):
    line = term.get_line(row)
    if line:
        text = "".join(cell[0] for cell in line).rstrip()
        if text:
            print(f"   Row {row}: '{text}'")
        else:
            print(f"   Row {row}: (blank)")
    else:
        print(f"   Row {row}: (empty)")

print("\n=== Test Complete ===")
