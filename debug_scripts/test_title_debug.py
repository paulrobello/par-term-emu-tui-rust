#!/usr/bin/env python3
"""
Debug script to test title changes in the terminal emulator directly.
"""

import time

import par_term_emu_core_rust


def test_title_changes() -> None:
    """Test that title changes are detected properly."""
    print("Testing terminal title changes...\n")

    # Create a Terminal (not PtyTerminal) for testing escape sequence processing
    # PtyTerminal requires an active PTY session
    term = par_term_emu_core_rust.Terminal(80, 24)

    print(f"Initial title: {term.title()!r}")
    assert term.title() == "", "Initial title should be empty"

    # Send OSC 0 sequence directly
    print("\n1. Sending OSC 0 sequence: \\x1b]0;Test Title 1\\x07")
    term.process_str("\x1b]0;Test Title 1\x07")

    # Give it a moment to process
    time.sleep(0.1)

    title = term.title()
    print(f"   Title after OSC 0: {title!r}")
    print("   Expected: 'Test Title 1'")
    print(f"   Match: {title == 'Test Title 1'}")

    if title != "Test Title 1":
        print("   ⚠️  Title did not update!")
        print("\n   Trying with process_str instead...")
        term.process_str("\x1b]0;Test via process_str\x07")
        time.sleep(0.1)
        title = term.title()
        print(f"   Title after process_str: {title!r}")

    print("\n2. Sending OSC 2 sequence: \\x1b]2;Window Title\\x07")
    term.process_str("\x1b]2;Window Title\x07")
    time.sleep(0.1)

    title = term.title()
    print(f"   Title after OSC 2: {title!r}")
    print("   Expected: 'Window Title'")
    print(f"   Match: {title == 'Window Title'}")

    print("\n3. Checking if pty_read is needed...")
    # Maybe we need to read from the PTY?
    try:
        # Create fresh terminal with shell
        import os

        shell = os.environ.get("SHELL", "/bin/bash")
        term2 = par_term_emu_core_rust.PtyTerminal(80, 24, shell)

        print(f"   Created PtyTerminal with shell: {shell}")
        print(f"   Initial title: {term2.title()!r}")

        # Write OSC sequence to the shell
        term2.write_str("\x1b]0;Shell Title Test\x07")
        time.sleep(0.1)

        # Try reading to process any output
        try:
            data = term2.pty_read(1024)
            print(f"   Read {len(data)} bytes from PTY")
        except Exception as e:
            print(f"   pty_read error: {e}")

        title = term2.title()
        print(f"   Title after write to shell: {title!r}")

        # Try sending it as if typed in the shell
        print("\n4. Testing by sending to shell stdin...")
        # Send the sequence followed by Enter
        term2.write_str("printf '\\033]0;Typed Title\\007'\n")
        time.sleep(0.2)

        # Read output
        try:
            data = term2.pty_read(1024)
            print(f"   Read {len(data)} bytes from PTY after printf")
        except Exception:
            pass

        title = term2.title()
        print(f"   Title after printf command: {title!r}")

    except Exception as e:
        print(f"   Error with PtyTerminal test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 70)
    print("Terminal Title Change Debug Test")
    print("=" * 70 + "\n")

    test_title_changes()

    print("\n" + "=" * 70)
    print("Debug test complete")
    print("=" * 70)
