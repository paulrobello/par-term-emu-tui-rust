#!/bin/bash
# Test script for control character functionality
# Run with: bash test_control_chars.sh

echo "=== Control Character Testing ==="
echo ""

echo "1. Testing VT (Vertical Tab) - should move cursor down like LF"
printf "Line 1\x0BLine 2\x0BLine 3\n"
echo ""

echo "2. Testing FF (Form Feed) - should move cursor down like LF"
printf "Line A\x0CLine B\x0CLine C\n"
echo ""

echo "3. Testing SO/SI (Shift Out/Shift In) - DEC Special Graphics"
echo "Drawing a box with line-drawing characters:"
printf "\x0E"  # SO - activate G1 (DEC Special Graphics)
printf "lqqqqk\n"  # l=top-left, q=horizontal, k=top-right
printf "x    x\n"  # x=vertical
printf "mqqqqj\n"  # m=bottom-left, j=bottom-right
printf "\x0F"  # SI - back to G0 (ASCII)
echo "Back to normal text"
echo ""

echo "4. Testing ignored characters (should not affect output)"
printf "Before\x00\x11\x13\x18\x1A\x7FAfter\n"
echo "(Should see 'BeforeAfter' with no gaps)"
echo ""

echo "5. Testing ENQ (Enquiry) - will transmit answerback if configured"
echo "Note: Answerback requires configuration via backend.configure_answerback()"
echo ""

echo "6. Testing DEC Special Graphics characters:"
printf "\x0E"  # SO - activate G1
echo "Diamond: \`"       # 0x60 -> ◆
echo "Horizontal: qqqqq" # 0x71 -> ─────
echo "Vertical: xxxxx"   # 0x78 -> │││││
echo "Corners: ljmk"     # corners of a box
printf "\x0F"  # SI - back to ASCII
echo ""

echo "=== Tests Complete ==="
