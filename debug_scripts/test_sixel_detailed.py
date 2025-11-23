#!/usr/bin/env python3
"""Detailed test of Sixel processing to understand cursor and graphic positions."""

from par_term_emu_core_rust import Terminal

print("=== Detailed Sixel Processing Test ===\n")

term = Terminal(80, 40, 10000)

# Step 1: Initial state
print("1. Initial state:")
print(f"   Cursor: {term.cursor_position()}")

# Step 2: Output prompt
prompt = "user@host:~$ "
term.process(prompt.encode())
print(f"\n2. After prompt '{prompt}':")
print(f"   Cursor: {term.cursor_position()}")

# Step 3: Output command (simulating what the shell does)
command = "cat snake.sixel\n"
term.process(command.encode())
print(f"\n3. After command '{command.rstrip()}':")
print(f"   Cursor: {term.cursor_position()}")

# Step 4: Load just the first few bytes of Sixel to see what happens
with open("images/snake.sixel", "rb") as f:
    sixel_data = f.read()

print(f"\n4. Loading Sixel data ({len(sixel_data)} bytes)...")
term.process(sixel_data)

print(f"   Cursor after Sixel: {term.cursor_position()}")
print(f"   Graphics count: {term.graphics_count()}")
if term.graphics_count() > 0:
    g = term.graphics()[0]
    print(f"   Graphic position: (col={g.position[0]}, row={g.position[1]})")
    print(f"   Graphic size: {g.width}x{g.height} pixels = {(g.height + 1) // 2} rows")
    print(f"   Graphic scroll_offset: {g.scroll_offset_rows}")
print(f"   Scrollback len: {term.scrollback_len()}")

# Step 5: Shell outputs next prompt
print("\n5. Shell outputs next prompt:")
term.process(prompt.encode())
print(f"   Cursor: {term.cursor_position()}")
print(f"   Scrollback len: {term.scrollback_len()}")

# Show what's visible on screen
print("\n6. Visible screen content (rows 0, 1, 38, 39):")
for row in [0, 1, 38, 39]:
    line = term.get_line(row)
    if line:
        text = "".join(cell[0] for cell in line).rstrip()
        print(f"   Row {row:2d}: '{text}'")
    else:
        print(f"   Row {row:2d}: (empty)")

print("\n=== Test Complete ===")
