#!/usr/bin/env python3
"""Test to determine if word_characters are INCLUDED or EXCLUDED from words."""

import par_term_emu_core_rust

# Create a terminal instance
term = par_term_emu_core_rust.Terminal(80, 24)

# Write test text with special characters
term.process_str("foo-bar foo.bar foo:bar foo/bar")

print("Testing word_characters semantics:")
print("=" * 70)
print("Text: 'foo-bar foo.bar foo:bar foo/bar'")
print()

# Test 1: Empty word_characters (nothing is part of words, everything is separator)
print("Test 1: word_characters = '' (empty - all special chars are separators)")
print("-" * 70)
word_chars = ""
for col in [0, 4, 8, 12, 16, 20, 24, 28]:
    result = term.get_word_at(col, 0, word_chars)
    char = term.get_char(col, 0)
    print(f"  col {col:2d} ('{char}'): {result!r}")
print()

# Test 2: Only hyphen
print("Test 2: word_characters = '-' (hyphen is part of word)")
print("-" * 70)
word_chars = "-"
for col in [0, 4, 8, 12, 16, 20, 24, 28]:
    result = term.get_word_at(col, 0, word_chars)
    char = term.get_char(col, 0)
    print(f"  col {col:2d} ('{char}'): {result!r}")
print()

# Test 3: Only dot
print("Test 3: word_characters = '.' (dot is part of word)")
print("-" * 70)
word_chars = "."
for col in [0, 4, 8, 12, 16, 20, 24, 28]:
    result = term.get_word_at(col, 0, word_chars)
    char = term.get_char(col, 0)
    print(f"  col {col:2d} ('{char}'): {result!r}")
print()

# Test 4: iTerm2 default
print("Test 4: word_characters = '/-+\\~_.' (iTerm2 default)")
print("-" * 70)
word_chars = "/-+\\~_."
for col in [0, 4, 8, 12, 16, 20, 24, 28]:
    result = term.get_word_at(col, 0, word_chars)
    char = term.get_char(col, 0)
    print(f"  col {col:2d} ('{char}'): {result!r}")
print()

print("=" * 70)
print("Conclusion:")
print("  - Characters IN word_characters are INCLUDED in word selection")
print("  - Characters NOT in word_characters are treated as SEPARATORS")
print("=" * 70)
