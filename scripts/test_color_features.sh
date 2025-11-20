#!/bin/bash
# Test script for 011-color-completion features
# Tests User Story 1 (Underline Color), User Story 2 (Bold Brightening), User Story 3 (Custom Palette)

cat << 'EOF'
========================================
PAR Terminal Color Features Test
========================================

This script tests the three color features:
1. Underline Color (SGR 58/59)
2. Bold Brightening
3. Custom ANSI Palette

Press ENTER after each test to continue...
========================================

EOF

read -p "Press ENTER to start..."

echo ""
echo "=== TEST 1: Underline Color (SGR 58/59) ==="
echo ""
echo "Testing colored underlines with different colors..."
echo ""

# Test 1a: Red underline with blue text
printf "\e[4m\e[34m\e[58;2;255;0;0mRed underline with blue text\e[0m\n"
echo "Expected: Blue text with red underline"
echo ""

# Test 1b: Green underline with default text
printf "\e[4m\e[58;2;0;255;0mGreen underline with default text\e[0m\n"
echo "Expected: Default color text with green underline"
echo ""

# Test 1c: Reset underline color with SGR 59
printf "\e[4m\e[31m\e[58;2;0;255;255mCyan underline, then \e[59mreset to text color\e[0m\n"
echo "Expected: Red text, first part has cyan underline, second part has red underline (matches text)"
echo ""

# Test 1d: Underline color persists when underline toggles
printf "\e[58;2;255;165;0mSet orange underline color, \e[4mthen enable underline\e[0m\n"
echo "Expected: First part no underline, second part has orange underline"
echo ""

read -p "Press ENTER for Test 2..."

echo ""
echo "=== TEST 2: Bold Brightening ==="
echo ""
echo "NOTE: Bold brightening is DISABLED by default."
echo "To enable it, you need to set bold_brightens_colors=True in config"
echo ""

# Test 2a: Normal colors without bold
printf "Normal colors: \e[31mRed\e[0m \e[32mGreen\e[0m \e[33mYellow\e[0m \e[34mBlue\e[0m\n"
echo ""

# Test 2b: Bold colors (without bold brightening, these stay the same hue but bold font)
printf "Bold colors: \e[1m\e[31mBold Red\e[0m \e[1m\e[32mBold Green\e[0m \e[1m\e[33mBold Yellow\e[0m \e[1m\e[34mBold Blue\e[0m\n"
echo "Expected: Same colors as above, but with bold font weight"
echo ""

# Test 2c: Explicit bright colors (these are always bright)
printf "Bright colors: \e[91mBright Red\e[0m \e[92mBright Green\e[0m \e[93mBright Yellow\e[0m \e[94mBright Blue\e[0m\n"
echo "Expected: Noticeably brighter/lighter versions of the colors"
echo ""

echo "To test bold brightening ENABLED:"
echo "1. Create a config file with bold_brightens_colors: true"
echo "2. Load it when starting the terminal"
echo "3. Re-run this script - bold colors will map to bright variants"
echo ""

read -p "Press ENTER for Test 3..."

echo ""
echo "=== TEST 3: Custom ANSI Palette ==="
echo ""
echo "Testing with current palette (iTerm2 defaults unless custom loaded)..."
echo ""

# Test 3a: Display all 16 ANSI colors
printf "Standard colors (0-7):\n"
for i in {0..7}; do
    printf "\e[48;5;${i}m  ${i}  \e[0m "
done
echo ""

printf "Bright colors (8-15):\n"
for i in {8..15}; do
    printf "\e[48;5;${i}m  ${i}  \e[0m "
done
echo ""
echo ""

echo "Current palette:"
printf "\e[30m■\e[0m Black  "
printf "\e[31m■\e[0m Red  "
printf "\e[32m■\e[0m Green  "
printf "\e[33m■\e[0m Yellow  "
printf "\e[34m■\e[0m Blue  "
printf "\e[35m■\e[0m Magenta  "
printf "\e[36m■\e[0m Cyan  "
printf "\e[37m■\e[0m White\n"

printf "\e[90m■\e[0m Br.Black  "
printf "\e[91m■\e[0m Br.Red  "
printf "\e[92m■\e[0m Br.Green  "
printf "\e[93m■\e[0m Br.Yellow  "
printf "\e[94m■\e[0m Br.Blue  "
printf "\e[95m■\e[0m Br.Magenta  "
printf "\e[96m■\e[0m Br.Cyan  "
printf "\e[97m■\e[0m Br.White\n"

echo ""
echo "To test custom palette:"
echo "1. See example config: config/example_palette.yaml"
echo "2. Load it with: config.load_palette_from_yaml(path)"
echo "3. Apply it: config.ansi_colors = palette"
echo "4. Colors above will change to your custom values"
echo ""

read -p "Press ENTER for Test 4 (256-color cube verification)..."

echo ""
echo "=== TEST 4: 256-Color Cube (Unaffected by Custom Palette) ==="
echo ""
echo "Custom palette only affects colors 0-15."
echo "The 256-color cube (16-231) and grayscale (232-255) use formulas."
echo ""

# Test 4a: Sample from 256-color cube
printf "Sample 256-color cube colors (should NOT change with custom palette):\n"
for i in 16 52 88 124 160 196; do
    printf "\e[48;5;${i}m  ${i}  \e[0m "
done
echo ""

# Test 4b: Grayscale ramp
printf "\nGrayscale ramp (232-255, should NOT change with custom palette):\n"
for i in {232..243}; do
    printf "\e[48;5;${i}m ${i} \e[0m"
done
echo ""
echo ""

echo "========================================"
echo "Tests Complete!"
echo "========================================"
echo ""
echo "To run the TUI and test interactively:"
echo "  uv run python -m par_terminal.tui.app"
echo ""
echo "To load a custom palette in Python:"
echo "  from par_terminal.config.terminal_config import TerminalConfig"
echo "  config = TerminalConfig()"
echo "  palette = config.load_palette_from_yaml('config/example_palette.yaml')"
echo "  if palette:"
echo "      config.ansi_colors = palette"
echo ""
EOF
chmod +x test_color_features.sh
