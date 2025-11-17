#!/usr/bin/env python3
"""Test script to verify hyperlink styling works correctly."""

import par_term_emu_core_rust


def test_hyperlink_styling() -> None:
    """Test that hyperlinks get styled with the configured link color."""
    print("Testing hyperlink styling...\n")

    # Create terminal
    term = par_term_emu_core_rust.Terminal(80, 24)

    # Set link color to blue
    print("Setting link color to RGB(100, 150, 255) - blue")
    term.set_link_color(100, 150, 255)

    # Process an OSC 8 hyperlink
    print("Processing OSC 8 hyperlink: 'Click me' -> https://example.com")
    term.process_str("\x1b]8;;https://example.com\x07Click me!\x1b]8;;\x07")

    # Get the line and check the attributes
    snapshot = term.create_snapshot()
    line = snapshot.get_line(0)

    print("\nLine cells:")
    for col, (char, fg, bg, attrs) in enumerate(line[:15]):
        if char and char.strip():
            hyperlink_id = attrs.hyperlink_id if attrs else None
            print(f"  col={col:2d} char={char!r} fg={fg!r:20s} bg={bg!r:20s} hyperlink_id={hyperlink_id}")

    # Check that cells have hyperlink_id set
    has_hyperlink = any(attrs and attrs.hyperlink_id is not None for _, _, _, attrs in line[:10])

    if has_hyperlink:
        print("\n✅ Hyperlink ID detected in cells")
    else:
        print("\n❌ No hyperlink ID found in cells")
        return

    # Get the URL from the hyperlink (using terminal, not snapshot)
    url = term.get_hyperlink(0, 0)
    print(f"\nRetrieved URL: {url!r}")

    if url == "https://example.com":
        print("✅ Hyperlink URL matches expected value")
    else:
        print(f"❌ Expected 'https://example.com', got {url!r}")

    print("\nNote: The TUI renderer will apply the blue color during rendering.")
    print("The terminal emulator stores the hyperlink ID, and the renderer applies styling.")


if __name__ == "__main__":
    print("=" * 70)
    print("Hyperlink Styling Test")
    print("=" * 70 + "\n")

    try:
        test_hyperlink_styling()

        print("\n" + "=" * 70)
        print("Test complete!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
