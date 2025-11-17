#!/usr/bin/env python3
"""
Test clipboard functionality to verify pyperclip is working correctly.
"""

import sys


def test_pyperclip_import() -> None:
    """Test that pyperclip can be imported."""
    print("Testing pyperclip import...")
    try:
        import pyperclip

        print(f"✅ pyperclip imported successfully (version {pyperclip.__version__})")
    except ImportError as e:
        print(f"❌ Failed to import pyperclip: {e}")
        sys.exit(1)


def test_clipboard_operations() -> None:
    """Test basic clipboard copy and paste operations."""
    print("\nTesting clipboard operations...")
    try:
        import pyperclip

        # Test copy
        test_text = "Test clipboard content from par-term-emu-tui-rust"
        pyperclip.copy(test_text)
        print(f"✅ Copied text to clipboard: {test_text!r}")

        # Test paste
        pasted = pyperclip.paste()
        print(f"✅ Pasted text from clipboard: {pasted!r}")

        # Verify they match
        if pasted == test_text:
            print("✅ Clipboard copy/paste verified!")
        else:
            print(f"❌ Mismatch: expected {test_text!r}, got {pasted!r}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Clipboard operations failed: {e}")
        sys.exit(1)


def test_clipboard_manager() -> None:
    """Test ClipboardManager class."""
    print("\nTesting ClipboardManager...")
    try:
        import par_term_emu_core_rust

        from par_term_emu_tui_rust.config import TuiConfig
        from par_term_emu_tui_rust.terminal_widget.clipboard import ClipboardManager

        # Create a terminal and config
        term = par_term_emu_core_rust.PtyTerminal(80, 24)
        config = TuiConfig()

        # Create clipboard manager
        clipboard = ClipboardManager(term=term, config=config)
        print("✅ ClipboardManager created successfully")

        # Test copy
        success, error = clipboard.copy_to_clipboard("Test from ClipboardManager", to_primary=False)
        if success:
            print("✅ ClipboardManager.copy_to_clipboard() succeeded")
        else:
            print(f"❌ ClipboardManager.copy_to_clipboard() failed: {error}")
            sys.exit(1)

        # Verify it was copied
        import pyperclip

        pasted = pyperclip.paste()
        if pasted == "Test from ClipboardManager":
            print("✅ ClipboardManager copy verified!")
        else:
            print(f"❌ Unexpected clipboard content: {pasted!r}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ ClipboardManager test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Clipboard Functionality Tests")
    print("=" * 60)

    test_pyperclip_import()
    test_clipboard_operations()
    test_clipboard_manager()

    print("\n" + "=" * 60)
    print("All clipboard tests passed! ✅")
    print("=" * 60)
    print("\nClipboard operations in the TUI should now work correctly.")
    print("Try copying text with Ctrl+Shift+C and pasting with Ctrl+Shift+V")
