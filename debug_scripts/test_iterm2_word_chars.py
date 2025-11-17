#!/usr/bin/env python3
"""Test word selection with iTerm2-compatible word characters."""

import par_term_emu_core_rust

# iTerm2 default word characters
iterm2_word_chars = "/-+\\~_."

# Create a terminal instance
term = par_term_emu_core_rust.Terminal(80, 24)

# Write test text with various special characters
term.process_str("foo-bar foo.bar foo:bar foo/bar foo+baz file_name~backup test\\path")

print("Testing with iTerm2-compatible word_characters: \"/-+\\~_.\"")
print("=" * 70)
print("Text: 'foo-bar foo.bar foo:bar foo/bar foo+baz file_name~backup test\\path'")
print()

# Test cases: (col, expected_word, description)
test_cases = [
    (0, "foo-bar", "hyphen included (in iTerm2 set)"),
    (8, "foo.bar", "dot included (in iTerm2 set)"),
    (16, "foo", "colon is separator (NOT in iTerm2 set)"),
    (20, "bar", "colon is separator (NOT in iTerm2 set)"),
    (24, "foo/bar", "slash included (in iTerm2 set)"),
    (32, "foo+baz", "plus included (in iTerm2 set)"),
    (40, "file_name~backup", "underscore and tilde included (in iTerm2 set)"),
    (57, "test\\path", "backslash included (in iTerm2 set)"),
]

print("Word Selection Results:")
print("-" * 70)

all_passed = True
for col, expected, description in test_cases:
    result = term.get_word_at(col, 0, iterm2_word_chars)
    status = "✅" if result == expected else "❌"
    print(f"{status} col {col:2d}: '{result:20s}' (expected: '{expected:15s}') - {description}")
    if result != expected:
        all_passed = False

print()
print("=" * 70)
if all_passed:
    print("✅ All tests passed! Word selection matches iTerm2 behavior.")
else:
    print("❌ Some tests failed!")
print("=" * 70)
