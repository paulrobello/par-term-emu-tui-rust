#!/usr/bin/env python3
"""Test script for custom ANSI palette loading (User Story 3).

This script demonstrates how to:
1. Load a custom palette from YAML
2. Apply it to the terminal configuration
3. Verify the palette was loaded correctly
"""

from pathlib import Path

from par_terminal.config.terminal_config import ITERM2_DEFAULT_ANSI_COLORS, TerminalConfig


def print_palette(colors: list[tuple[int, int, int]], name: str) -> None:
    """Print a color palette in a readable format."""
    print(f"\n{name}:")
    print("=" * 60)

    color_names = [
        "Black",
        "Red",
        "Green",
        "Yellow",
        "Blue",
        "Magenta",
        "Cyan",
        "White",
        "Bright Black",
        "Bright Red",
        "Bright Green",
        "Bright Yellow",
        "Bright Blue",
        "Bright Magenta",
        "Bright Cyan",
        "Bright White",
    ]

    for i, (r, g, b) in enumerate(colors):
        print(f"  {i:2d}. {color_names[i]:15s}  RGB({r:3d}, {g:3d}, {b:3d})  #{r:02X}{g:02X}{b:02X}")


def test_palette_loading() -> None:
    """Test loading custom palettes."""
    print("\n" + "=" * 70)
    print("PAR Terminal - Custom Palette Loading Test")
    print("=" * 70)

    # Create config instance
    config = TerminalConfig()

    # Show default palette
    print_palette(ITERM2_DEFAULT_ANSI_COLORS, "Default iTerm2 Palette")

    # Test 1: Load example palette
    example_path = Path("config/example_palette.yaml")
    if example_path.exists():
        print(f"\n\nTest 1: Loading example palette from {example_path}")
        print("-" * 60)

        palette = config.load_palette_from_yaml(example_path)
        if palette:
            print("✅ Palette loaded successfully!")
            print_palette(palette, "Example Palette")

            # Apply it
            config.ansi_colors = palette
            print("\n✅ Palette applied to config.ansi_colors")
        else:
            print("❌ Failed to load palette")
    else:
        print(f"\n⚠️  Example palette not found at {example_path}")

    # Test 2: Try loading test fixture palette
    test_path = Path("tests/fixtures/palette_configs/valid_palette.yaml")
    if test_path.exists():
        print(f"\n\nTest 2: Loading test fixture palette from {test_path}")
        print("-" * 60)

        palette = config.load_palette_from_yaml(test_path)
        if palette:
            print("✅ Test palette loaded successfully!")
            print_palette(palette, "Test Fixture Palette")
        else:
            print("❌ Failed to load test palette")
    else:
        print(f"\n⚠️  Test palette not found at {test_path}")

    # Test 3: Security checks - world-writable file
    print("\n\nTest 3: Security - World-writable file rejection")
    print("-" * 60)
    import os
    import stat
    import tempfile

    import yaml

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        temp_path = Path(f.name)
        yaml.dump({"ansi_palette": {i: [i * 16, i * 16, i * 16] for i in range(16)}}, f)

    try:
        # Make it world-writable
        os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IWOTH)

        palette = config.load_palette_from_yaml(temp_path)
        if palette is None:
            print("✅ Correctly rejected world-writable file")
        else:
            print("❌ Security failure: world-writable file was accepted!")
    finally:
        temp_path.unlink()

    # Test 4: Invalid RGB values
    print("\n\nTest 4: Validation - Invalid RGB values rejection")
    print("-" * 60)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        temp_path = Path(f.name)
        bad_palette = {"ansi_palette": {i: [i * 16, i * 16, i * 16] for i in range(16)}}
        bad_palette["ansi_palette"][1] = [300, 0, 0]  # Invalid: > 255
        yaml.dump(bad_palette, f)

    try:
        os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)
        palette = config.load_palette_from_yaml(temp_path)
        if palette is None:
            print("✅ Correctly rejected palette with RGB value > 255")
        else:
            print("❌ Validation failure: invalid RGB value was accepted!")
    finally:
        temp_path.unlink()

    # Test 5: Incomplete palette
    print("\n\nTest 5: Validation - Incomplete palette rejection")
    print("-" * 60)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        temp_path = Path(f.name)
        incomplete = {"ansi_palette": {i: [i * 16, i * 16, i * 16] for i in range(10)}}  # Only 10 colors
        yaml.dump(incomplete, f)

    try:
        os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)
        palette = config.load_palette_from_yaml(temp_path)
        if palette is None:
            print("✅ Correctly rejected incomplete palette (10/16 colors)")
        else:
            print("❌ Validation failure: incomplete palette was accepted!")
    finally:
        temp_path.unlink()

    print("\n\n" + "=" * 70)
    print("All Tests Complete!")
    print("=" * 70)
    print("\n💡 How to use custom palettes in your code:")
    print("   1. Create a YAML file with your 16 custom colors")
    print("   2. Load it: palette = config.load_palette_from_yaml(path)")
    print("   3. Apply it: config.ansi_colors = palette")
    print("   4. Start the terminal with this config")
    print("\n📝 Example palette: config/example_palette.yaml")
    print("\n")


if __name__ == "__main__":
    test_palette_loading()
