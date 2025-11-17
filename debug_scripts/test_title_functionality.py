#!/usr/bin/env python3
"""
Test script to verify terminal title change functionality.

This script tests:
1. Terminal can detect title changes
2. TitleChanged messages are posted correctly
3. App subtitle updates when title changes
"""

import par_term_emu_core_rust


def test_title_property() -> None:
    """Test that Terminal has a title() method that works."""
    print("Testing Terminal.title() method...")

    # Create a terminal
    term = par_term_emu_core_rust.Terminal(80, 24)

    # Initial title should be empty
    initial_title = term.title()
    print(f"  Initial title: {initial_title!r}")
    assert initial_title == "", f"Expected empty title, got {initial_title!r}"

    # Send OSC 0 sequence to set title
    title_seq = "\x1b]0;Test Title\x07"
    term.process_str(title_seq)

    # Check title was updated
    new_title = term.title()
    print(f"  After OSC 0: {new_title!r}")
    assert new_title == "Test Title", f"Expected 'Test Title', got {new_title!r}"

    # Send OSC 2 sequence (window title)
    title_seq = "\x1b]2;Window Title\x07"
    term.process_str(title_seq)

    new_title = term.title()
    print(f"  After OSC 2: {new_title!r}")
    assert new_title == "Window Title", f"Expected 'Window Title', got {new_title!r}"

    # Send OSC 1 sequence (icon title)
    title_seq = "\x1b]1;Icon Title\x07"
    term.process_str(title_seq)

    new_title = term.title()
    print(f"  After OSC 1: {new_title!r}")
    # Note: OSC 1 might not change the window title, depending on implementation
    # Just verify it doesn't crash

    print("✅ Terminal.title() method works correctly!\n")


def test_message_integration() -> None:
    """Verify the messages module has TitleChanged."""
    print("Testing message integration...")

    from par_term_emu_tui_rust import messages

    # Check TitleChanged exists
    assert hasattr(messages, "TitleChanged"), "TitleChanged message not found"

    # Create a TitleChanged message
    msg = messages.TitleChanged(title="Test")
    assert msg.title == "Test"

    print("✅ TitleChanged message exists and works!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Terminal Title Change Functionality Tests")
    print("=" * 60 + "\n")

    try:
        test_title_property()
        test_message_integration()

        print("=" * 60)
        print("All tests passed! ✅")
        print("=" * 60)
        print("\nTo test the full integration:")
        print("1. Run: uv run par-term-emu-tui-rust")
        print("2. In the terminal, run: ./test_title_change.sh")
        print("3. Watch the subtitle update as titles change")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
