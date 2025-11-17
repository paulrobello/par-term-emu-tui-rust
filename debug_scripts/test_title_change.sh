#!/bin/bash
# Test script to verify terminal title changes work correctly
# This script sets the terminal title using OSC sequences

echo "Testing terminal title changes..."
echo ""

# Function to set terminal title using OSC 0 (icon + window title)
set_title() {
    printf '\033]0;%s\007' "$1"
}

# Function to set window title using OSC 2
set_window_title() {
    printf '\033]2;%s\007' "$1"
}

# Function to set icon title using OSC 1
set_icon_title() {
    printf '\033]1;%s\007' "$1"
}

echo "Step 1: Setting title to 'Test Title 1'"
set_title "Test Title 1"
sleep 2

echo "Step 2: Setting title to 'Hello from Terminal'"
set_title "Hello from Terminal"
sleep 2

echo "Step 3: Setting window title to 'Window Title Test'"
set_window_title "Window Title Test"
sleep 2

echo "Step 4: Setting title to 'Another Title'"
set_title "Another Title"
sleep 2

echo "Step 5: Setting icon title to 'Icon Title'"
set_icon_title "Icon Title"
sleep 2

echo "Step 6: Setting title to 'Final Title'"
set_title "Final Title"
sleep 2

echo ""
echo "Title change test complete!"
echo "You should have seen the subtitle change several times."
echo ""
echo "Press Enter to reset title and continue..."
read -r

# Reset to empty title
printf '\033]0;\007'
