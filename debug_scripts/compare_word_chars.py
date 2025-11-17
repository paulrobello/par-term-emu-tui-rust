#!/usr/bin/env python3
"""Compare our word_characters with iTerm2's default."""

# iTerm2 default (from iTermPreferences.m)
iterm2_chars = set("/-+\\~_.")

# Our current default (from config.py)
our_chars = set("-_.~:/?#[]@!$&'()*+,;=")

print("Word Characters Comparison")
print("=" * 70)
print()

print(f"iTerm2 default: {''.join(sorted(iterm2_chars))}")
print(f"Our default:    {''.join(sorted(our_chars))}")
print()

print("Analysis:")
print("-" * 70)

# Check if we include all iTerm2 chars
missing_from_ours = iterm2_chars - our_chars
if missing_from_ours:
    print(f"❌ MISSING from our config: {sorted(missing_from_ours)}")
else:
    print("✅ Our config includes ALL iTerm2 characters")

print()

# Show what we have extra
extra_in_ours = our_chars - iterm2_chars
if extra_in_ours:
    print(f"Additional chars in our config: {''.join(sorted(extra_in_ours))}")
    print()
    print("Extra characters by category:")
    print(f"  URL/URI: :/?#@!&;=")
    print(f"  Brackets: []")
    print(f"  Quotes/Parens: '()*")
    print(f"  Other: $,")

print()
print("=" * 70)
