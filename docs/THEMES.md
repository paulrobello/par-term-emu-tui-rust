# Theme System

Complete guide to color themes in par-term-emu-tui-rust, including built-in themes, customization, and creating your own themes.

## Table of Contents
- [Overview](#overview)
- [Using Themes](#using-themes)
  - [Setting a Theme](#setting-a-theme)
  - [Listing Available Themes](#listing-available-themes)
- [Built-in Themes](#built-in-themes)
  - [Dark Themes](#dark-themes)
  - [Light Themes](#light-themes)
  - [Specialty Themes](#specialty-themes)
- [Theme Anatomy](#theme-anatomy)
- [Creating Custom Themes](#creating-custom-themes)
  - [Custom Theme Location](#custom-theme-location)
  - [Theme File Format](#theme-file-format)
  - [Example Custom Theme](#example-custom-theme)
- [Theme Application](#theme-application)
- [Related Documentation](#related-documentation)

## Overview

The theme system provides complete control over terminal colors, including:
- 16 ANSI palette colors (8 standard + 8 bright variants)
- Default background and foreground colors
- Cursor, selection, and UI element colors
- Support for custom user-defined themes

Themes are applied **before the shell starts**, ensuring consistent colors from the first prompt.

## Using Themes

### Setting a Theme

**Via Configuration File:**

Edit `~/.config/par-term-emu-tui-rust/config.yaml`:

```yaml
theme: "iterm2-dark"
```

**Via Command Line:**

```bash
# Use a specific theme for one session
uv run par-term-emu-tui-rust --theme solarized-dark

# Apply theme to config permanently
uv run par-term-emu-tui-rust --apply-theme iterm2-dark
```

### Listing Available Themes

```bash
# List all built-in themes
uv run par-term-emu-tui-rust --list-themes

# Or via make
make themes
```

## Built-in Themes

### Dark Themes

#### iTerm2 Dark (Default)
**Key:** `iterm2-dark`

Classic iTerm2-style color scheme with pure black background. Perfect for OLED displays and users who prefer deep blacks.

- **Background:** `#000000` (Pure black)
- **Foreground:** `#d3d7cf` (Light gray)
- **Palette:** Tango color scheme
- **Best for:** OLED displays, dark environment, maximum contrast

#### Dark Background
**Key:** `dark-background`

Traditional dark terminal with slightly lighter black background.

- **Background:** `#000000` (Black)
- **Foreground:** `#bbbbbb` (Gray)
- **Best for:** General use, compatibility

#### Tango Dark
**Key:** `tango-dark`

Tango color scheme with dark gray background (softer than pure black).

- **Background:** `#2e3436` (Dark gray)
- **Foreground:** `#d3d7cf` (Light gray)
- **Palette:** Official Tango colors
- **Best for:** Reduced eye strain, non-OLED displays

#### Solarized Dark
**Key:** `solarized-dark`

Ethan Schoonover's carefully designed low-contrast dark theme.

- **Background:** `#002b36` (Dark blue-gray)
- **Foreground:** `#839496` (Gray-blue)
- **Best for:** Long coding sessions, color consistency

#### Pastel Dark
**Key:** `pastel-dark`

Soft pastel colors on dark background.

- **Background:** `#000000` (Black)
- **Foreground:** `#bbbbbb` (Gray)
- **Palette:** Muted pastels
- **Best for:** Aesthetic preference, softer visual experience

#### Smoooooth
**Key:** `smoooooth`

Smooth, muted colors optimized for extended use.

- **Background:** `#15191f` (Very dark blue-gray)
- **Foreground:** `#dcdcdc` (Light gray)
- **Best for:** Minimal eye strain, elegant appearance

### Light Themes

#### Light Background
**Key:** `light-background`

Classic light terminal colors.

- **Background:** `#ffffff` (White)
- **Foreground:** `#000000` (Black)
- **Best for:** Bright environments, high ambient light

#### Tango Light
**Key:** `tango-light`

Tango color scheme optimized for light backgrounds.

- **Background:** `#ffffff` (White)
- **Foreground:** `#2e3436` (Dark gray)
- **Best for:** Daytime use, outdoor work

#### Solarized Light
**Key:** `solarized-light`

Light variant of Solarized with the same color relationships.

- **Background:** `#fdf6e3` (Cream)
- **Foreground:** `#657b83` (Blue-gray)
- **Best for:** Consistent colors with Solarized Dark

### Specialty Themes

#### High Contrast
**Key:** `high-contrast`

Maximum contrast for accessibility.

- **Background:** `#000000` (Pure black)
- **Foreground:** `#ffffff` (Pure white)
- **Colors:** Bright, saturated ANSI colors
- **Best for:** Visual accessibility, presentations

#### Regular
**Key:** `regular`

Balanced colors for general terminal use.

- **Background:** `#fafafa` (Very light gray)
- **Foreground:** `#101010` (Very dark gray)
- **Best for:** Moderate contrast preference

#### Solarized
**Key:** `solarized`

Original Solarized base theme.

- **Background:** `#002b36` (Dark blue-gray)
- **Foreground:** `#839496` (Gray-blue)
- **Best for:** Solarized purists

## Theme Anatomy

Each theme consists of these color components:

```yaml
# ANSI Palette (16 colors)
palette:
  - "#2e3436"  # Black (Color 0)
  - "#cc0000"  # Red (Color 1)
  - "#4e9a06"  # Green (Color 2)
  - "#c4a000"  # Yellow (Color 3)
  - "#3465a4"  # Blue (Color 4)
  - "#75507b"  # Magenta (Color 5)
  - "#06989a"  # Cyan (Color 6)
  - "#d3d7cf"  # White (Color 7)
  - "#555753"  # Bright Black (Color 8)
  - "#ef2929"  # Bright Red (Color 9)
  - "#8ae234"  # Bright Green (Color 10)
  - "#fce94f"  # Bright Yellow (Color 11)
  - "#729fcf"  # Bright Blue (Color 12)
  - "#ad7fa8"  # Bright Magenta (Color 13)
  - "#34e2e2"  # Bright Cyan (Color 14)
  - "#eeeeec"  # Bright White (Color 15)

# Default Colors
background: "#000000"      # Default background
foreground: "#d3d7cf"      # Default text color

# Cursor Colors
cursor: "#d3d7cf"          # Cursor color
cursor_text: "#000000"     # Text inside cursor (reverse video)

# Selection Colors
selection: "#eeeeec"       # Selection background
selection_text: "#555753"  # Selected text color

# UI Colors
link: "#729fcf"            # Hyperlink color
bold: "#eeeeec"            # Bold text color override
cursor_guide: "#555753"    # Cursor column guide
underline: "#d3d7cf"       # Underline color override
badge: "#cc0000"           # Badge/notification color
match: "#fce94f"           # Search match highlight
```

## Creating Custom Themes

### Custom Theme Location

Custom themes are stored in:

```
~/.config/par-term-emu-tui-rust/themes/
```

Each theme is a separate YAML file named `{theme-name}.yaml`.

### Theme File Format

Create a YAML file with all required color fields:

```yaml
name: "My Custom Theme"

palette:
  - "#hexcolor"  # 16 colors required (0-15)
  # ... (must have exactly 16 colors)

background: "#hexcolor"
foreground: "#hexcolor"
cursor: "#hexcolor"
cursor_text: "#hexcolor"
selection: "#hexcolor"
selection_text: "#hexcolor"
link: "#hexcolor"
bold: "#hexcolor"
cursor_guide: "#hexcolor"
underline: "#hexcolor"
badge: "#hexcolor"
match: "#hexcolor"
```

### Example Custom Theme

**File:** `~/.config/par-term-emu-tui-rust/themes/nord-inspired.yaml`

```yaml
name: "Nord Inspired"

palette:
  - "#3b4252"  # Black
  - "#bf616a"  # Red
  - "#a3be8c"  # Green
  - "#ebcb8b"  # Yellow
  - "#81a1c1"  # Blue
  - "#b48ead"  # Magenta
  - "#88c0d0"  # Cyan
  - "#e5e9f0"  # White
  - "#4c566a"  # Bright Black
  - "#d08770"  # Bright Red
  - "#a3be8c"  # Bright Green
  - "#ebcb8b"  # Bright Yellow
  - "#81a1c1"  # Bright Blue
  - "#b48ead"  # Bright Magenta
  - "#8fbcbb"  # Bright Cyan
  - "#eceff4"  # Bright White

background: "#2e3440"
foreground: "#d8dee9"
cursor: "#d8dee9"
cursor_text: "#2e3440"
selection: "#4c566a"
selection_text: "#eceff4"
link: "#88c0d0"
bold: "#eceff4"
cursor_guide: "#4c566a"
underline: "#d8dee9"
badge: "#bf616a"
match: "#ebcb8b"
```

**Usage:**

```bash
uv run par-term-emu-tui-rust --theme nord-inspired
```

Or in `config.yaml`:

```yaml
theme: "nord-inspired"
```

## Theme Application

Themes are applied in this order:

```mermaid
graph LR
    A[Create PtyTerminal] --> B[Apply Theme]
    B --> C[Set Renderer Background]
    C --> D[Spawn Shell]
    D --> E[Mount Widget]
    E --> F[Set Widget Background]

    style A fill:#2e3436,stroke:#eeeeec,color:#eeeeec
    style B fill:#4e9a06,stroke:#eeeeec,color:#000000
    style C fill:#4e9a06,stroke:#eeeeec,color:#000000
    style D fill:#3465a4,stroke:#eeeeec,color:#eeeeec
    style E fill:#2e3436,stroke:#eeeeec,color:#eeeeec
    style F fill:#2e3436,stroke:#eeeeec,color:#eeeeec
```

**Key Points:**
- Theme is applied **before shell spawns** (ensures correct colors from first prompt)
- Renderer gets default background for cells without explicit colors
- Widget background is set during mount to match theme

**Cell Background Logic:**
- If cell has non-black background → use cell's color
- If cell has black (`#000000`) and theme has different background → use theme background
- If cell has no background → use theme background

This ensures theme backgrounds work correctly while preserving intentional black backgrounds from applications.

## Related Documentation

- [Configuration Reference](CONFIG_REFERENCE.md) - All configuration options including theme setting
- [Quick Start Guide](QUICK_START.md) - Getting started with the terminal
- [Usage Guide](USAGE.md) - Command-line options and flags
