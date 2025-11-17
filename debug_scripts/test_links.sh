#!/bin/bash
# Test script for hyperlink styling in the TUI

echo "Testing Hyperlink Styling"
echo "========================="
echo ""

echo "1. OSC 8 Hyperlink (should be blue and underlined):"
printf '\e]8;;https://github.com\e\\GitHub\e]8;;\e\\\n'
echo ""

echo "2. Plain URL (should be clickable after detection):"
echo "Visit https://google.com for search"
echo ""

echo "3. Multiple links:"
printf 'Check out \e]8;;https://python.org\e\\Python\e]8;;\e\\ and \e]8;;https://rust-lang.org\e\\Rust\e]8;;\e\\\n'
echo ""

echo "4. FTP link:"
echo "Download from ftp://ftp.example.com/file.txt"
echo ""

echo "5. Email link:"
echo "Contact us at mailto:user@example.com"
echo ""

echo "All hyperlinks should be styled in blue with underline."
echo "Click on any link to open it in your browser!"
