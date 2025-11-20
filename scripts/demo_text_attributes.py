#!/usr/bin/env python3
"""Compact text attributes rendering demo for visual verification."""


def s(title: str) -> None:
    """Print section header."""
    print(f"\n║ {title}")


def main() -> None:
    """Run compact demo of all text attributes."""
    # Box width: 77 chars total (75 content + 2 borders)
    print("\n╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║ PAR TERMINAL - TEXT ATTRIBUTES DEMO                                       ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")

    # Individual attributes
    s("1. INDIVIDUAL ATTRIBUTES")
    print("Normal    │ The quick brown fox")
    print("\x1b[1mBold      │ The quick brown fox\x1b[0m")
    print("\x1b[2mDim       │ The quick brown fox\x1b[0m")
    print("\x1b[3mItalic    │ The quick brown fox\x1b[0m")
    print("\x1b[4mUnderline │ The quick brown fox\x1b[0m")
    print("\x1b[7mReverse   │ The quick brown fox\x1b[0m")
    print("\x1b[9mStrike    │ The quick brown fox\x1b[0m")

    # Two-attribute combinations
    s("2. TWO-ATTRIBUTE COMBINATIONS")
    print(
        "\x1b[1;2mBold+Dim\x1b[0m  \x1b[1;3mBold+Italic\x1b[0m  \x1b[1;4mBold+Under\x1b[0m  \x1b[1;7mBold+Reverse\x1b[0m  \x1b[1;9mBold+Strike\x1b[0m"
    )
    print(
        "\x1b[2;3mDim+Italic\x1b[0m  \x1b[2;4mDim+Under\x1b[0m  \x1b[2;7mDim+Reverse\x1b[0m  \x1b[2;9mDim+Strike\x1b[0m"
    )
    print("\x1b[3;4mItalic+Under\x1b[0m  \x1b[3;7mItalic+Reverse\x1b[0m  \x1b[3;9mItalic+Strike\x1b[0m")
    print("\x1b[4;7mUnder+Reverse\x1b[0m  \x1b[4;9mUnder+Strike\x1b[0m  \x1b[7;9mReverse+Strike\x1b[0m")

    # Complex combinations
    s("3. COMPLEX COMBINATIONS")
    print(
        "\x1b[1;3;4mBold+Italic+Under\x1b[0m  \x1b[1;3;7mBold+Italic+Reverse\x1b[0m  \x1b[2;3;4mDim+Italic+Under\x1b[0m"
    )
    print("\x1b[1;2;3;4;7;9mALL SIX: Bold+Dim+Italic+Under+Reverse+Strike\x1b[0m")

    # Colors with attributes
    s("4. COLORS + ATTRIBUTES")
    print("ANSI-16: ", end="")
    for c in [31, 32, 34, 35]:
        print(f"\x1b[{c};1m█\x1b[0m\x1b[{c};2m█\x1b[0m\x1b[{c};4m█\x1b[0m ", end="")
    print()
    print("Bright:  ", end="")
    for c in [91, 92, 94, 95]:
        print(f"\x1b[{c};1m█\x1b[0m\x1b[{c};2m█\x1b[0m\x1b[{c};4m█\x1b[0m ", end="")
    print()
    print("256-col: ", end="")
    for c in [196, 46, 21, 226]:
        print(f"\x1b[38;5;{c};1m██\x1b[0m\x1b[38;5;{c};2m██\x1b[0m ", end="")
    print()
    print("RGB24:   ", end="")
    for r, g, b in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]:
        print(f"\x1b[38;2;{r};{g};{b};1m██\x1b[0m\x1b[38;2;{r};{g};{b};2m██\x1b[0m ", end="")
    print()

    # Dim intensity reduction
    s("5. DIM INTENSITY (50% RGB reduction)")
    print("Normal: ", end="")
    for i in range(0, 256, 32):
        print(f"\x1b[38;2;{i};{i};{i}m██\x1b[0m", end="")
    print("\nDim:    ", end="")
    for i in range(0, 256, 32):
        print(f"\x1b[38;2;{i};{i};{i};2m██\x1b[0m", end="")
    print()

    # SGR resets
    s("6. SGR RESET CODES")
    print("\x1b[1;2;3;4mAll→\x1b[22mSGR22→\x1b[0m (resets bold+dim)")
    print("\x1b[1;3;4mB+I+U→\x1b[23mSGR23→\x1b[0m (resets italic)")
    print("\x1b[1;3;4mB+I+U→\x1b[24mSGR24→\x1b[0m (resets underline)")
    print("\x1b[1;7mBold+Rev→\x1b[27mSGR27→\x1b[0m (resets reverse)")
    print("\x1b[1;9mBold+Strike→\x1b[29mSGR29→\x1b[0m (resets strike)")
    print("\x1b[1;2;3;4;7;9mAll→\x1b[0mSGR0 (resets all)")

    # Reverse video
    s("7. REVERSE VIDEO (color swap)")
    print(
        "\x1b[31;42mRed/Green\x1b[0m→\x1b[31;42;7mReversed\x1b[0m  \x1b[33;44mYellow/Blue\x1b[0m→\x1b[33;44;7mReversed\x1b[0m"
    )
    print("\x1b[31;4mRed+Under\x1b[0m→\x1b[31;4;7mReversed (underline color swaps)\x1b[0m")

    # Wide characters
    s("8. WIDE CHARACTERS (CJK, Emoji)")
    print("\x1b[1m粗体\x1b[0m \x1b[2m暗淡\x1b[0m \x1b[3m斜体\x1b[0m \x1b[4m下划线\x1b[0m \x1b[1;2;3;4m全部\x1b[0m")
    print("\x1b[1m🚀\x1b[0m \x1b[2m🌟\x1b[0m \x1b[4m🎨\x1b[0m \x1b[7m💻\x1b[0m \x1b[9m❌\x1b[0m \x1b[1;2;3;4m🎯\x1b[0m")
    print("\x1b[1mHello 世界\x1b[0m \x1b[2;4mASCII 中文 🌈 mixed\x1b[0m")

    # Attribute boundaries
    s("9. BOUNDARIES & TRANSITIONS")
    print("Normal→\x1b[1mBold\x1b[0m→Normal→\x1b[3mItalic\x1b[0m→Normal→\x1b[4mUnder\x1b[0m→Normal")
    print(
        "\x1b[1mBold \x1b[3m+Italic \x1b[4m+Under \x1b[7m+Rev \x1b[27m-Rev \x1b[24m-Under \x1b[23m-Italic \x1b[22m-Bold"
    )

    # Edge cases
    s("10. EDGE CASES")
    print("\x1b[7m          \x1b[0m← Empty cells reversed")
    print("\x1b[1mBold\x1b[22m→reset\x1b[22m→reset\x1b[22m (idempotent)")
    print("\x1b[1;2;3;4;7;9mAll→\x1b[22;23;24;27;29mMulti-reset in one sequence\x1b[0m")

    # Performance pattern
    s("11. PERFORMANCE PATTERN (dense changes)")
    for i in range(40):
        attr = (i % 6) + 1
        char = chr(65 + (i % 26))
        print(f"\x1b[{attr}m{char}\x1b[0m", end="")
    print()

    # Comparison grid
    s("12. ATTRIBUTE × COLOR GRID")
    attrs = [("Norm", ""), ("Bold", "1"), ("Dim", "2"), ("Ital", "3"), ("Und", "4"), ("Rev", "7")]
    print("      ", end="")
    for name, _ in attrs:
        print(f"{name:6}", end="")
    print()
    for color_name, color_code in [("Red", "31"), ("Grn", "32"), ("Blu", "34"), ("RGB", "38;2;255;0;255")]:
        print(f"{color_name:5} ", end="")
        for _, attr_code in attrs:
            codes = ";".join(filter(None, [color_code, attr_code]))
            if codes:
                print(f"\x1b[{codes}mTest\x1b[0m  ", end="")
            else:
                print("Test  ", end="")
        print()

    print("\n╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║ ✓ All attributes • ✓ Combinations • ✓ Colors • ✓ Resets • ✓ Wide chars    ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝\n")


if __name__ == "__main__":
    main()
