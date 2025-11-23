# Debug Scripts

This directory contains debug and development scripts for testing specific features of the par-term-emu-tui-rust terminal emulator. These scripts are used during development to verify individual components and features work correctly.

**Note**: These scripts are intended for development and debugging purposes. For general testing and demonstration scripts, see the `scripts/` directory.

## Overview

Debug scripts are organized by feature area:
- **Word Selection & Characters**: Testing word boundary detection and character classification
- **Clipboard**: Testing clipboard operations and integration
- **Hyperlinks**: Testing hyperlink detection, styling, and OSC 8 protocol
- **Title Management**: Testing terminal title changes via OSC sequences
- **Graphics & Scrollback**: Testing Sixel graphics, scrollback behavior, and rendering calculations

## Requirements

All Python scripts require the project dependencies:
```bash
uv sync
```

Some scripts have additional dependencies:
- `test_clipboard.py`: Requires `pyperclip` (should be installed via uv sync)

## Scripts Reference

### Word Selection & Characters

#### `compare_word_chars.py`
Compare the project's default word_characters configuration with iTerm2's defaults.

**Purpose**: Understand the differences between our word selection behavior and iTerm2's.

**Usage**:
```bash
uv run python debug_scripts/compare_word_chars.py
```

**Output**:
- Shows iTerm2 default: `/-+\~_.`
- Shows our default: `-_.~:/?#[]@!$&'()*+,;=`
- Lists missing characters and extra characters
- Categorizes extra characters (URL/URI, brackets, etc.)

**Use case**: Deciding whether to align with iTerm2 or keep URL-friendly defaults.

---

#### `test_get_word_at.py`
Test the `get_word_at()` API from the Rust backend and SelectionManager integration.

**Purpose**: Verify word boundary detection works correctly with configured word_characters.

**Usage**:
```bash
uv run python debug_scripts/test_get_word_at.py
```

**Tests**:
1. Direct `Terminal.get_word_at()` API calls
2. `SelectionManager.select_word_at()` integration
3. Word selection with hyphens, dots, and URLs

**What to verify**:
- Words are extracted correctly at various cursor positions
- Word boundaries respect configured word_characters
- SelectionManager selects the correct range

---

#### `test_iterm2_word_chars.py`
Test word selection using iTerm2's default word_characters.

**Purpose**: Verify our word selection matches iTerm2 behavior when using their defaults.

**Usage**:
```bash
uv run python debug_scripts/test_iterm2_word_chars.py
```

**Tests word selection with**:
- Hyphens (included in iTerm2 set)
- Dots (included)
- Colons (NOT included - separator)
- Slashes (included)
- Plus signs (included)
- Underscores and tildes (included)
- Backslashes (included)

**Use case**: Ensuring iTerm2 compatibility for users who prefer that behavior.

---

#### `test_word_chars_semantics.py`
Determine whether word_characters are INCLUDED or EXCLUDED from words.

**Purpose**: Clarify the semantics of the word_characters configuration.

**Usage**:
```bash
uv run python debug_scripts/test_word_chars_semantics.py
```

**Tests**:
1. Empty word_characters (all specials are separators)
2. Only hyphen (hyphen included in words)
3. Only dot (dot included in words)
4. iTerm2 default

**Conclusion**: Characters IN word_characters are INCLUDED in word selection. Characters NOT in word_characters are treated as SEPARATORS.

---

### Clipboard

#### `test_clipboard.py`
Test clipboard functionality using pyperclip and ClipboardManager.

**Purpose**: Verify clipboard copy/paste operations work correctly.

**Usage**:
```bash
uv run python debug_scripts/test_clipboard.py
```

**Tests**:
1. Pyperclip import and version
2. Basic copy/paste operations
3. ClipboardManager integration
4. Clipboard content verification

**What to verify**:
- Pyperclip is installed and working
- Copy operations succeed
- Pasted content matches copied content
- ClipboardManager works with terminal integration

**Note**: Requires a clipboard backend (xclip/xsel on Linux, pbcopy/pbpaste on macOS, built-in on Windows)

---

### Hyperlinks

#### `test_hyperlink_styling.py`
Test hyperlink styling with OSC 8 protocol and link colors.

**Purpose**: Verify hyperlinks are detected, stored, and can be styled.

**Usage**:
```bash
uv run python debug_scripts/test_hyperlink_styling.py
```

**Tests**:
1. Setting link color via `set_link_color()`
2. Processing OSC 8 hyperlink sequences
3. Verifying hyperlink_id is set in cell attributes
4. Retrieving URLs via `get_hyperlink()`

**What to verify**:
- Hyperlink IDs are stored in cell attributes
- URLs can be retrieved from the terminal
- Link color is configured correctly

**Note**: This tests backend storage. The TUI renderer applies the styling during display.

---

#### `test_links.sh`
Bash script to visually test hyperlink styling in the terminal.

**Purpose**: Visual verification that hyperlinks display with correct styling.

**Usage**:
```bash
bash debug_scripts/test_links.sh
```

**Displays**:
1. OSC 8 hyperlink (explicit URL with text)
2. Plain URL (auto-detection)
3. Multiple links in one line
4. FTP link
5. Email link (mailto:)

**What to look for**:
- Links are styled in blue with underline
- Clicking links opens them in browser
- Different link types are all detected

**Best for**: Manual visual testing of link styling.

---

### Title Management

#### `test_title_change.sh`
Bash script to test terminal title changes using OSC sequences.

**Purpose**: Visual verification that title changes update the TUI subtitle.

**Usage**:
```bash
bash debug_scripts/test_title_change.sh
```

**Sequences tested**:
- OSC 0 (icon + window title)
- OSC 1 (icon title)
- OSC 2 (window title)

**What to verify**:
- Subtitle updates when titles change
- Different OSC sequences work correctly
- Title persists until changed again

**Note**: Must be run inside the TUI to see subtitle updates.

---

#### `test_title_debug.py`
Debug script to test title changes with Terminal instances.

**Purpose**: Low-level testing of title change detection in the backend.

**Usage**:
```bash
uv run python debug_scripts/test_title_debug.py
```

**Tests**:
1. Direct Terminal.process_str() with OSC sequences
2. Checking Terminal.title() after each change
3. PtyTerminal integration (with shell)
4. Title changes via shell commands

**What to verify**:
- Terminal.title() returns correct value after OSC sequences
- Both Terminal and PtyTerminal handle titles correctly
- Title changes propagate from shell to terminal

**Use case**: Debugging title detection issues.

---

#### `test_title_functionality.py`
Test Terminal.title() method and TitleChanged message integration.

**Purpose**: Unit test for title functionality and message passing.

**Usage**:
```bash
uv run python debug_scripts/test_title_functionality.py
```

**Tests**:
1. Terminal.title() method exists and works
2. OSC 0, OSC 1, OSC 2 sequences update title
3. TitleChanged message class exists
4. TitleChanged message can be instantiated

**What to verify**:
- All title-related APIs are present
- Title updates work for all OSC types
- Message integration is correct

**Best for**: Regression testing after backend changes.

---

### Graphics & Scrollback

#### `test_graphics_scrollback.py`
Test that graphics are preserved during terminal scrolling.

**Purpose**: Verify graphics objects stay visible when scrolling and are removed when scrolled completely off-screen.

**Usage**:
```bash
uv run python debug_scripts/test_graphics_scrollback.py
```

**Tests**:
1. Load graphics (snake.sixel)
2. Simulate scrolling with newlines
3. Verify graphics persist with updated scroll_offset
4. Verify graphics are removed when completely scrolled off

**What to verify**:
- Graphics count remains correct during scrolling
- `scroll_offset_rows` increments as content scrolls
- Graphics are dropped when no longer visible
- Dropped graphics appear in `get_dropped_sixel_graphics()`

**Use case**: Debugging graphics persistence during scrolling operations.

---

#### `test_scrollback_content.py`
Test scrollback with mixed text and graphics content.

**Purpose**: Verify that text content before graphics is preserved in scrollback.

**Usage**:
```bash
uv run python debug_scripts/test_scrollback_content.py
```

**Tests**:
1. Add text lines to terminal
2. Load Sixel graphic
3. Verify scrollback contains the text
4. Verify graphic position and scroll offset

**What to verify**:
- Text lines are preserved in scrollback
- Cursor position is correct after Sixel load
- Graphics position is tracked correctly
- `scrollback_len()` returns expected value

**Use case**: Verifying scrollback buffer handles mixed content correctly.

---

#### `test_scrollback_graphics.py`
Test graphics rendering when viewing scrollback.

**Purpose**: Verify the calculation of which graphics rows should appear when scrolled back in history.

**Usage**:
```bash
uv run python debug_scripts/test_scrollback_graphics.py
```

**Tests**:
1. Add text content
2. Load Sixel graphic
3. Calculate which graphic rows are visible at different scroll positions
4. Verify `graphics_at_row()` returns correct results

**What to verify**:
- Formula for `graphic_virtual_row = scroll_offset - scroll_distance` is correct
- Graphics appear at the right rows when scrolled back
- `graphics_at_row()` works for live terminal view

**Implementation reference**: See `terminal_widget/rendering.py:719` for the rendering formula.

**Use case**: Debugging scrollback rendering calculations.

---

#### `test_sixel_cursor.py`
Test cursor position and scrollback after Sixel load.

**Purpose**: Verify cursor positioning behavior when Sixel graphics are loaded.

**Usage**:
```bash
uv run python debug_scripts/test_sixel_cursor.py
```

**Tests**:
1. Display initial shell prompt
2. Load Sixel graphic
3. Verify cursor position after graphic
4. Add next prompt and verify positioning
5. Display bottom screen rows

**What to verify**:
- Cursor moves to correct position after Sixel
- Scrollback length is updated correctly
- Next prompt appears at expected location
- Screen content is properly laid out

**Use case**: Debugging cursor positioning issues with Sixel graphics.

---

#### `test_sixel_detailed.py`
Detailed Sixel processing test with step-by-step output.

**Purpose**: Understand the complete Sixel loading process including cursor, graphics position, and scrollback state changes.

**Usage**:
```bash
uv run python debug_scripts/test_sixel_detailed.py
```

**Tests**:
1. Initial terminal state
2. Shell prompt output
3. Command echo
4. Sixel data loading (with byte count)
5. Next prompt after graphic
6. Screen content inspection

**What to verify**:
- Cursor position at each step
- Graphics position (column, row)
- Graphics size (pixels and terminal rows)
- `scroll_offset_rows` value
- Scrollback length changes
- Visible screen content

**Best for**: Debugging Sixel loading issues and understanding the complete process.

---

## Running All Debug Scripts

### By Category

**Word Selection**:
```bash
uv run python debug_scripts/compare_word_chars.py
uv run python debug_scripts/test_get_word_at.py
uv run python debug_scripts/test_iterm2_word_chars.py
uv run python debug_scripts/test_word_chars_semantics.py
```

**Clipboard**:
```bash
uv run python debug_scripts/test_clipboard.py
```

**Hyperlinks**:
```bash
uv run python debug_scripts/test_hyperlink_styling.py
bash debug_scripts/test_links.sh  # Must run in TUI
```

**Title Management**:
```bash
uv run python debug_scripts/test_title_functionality.py
uv run python debug_scripts/test_title_debug.py
bash debug_scripts/test_title_change.sh  # Must run in TUI
```

**Graphics & Scrollback**:
```bash
uv run python debug_scripts/test_graphics_scrollback.py
uv run python debug_scripts/test_scrollback_content.py
uv run python debug_scripts/test_scrollback_graphics.py
uv run python debug_scripts/test_sixel_cursor.py
uv run python debug_scripts/test_sixel_detailed.py
```

### All Python Scripts
```bash
for script in debug_scripts/*.py; do
    echo "Running $script..."
    uv run python "$script"
    echo ""
done
```

## Common Workflows

### Debugging Word Selection Issues
1. Run `test_word_chars_semantics.py` to understand inclusion/exclusion
2. Run `compare_word_chars.py` to see iTerm2 differences
3. Run `test_get_word_at.py` to verify API behavior
4. Test in TUI with double-click word selection

### Debugging Clipboard Issues
1. Run `test_clipboard.py` to verify pyperclip works
2. Check for clipboard backend (xclip/xsel on Linux)
3. Test in TUI with Ctrl+Shift+C and Ctrl+Shift+V

### Debugging Hyperlink Issues
1. Run `test_hyperlink_styling.py` to verify backend storage
2. Run `test_links.sh` in TUI to see visual styling
3. Check link color in theme configuration
4. Verify OSC 8 sequences are being processed

### Debugging Title Issues
1. Run `test_title_functionality.py` to verify APIs
2. Run `test_title_debug.py` to test backend processing
3. Run `test_title_change.sh` in TUI to see subtitle updates
4. Check TitleChanged message handler in app.py

### Debugging Graphics & Scrollback Issues
1. Run `test_sixel_detailed.py` for step-by-step Sixel processing
2. Run `test_sixel_cursor.py` to verify cursor positioning
3. Run `test_graphics_scrollback.py` to test scrolling behavior
4. Run `test_scrollback_graphics.py` for rendering calculations
5. Run `test_scrollback_content.py` for mixed content handling
6. Check rendering.py:719 for scrollback rendering formula

## Development Notes

### Adding New Debug Scripts

When adding a new debug script:

1. **Name descriptively**: `test_<feature>.py` or `test_<feature>.sh`
2. **Add docstring**: Explain purpose and usage
3. **Print clear output**: Show what's being tested and results
4. **Use assertions**: For expected behavior (in Python)
5. **Add to this README**: Document the new script

### Script Organization

- **Python scripts**: Test backend APIs and integration
- **Bash scripts**: Visual testing in the TUI
- **Comparison scripts**: Analyze configuration differences

### When to Use Debug Scripts vs Tests

**Use debug scripts when**:
- Testing interactive features (clipboard, links, titles)
- Comparing with other terminal emulators
- Visual verification is needed
- Rapid iteration during development

**Use pytest tests when**:
- Testing pure logic
- Regression testing
- Automated CI/CD
- Unit testing individual components

## Debugging Tips

### Enable Debug Logging
```bash
export DEBUG_LEVEL=3
uv run python debug_scripts/test_<feature>.py
tail -f /tmp/par_term_emu_core_rust_debug_*.log
```

### Test in TUI
Some scripts (marked "Must run in TUI") should be executed inside the terminal:
```bash
# Terminal 1: Start TUI
uv run par-term-emu-tui-rust

# Inside TUI: Run bash script
bash debug_scripts/test_title_change.sh
bash debug_scripts/test_links.sh
```

### Compare with Reference Terminals
Use iTerm2, Alacritty, or WezTerm to compare behavior:
```bash
# In reference terminal
bash debug_scripts/test_links.sh
# Note differences in styling, behavior
```

## Related Documentation

- **Main Scripts**: `scripts/` - Test and demo scripts for general use
- **Tests**: `tests/` - Automated pytest test suite
- **Architecture**: `docs/ARCHITECTURE.md` - System design details
- **Features**: `docs/FEATURES.md` - Implemented features

## Common Issues

### "ModuleNotFoundError: No module named 'pyperclip'"
```bash
uv sync  # Should install all dependencies
```

### "Clipboard operations failed"
**Linux**: Install clipboard backend:
```bash
sudo apt-get install xclip  # or xsel
```

**macOS**: Should work out of the box with pbcopy/pbpaste

### Scripts don't show visual output
Make sure to run bash scripts (`.sh`) inside the TUI for visual verification. Python scripts can run standalone but test backend only.

## Contributing

Debug scripts are development tools. Feel free to:
- Add new scripts for features you're debugging
- Modify existing scripts to test edge cases
- Remove scripts that are no longer relevant

Keep them simple, focused, and well-documented!
