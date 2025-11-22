#!/usr/bin/env python3
"""Test to verify graphics appear correctly when viewing scrollback."""

from par_term_emu_core_rust import Terminal

print("=== Testing Scrollback Graphics Rendering ===\n")

term = Terminal(80, 40, 10000)

# Add 20 lines of text
for i in range(20):
    term.process(f"Line {i:02d}\r\n".encode())

# Load Sixel
print("1. Loading Sixel after 20 lines...")
with open("snake.sixel", "rb") as f:
    term.process(f.read())

print(f"   Scrollback len: {term.scrollback_len()}")
if term.graphics_count() > 0:
    g = term.graphics()[0]
    print(f"   Graphic: row={g.position[1]}, scroll_offset={g.scroll_offset_rows}")
    print(f"   Graphic height: {g.height} pixels = {(g.height + 1) // 2} rows")

# Simulate scrolling back to view the scrollback
print("\n2. Checking which 'virtual' graphics rows would appear in scrollback:")
print("   Scrollback contains rows at 'scroll distance' 1-40 from current view")

# For each scrollback position, calculate which graphic row it corresponds to
scrollback_len = term.scrollback_len()
if term.graphics_count() > 0:
    g = term.graphics()[0]
    scroll_off = g.scroll_offset_rows

    print(f"\n   Graphic scroll_offset = {scroll_off}")
    print(f"   This means rows 0-{scroll_off - 1} of the graphic have scrolled off")
    print("\n   When viewing scrollback:")

    # Check a few key scrollback positions
    for scroll_distance in [1, 10, 20, 30, 40, 100, 150, 186, 187]:
        if scroll_distance > scrollback_len:
            break

        # This is the formula from rendering.py line 719
        graphic_virtual_row = scroll_off - scroll_distance

        graphic_height_in_rows = (g.height + 1) // 2
        is_visible = 0 <= graphic_virtual_row < graphic_height_in_rows

        if is_visible:
            print(f"   - Scroll back {scroll_distance:3d} rows → graphic row {graphic_virtual_row:3d} (visible)")
        elif scroll_distance <= 40:  # Only show first 40
            print(f"   - Scroll back {scroll_distance:3d} rows → graphic row {graphic_virtual_row:3d} (not visible)")

# Verify we can query graphics_at_row for terminal rows
print("\n3. Testing graphics_at_row for live terminal:")
for row in [0, 1, 10, 38, 39]:
    graphics_at_row = term.graphics_at_row(row)
    if graphics_at_row:
        print(f"   Row {row}: {len(graphics_at_row)} graphic(s)")
    else:
        print(f"   Row {row}: no graphics")

print("\n=== Test Complete ===")
