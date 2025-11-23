# Handoff Document - par-term-emu-tui-rust

## Current Status

✅ **FIXED** - Mouse hover event regression resolved!

## Solution Summary

**Root Cause**: Textual 6.2.0 introduced a breaking change where widgets must define a `:hover` CSS style to receive hover events. Previously (< 6.2.0), hover events were delivered automatically.

**Fix Applied**: Added `:hover` style to `TerminalWidget.DEFAULT_CSS` (lines 98-101 in `terminal_widget.py`):
```css
/* Enable hover events for mouse tracking (Textual 6.2.0+ requirement) */
TerminalWidget:hover {
    /* No visual change - just enables hover event delivery */
}
```

**Files Modified**:
- `src/par_term_emu_tui_rust/terminal_widget/terminal_widget.py` (lines 98-101)

**Testing**:
- All 63 tests passing ✓
- All quality checks passing (ruff, pyright) ✓
- Ready for user verification

**Reference**: Textual PR [#6132](https://github.com/Textualize/textual/pull/6132) - "The :hover pseudo-class now applies to the first widget under the mouse with a hover style set"

---

## Issue Summary

**Problem**: Mouse hover events (mouse movement without button pressed) stopped working for TUI applications running inside the terminal emulator. Click and drag events still work correctly.

**User Report**: "This was working before. New methods should not be required. I believe the last changes relating to a mouse had to do with triple click drag highlighting."

## Recent Work Completed

### 1. Fixed Theme Color Rendering Issues ✅
- **Problem**: Text colors were too dark in Ghostty terminal compared to iTerm2
- **Root Cause**: Rust backend was returning hardcoded ANSI color values instead of theme palette colors
- **Solution**:
  - Modified `par-term-emu-core-rust/src/python_bindings/pty.rs` to resolve ANSI colors 0-15 using theme palette
  - Created `resolve_fg_color()` and `resolve_bg_color()` helper functions
  - Fixed `iterm2-dark` theme to set `palette[0] = "#000000"` to match background color
- **Files Modified**:
  - `../par-term-emu-core-rust/src/python_bindings/pty.rs` (lines 799-837)
  - `src/par_term_emu_tui_rust/themes.py` (line 361)

### 2. Added Makefile Target ✅
- Added `make install-force` target to `../par-term-emu-core-rust/Makefile` for forcing package reinstallation

## Current Investigation: Mouse Hover Regression

### Symptoms
- **Working**: Mouse clicks, drags, scrolling
- **Not Working**: Hover events (mouse movement without button pressed) in nested TUI apps

### Investigation Findings

1. **Debug Logging Added**:
   - Added debug logs to `on_mouse_move()` handler in `terminal_widget.py` (lines 1559-1568)
   - Logs show: `MOUSE_MOVE`, `MOUSE_HOVER`, `MOUSE_MOVE_SKIP` events
   - **Result**: NO logs appeared when hovering - `on_mouse_move()` is NOT being called at all!

2. **Textual Event System**:
   - Textual's `MouseMove` event exists
   - `on_mouse_move` handler is defined in TerminalWidget
   - During drag operations, mouse move events work (because mouse is "captured")
   - During hover (no button pressed), no events are received

3. **Recent Changes Identified**:
   - Git history shows changes to triple-click line selection around commit `c84b9f1`
   - Changes to `on_mouse_move()` added `SelectionMode.LINE` handling
   - Line 1529: `event.stop()` is called during selection dragging
   - This might be interfering with hover event propagation

### Key Code Locations

**File**: `src/par_term_emu_tui_rust/terminal_widget/terminal_widget.py`

**Lines 1520-1530** - Selection drag handling:
```python
# Update selection end while dragging
if self.selection.selecting:
    # Handle line-based selection extension (triple-click + drag)
    if self.selection.selection_mode == SelectionMode.LINE:
        self.selection.extend_line_selection_to(event.y, self.renderer._frame_snapshot)
    else:
        # Normal character-based selection
        self.selection.end = (event.x, event.y)
    self.refresh()
    event.stop()  # <-- This might be problematic
    return
```

**Lines 1546-1568** - Mouse mode detection and hover event sending:
```python
# Send move events based on mode
if self._mouse_button_state is not None and mouse_mode in ("button", "any"):
    # Dragging - send move event with button code + 32 (motion flag)
    motion_button = self._mouse_button_state + 32
    self._send_mouse_event(motion_button, col, row, pressed=True, modifiers=modifiers)
elif mouse_mode == "any":
    # AnyEvent mode - send motion even without button pressed
    # This should handle hover events
    self._send_mouse_event(35, col, row, pressed=True, modifiers=modifiers)
else:
    debug_log("MOUSE_MOVE_SKIP", f"Not sending: mode={mouse_mode}")
```

## Recommended Next Steps

### Option 1: Check for Event System Changes (Most Likely)
The user states this was working before and recent changes involved triple-click highlighting. The issue is likely NOT that we need new methods, but that something in the event flow broke.

**Action Items**:
1. Check if `on_mouse_move()` is even being registered as an event handler
2. Review the triple-click selection changes in commit `c84b9f1` and earlier
3. Look for any `event.stop()` or `event.prevent_default()` calls that might be blocking hover events
4. Check if the App or parent widgets are intercepting mouse move events

### Option 2: Textual Version Compatibility
Check if a recent Textual version change affected how `on_mouse_move` events are delivered to widgets.

**Action Items**:
1. Current version: `textual>=6.6.0`
2. Check Textual changelog for mouse event behavior changes
3. Verify that custom `on_mouse_move()` handlers are still supported

### Option 3: Widget Event Registration
The fact that NO `on_mouse_move` events arrive during hover (but DO arrive during drag) suggests the event handler might not be properly registered for hover scenarios.

**Action Items**:
1. Check if Textual requires explicit event handler registration
2. Verify the widget is receiving focus correctly
3. Check if there's a difference in event routing between "mouse captured" (drag) and "normal" (hover) modes

## Debug Commands

```bash
# Run with debug logging
make debug-verbose

# Or manually:
DEBUG_LEVEL=3 uv run par-term-emu-tui-rust --debug

# After running and moving mouse, check logs:
grep "MOUSE_MOVE\|MOUSE_HOVER\|MOUSE_MOVE_SKIP" /tmp/par_term_emu_core_rust_debug_rust.log | tail -50

# Test nested TUI:
# Inside terminal, run: python -m textual
# Move mouse over it - hover should trigger visual effects
```

## Files to Review

1. **Terminal Widget**: `src/par_term_emu_tui_rust/terminal_widget/terminal_widget.py`
   - Lines 59: Class definition
   - Lines 1296-1509: Mouse down/up handlers
   - Lines 1510-1570: Mouse move handler (CRITICAL)
   - Lines 1211-1262: `_send_mouse_event()` method

2. **Selection Manager**: `src/par_term_emu_tui_rust/terminal_widget/selection.py`
   - Check `SelectionMode.LINE` handling
   - Check `extend_line_selection_to()` method

3. **App**: `src/par_term_emu_tui_rust/app.py`
   - Check if app-level mouse handlers exist
   - Verify event routing

## Environment

- **Python**: 3.14
- **Textual**: 6.6.0
- **Terminal**: Works in iTerm2 and Ghostty (after color fixes)
- **Platform**: macOS (Darwin 25.1.0)

## Unresolved Issues

1. **Mouse Hover Events Not Working**: Main blocking issue - `on_mouse_move()` not being called during hover
2. **Debug Logs Silent**: No mouse move events logged during hover, suggesting event handler registration issue

## Notes

- DO NOT add `can_hover=True` to the Widget class - this causes `TypeError: Widget.__init_subclass__() got an unexpected keyword argument 'can_hover'`
- The hover logic itself (lines 1556-1563) appears correct - the issue is events not arriving
- User emphasizes this worked before, so look for regressions, not missing features

## References

- **Documentation**: `docs/ARCHITECTURE.md` - Detailed system design
- **Config**: `~/.config/par-term-emu-tui-rust/config.yaml`
- **Debug Logs**: `/tmp/par_term_emu_core_rust_debug_rust.log`
- **Sister Projects**:
  - `../par-term-emu-core-rust` - Rust backend (local dependency)
  - `../par-term` - Full Rust terminal frontend
