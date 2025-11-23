# Demo & Utility Scripts

This directory contains demonstration and utility scripts for the par-term-emu-tui-rust terminal emulator. These scripts are user-facing tools for visual testing, feature demonstrations, and general utilities.

**For development and debugging scripts**, see the `debug_scripts/` directory.

## Overview

These scripts demonstrate terminal emulation features and provide useful utilities:
- **Visual Demos**: Scripts that showcase text rendering and terminal capabilities
- **Utilities**: Tools for displaying graphics and testing protocols

## Requirements

### Python Scripts
```bash
# Ensure dependencies are installed
uv sync
```

### Specific Dependencies
- **display_image_sixel.py**: Requires Pillow (PIL)
  ```bash
  uv add pillow
  ```
- **test_kitty_animation.py**: Requires Pillow (PIL)
  ```bash
  uv add pillow
  ```

## Scripts Reference

### Visual Demonstrations

#### `demo_text_attributes.py`
Comprehensive visual demonstration of all text attributes and SGR codes.

**Purpose**: Showcase the terminal's text rendering capabilities with a compact, visual demo.

**Usage**:
```bash
uv run python scripts/demo_text_attributes.py
```

**Demonstrates**:
- Individual attributes: bold, dim, italic, underline, reverse, strikethrough
- Two-attribute combinations (bold+italic, dim+underline, etc.)
- Complex combinations (3+ attributes)
- Colors with attributes (ANSI-16, bright colors, 256-color, RGB)
- Dim intensity reduction (50% RGB)
- SGR reset codes (22, 23, 24, 27, 29, 0)
- Reverse video (color swapping)
- Wide characters (CJK, emoji) with attributes
- Attribute boundaries and transitions
- Edge cases and performance patterns
- Attribute × color grid comparison

**Output**: Formatted visual display showing all combinations with clear labels and checkmarks.

---

#### `test_control_chars.sh`
Bash script demonstrating VT100 control character functionality.

**Purpose**: Visual test of control characters and DEC Special Graphics.

**Usage**:
```bash
bash scripts/test_control_chars.sh
```

**Demonstrates**:
- VT (Vertical Tab) - cursor movement
- FF (Form Feed) - cursor movement
- SO/SI (Shift Out/Shift In) - DEC Special Graphics character set
- Box-drawing characters using line-drawing glyphs
- Ignored characters (NUL, XON, XOFF, CAN, SUB, DEL)
- ENQ (Enquiry) - answerback transmission

**Output**: Box drawings and text demonstrating control character behavior.

---

### Utilities

#### `display_image_sixel.py`
Utility to convert and display images in Sixel format.

**Purpose**: Display images using the Sixel graphics protocol. Useful for testing Sixel rendering and viewing images in the terminal.

**Dependencies**: Pillow (PIL), optionally img2sixel (libsixel)

**Usage**:
```bash
# Display image with auto-detected terminal size
uv run python scripts/display_image_sixel.py path/to/image.png

# Specify size in terminal characters
uv run python scripts/display_image_sixel.py path/to/image.png -w 80 --height 24

# Adjust scale factor (default: 1.0)
uv run python scripts/display_image_sixel.py path/to/image.png --scale 0.5

# Override cell size (if using custom font metrics)
uv run python scripts/display_image_sixel.py path/to/image.png --cell-px "10x20"

# Force Python implementation (don't use img2sixel)
uv run python scripts/display_image_sixel.py path/to/image.png --no-libsixel
```

**Options**:
- `-w, --width`: Maximum width in terminal characters (default: auto-detect)
- `--height`: Maximum height in terminal characters (default: auto-detect)
- `--scale`: Scale factor applied to detected/specified size (default: 1.0)
- `--cell-px`: Character cell size in pixels as WxH (default: 8x16 or $CELL_SIZE_PX)
- `--no-libsixel`: Force Python implementation even if img2sixel is available

**Features**:
- Automatic terminal size detection
- Preserves aspect ratio when resizing
- Uses img2sixel if available (faster, better quality)
- Falls back to Python implementation
- Supports all common image formats (PNG, JPEG, GIF, etc.)

**Example**:
```bash
# Display the test snake image
uv run python scripts/display_image_sixel.py images/snake.sixel --scale 0.3
```

---

### Protocol Testing

#### `test_kitty_animation.py`
Comprehensive test and demonstration of Kitty graphics protocol animation support.

**Purpose**: Demonstrate animation frame loading, playback control, and timing using the Kitty graphics protocol.

**Dependencies**: Pillow (PIL)

**Usage**:
```bash
uv run python scripts/test_kitty_animation.py
```

**Demonstrates**:
1. **Simple 2-frame animation**: Red/blue color alternation (32×32 pixels)
2. **Multi-frame animation**: 4-color cycle (24×24 pixels, 2 loops)
3. **Animation controls**:
   - Infinite looping (`v=1`)
   - Enable looping (`s=3`)
   - Pause/loading mode (`s=2`)
   - Stop animation (`s=1`)

**Features**:
- Creates solid color PNG frames on the fly
- Sends frames using Kitty protocol (APC escape sequences)
- Demonstrates animation control commands
- Shows proper timing and synchronization

**What to verify**:
- Animation frames are transmitted correctly
- Control commands work (play, pause, stop, loop)
- Frame timing is accurate
- Check debug logs for backend storage

**Protocol Reference**: [Kitty Graphics Protocol - Animation](https://sw.kovidgoyal.net/kitty/graphics-protocol/#animation)

**Note**: This tests the protocol implementation. Frontend rendering integration may vary.

---

## Running All Scripts

To run all demo scripts:

```bash
# Visual demonstrations
uv run python scripts/demo_text_attributes.py
bash scripts/test_control_chars.sh

# Utilities and protocol tests
uv run python scripts/display_image_sixel.py images/snake.sixel --scale 0.3
uv run python scripts/test_kitty_animation.py
```

## Use Cases

### Testing Text Rendering
Run `demo_text_attributes.py` to verify:
- Text attributes render correctly
- Color combinations work
- Wide characters (emoji, CJK) display properly
- SGR codes are handled correctly

### Testing Sixel Support
Use `display_image_sixel.py` to:
- Verify Sixel graphics work in your terminal
- Test image rendering quality
- Check aspect ratio preservation
- Compare img2sixel vs Python implementation

### Testing Kitty Graphics
Run `test_kitty_animation.py` to:
- Verify Kitty protocol support
- Test animation frame handling
- Check timing and control commands
- Validate protocol compliance

### Visual Testing
Use bash scripts for quick visual verification:
- `test_control_chars.sh` - Check box drawing and control characters

## Debugging

For detailed logging during testing:

```bash
# Set debug level
export DEBUG_LEVEL=3

# Run script
uv run python scripts/display_image_sixel.py images/test.png

# View logs
tail -f /tmp/par_term_emu_core_rust_debug_rust.log
tail -f /tmp/par_term_emu_core_rust_debug_python.log
```

See `docs/DEBUG.md` for more information.

## Common Issues

### "No module named 'PIL'"
Install Pillow:
```bash
uv add pillow
```

### "FileNotFoundError" when running scripts
Always run scripts from the project root:
```bash
cd /path/to/par-term-emu-tui-rust
uv run python scripts/script_name.py
```

### Sixel images don't display
- Verify your terminal supports Sixel graphics
- Try with img2sixel installed: `brew install libsixel` (macOS) or `apt install libsixel-bin` (Linux)
- Check debug logs for processing errors

### Kitty animations don't play
- Backend may store animations but frontend rendering may be in progress
- Check debug logs to verify frames are being stored
- Animation playback requires frontend integration

## Development Scripts

For backend testing and debugging tools, see `debug_scripts/README.md`. Those scripts include:
- Backend API testing (Terminal/PtyTerminal)
- Component testing (clipboard, selection, links)
- Low-level graphics protocol debugging
- Scrollback and rendering verification

## Related Documentation

- **Debug Scripts**: `debug_scripts/README.md` - Development and debugging tools
- **Architecture**: `docs/ARCHITECTURE.md` - System design details
- **Features**: `docs/FEATURES.md` - Supported terminal features
- **Debugging**: `docs/DEBUG.md` - Debug logging guide

## Contributing

When adding new demo or utility scripts:

1. **Purpose**: Scripts should be user-facing demos or utilities
2. **Documentation**: Include clear docstrings and usage examples
3. **Testing**: Verify scripts work from project root
4. **Dependencies**: Document any special requirements
5. **Update README**: Add documentation for the new script

For development/debugging scripts, add them to `debug_scripts/` instead.

## License

These scripts are part of par-term-emu-tui-rust and use the same license as the main project.
