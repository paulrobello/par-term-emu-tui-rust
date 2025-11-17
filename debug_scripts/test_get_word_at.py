#!/usr/bin/env python3
"""Test script to verify get_word_at() API and word selection integration."""

import par_term_emu_core_rust


def test_get_word_at_api() -> None:
    """Test the get_word_at() API."""
    print("Testing get_word_at() API:")
    print("-" * 60)

    # Create a terminal instance
    term = par_term_emu_core_rust.Terminal(80, 24)

    # Write some test text
    term.process_str("hello world test-string url.example.com")

    # Default word characters (from config)
    word_chars = "-_.~:/?#[]@!$&'()*+,;="

    # Test cases: (col, expected_word)
    test_cases = [
        (0, "hello"),
        (6, "world"),
        (12, "test-string"),
        (24, "url.example.com"),
        (50, None),
    ]

    all_passed = True
    for col, expected in test_cases:
        result = term.get_word_at(col, 0, word_chars)
        status = "✅" if result == expected else "❌"
        print(f"{status} get_word_at({col:2d}, 0) = {result!r:20s} (expected: {expected!r})")
        if result != expected:
            all_passed = False

    print()
    if all_passed:
        print("✅ All get_word_at() tests passed!")
    else:
        print("❌ Some tests failed!")
    print()


def test_selection_integration() -> None:
    """Test word selection integration."""
    print("Testing word selection integration:")
    print("-" * 60)

    from par_term_emu_tui_rust.config import TuiConfig
    from par_term_emu_tui_rust.terminal_widget.selection import SelectionManager

    # Create terminal and config
    term = par_term_emu_core_rust.Terminal(80, 24)
    config = TuiConfig()
    term.process_str("hello world test-string url.example.com")

    # Create selection manager
    def get_cols() -> int:
        return 80

    selection = SelectionManager(term, config, get_cols)

    # Create snapshot
    snapshot = term.create_snapshot()

    # Test word selection at various positions
    test_cases = [
        (0, 0, "hello", (0, 4)),
        (6, 0, "world", (6, 10)),
        (12, 0, "test-string", (12, 22)),
        (24, 0, "url.example.com", (24, 38)),
    ]

    all_passed = True
    for col, row, expected_word, (expected_start, expected_end) in test_cases:
        selection.clear()
        selection.select_word_at(col, row, snapshot)

        if selection.start and selection.end:
            start_col, start_row = selection.start
            end_col, end_row = selection.end
            selected_text = ""
            for c in range(start_col, end_col + 1):
                char = term.get_char(c, row)
                selected_text += char if char else " "
            selected_text = selected_text.rstrip()

            status = "✅" if selected_text == expected_word else "❌"
            print(
                f"{status} select_word_at({col:2d}, {row}) = '{selected_text:20s}' "
                f"cols ({start_col},{end_col})  (expected: '{expected_word}' at ({expected_start},{expected_end}))"
            )
            if selected_text != expected_word:
                all_passed = False
        else:
            print(f"❌ select_word_at({col:2d}, {row}) returned no selection")
            all_passed = False

    print()
    if all_passed:
        print("✅ All word selection tests passed!")
    else:
        print("❌ Some tests failed!")
    print()


if __name__ == "__main__":
    print("=" * 70)
    print("Word Selection Test Suite")
    print("=" * 70 + "\n")

    try:
        test_get_word_at_api()
        test_selection_integration()

        print("=" * 70)
        print("All tests complete!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        raise
