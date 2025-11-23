#!/usr/bin/env python3
"""Test script to verify graphics are preserved during scrolling."""

from par_term_emu_core_rust import Terminal

print("=== Testing Graphics Scrollback Behavior ===\n")

# Create terminal
term = Terminal(80, 40)
print(f"Terminal: {term.size()}")

# Load snake.sixel
print("\n1. Loading images/snake.sixel...")
with open("images/snake.sixel", "rb") as f:
    term.process(f.read())

print(f"   Graphics count: {term.graphics_count()}")
if term.graphics_count() > 0:
    g = term.graphics()[0]
    print(f"   Position: row {g.position[1]}")
    print(f"   Size: {g.width}x{g.height} pixels ({(g.height + 1) // 2} rows)")
    print(f"   Scroll offset: {g.scroll_offset_rows} rows")

# Simulate scrolling by adding blank lines
print("\n2. Simulating 100 lines of scrolling...")
for i in range(100):
    term.process(b"\n")

print(f"   Graphics count: {term.graphics_count()}")
if term.graphics_count() > 0:
    g = term.graphics()[0]
    print("   ✅ Graphic preserved!")
    print(f"   Position: row {g.position[1]}")
    print(f"   Scroll offset: {g.scroll_offset_rows} rows")
else:
    print("   ❌ ERROR: Graphics were removed!")
    print(f"   Dropped: {term.get_dropped_sixel_graphics()}")

# Scroll more to completely scroll off
print("\n3. Simulating 150 more lines (250 total)...")
for i in range(150):
    term.process(b"\n")

print(f"   Graphics count: {term.graphics_count()}")
if term.graphics_count() > 0:
    g = term.graphics()[0]
    print("   ⚠️  Still preserved (shouldn't be - graphic is only 225 rows)")
    print(f"   Position: row {g.position[1]}")
    print(f"   Scroll offset: {g.scroll_offset_rows} rows")
else:
    print("   ✅ Correctly removed (graphic completely scrolled off)")
    print(f"   Dropped: {term.get_dropped_sixel_graphics()}")

print("\n=== Test Complete ===")
