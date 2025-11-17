"""Clipboard operations for terminal widget."""

import sys
from typing import TYPE_CHECKING

from par_term_emu_core_rust.debug import debug_log

if TYPE_CHECKING:
    from par_term_emu_core_rust import PtyTerminal

    from par_term_emu_tui_rust.config import TuiConfig


class ClipboardManager:
    """Manages clipboard operations with cross-platform support."""

    def __init__(
        self,
        term: PtyTerminal,
        config: TuiConfig,
    ) -> None:
        """Initialize clipboard manager.

        Args:
            term: Terminal instance
            config: TUI configuration
        """
        self.term = term
        self.config = config

    def copy_to_clipboard(
        self,
        text: str,
        to_primary: bool = True,
    ) -> tuple[bool, str | None]:
        """Copy text to clipboard using pyperclip (cross-platform).

        Args:
            text: The text to copy
            to_primary: Whether to also copy to PRIMARY selection for middle-click paste
                       (default: True, Linux-only)

        Returns:
            Tuple of (success, error_message). If successful, error_message is None.
        """
        if not text:
            return False, "No text to copy"

        try:
            # Use pyperclip for cross-platform clipboard support
            # This handles Windows (win32clipboard), macOS (pbcopy), and Linux (xclip/xsel)
            import pyperclip

            pyperclip.copy(text)

            # On Linux, also copy to PRIMARY selection for middle-click paste if requested
            if sys.platform == "linux" and to_primary:
                self._copy_to_primary(text)

            return True, None
        except Exception as e:
            return False, str(e)

    def _copy_to_primary(self, text: str) -> None:
        """Copy text to X11 PRIMARY selection (Linux only).

        This is best effort - failures are logged but not raised.

        Args:
            text: Text to copy to PRIMARY selection
        """
        try:
            import subprocess

            # Try xclip first, then xsel
            try:
                subprocess.run(
                    ["xclip", "-selection", "primary"],
                    input=text.encode(),
                    check=True,
                    capture_output=True,
                )
            except FileNotFoundError:
                subprocess.run(
                    ["xsel", "--primary", "--input"],
                    input=text.encode(),
                    check=True,
                    capture_output=True,
                )
        except Exception as e:
            # PRIMARY selection is optional - don't fail if it doesn't work
            debug_log("CLIPBOARD", f"Failed to copy to PRIMARY: {e}")

    async def paste_from_primary(self) -> None:
        """Paste PRIMARY selection content to terminal (for middle-click paste).

        On Linux: Reads from X11 PRIMARY selection (text selected with mouse).
        On macOS/Windows: Pastes from regular clipboard.

        Middle-click paste is immediate without warnings or chunking.
        """
        try:
            if sys.platform == "linux":
                content = self._read_from_primary()
            else:
                content = self._read_from_clipboard()

            if content:
                # Middle click paste typically doesn't warn or chunk
                # It's expected to be small (just selected text)
                self.term.paste(content)
                debug_log(
                    "PASTE",
                    f"Middle-click pasted {len(content)} chars",
                )
        except Exception as e:
            debug_log("PASTE", f"Failed to paste: {e}")

    def _read_from_primary(self) -> str | None:
        """Read from X11 PRIMARY selection (Linux only).

        Returns:
            Content from PRIMARY selection, or None if empty/unavailable
        """
        import subprocess

        try:
            result = subprocess.run(
                ["xclip", "-selection", "primary", "-o"],
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError:
            result = subprocess.run(
                ["xsel", "--primary", "--output"],
                capture_output=True,
                text=True,
                check=True,
            )

        return result.stdout if result.stdout else None

    def _read_from_clipboard(self) -> str | None:
        """Read from system clipboard.

        Returns:
            Content from clipboard, or None if empty
        """
        import pyperclip

        return pyperclip.paste()

    async def paste_from_clipboard(self) -> tuple[bool, str | None]:
        """Paste clipboard content to terminal using pyperclip (cross-platform).

        Respects config settings:
        - paste_warn_size: Returns warning if content exceeds this size
        - paste_chunk_size: Splits paste into chunks if > 0
        - paste_chunk_delay_ms: Delay between chunks

        Returns:
            Tuple of (success, message). Message may be a warning, error, or success message.
        """
        import asyncio

        try:
            # Use pyperclip for cross-platform clipboard access
            import pyperclip

            content = pyperclip.paste()

            if not content:
                return False, "Clipboard is empty"

            content_size = len(content.encode())

            # Build warning if content is very large
            warning = None
            if content_size > self.config.paste_warn_size:
                warning = f"Pasting large content ({content_size:,} bytes)"

            # Check if chunking is enabled
            if self.config.paste_chunk_size > 0:
                # Paste in chunks
                chunk_size = self.config.paste_chunk_size
                delay_ms = self.config.paste_chunk_delay_ms
                total_chunks = (len(content) + chunk_size - 1) // chunk_size

                debug_log(
                    "PASTE",
                    f"Chunked paste: {len(content)} chars in {total_chunks} chunks of {chunk_size}",
                )

                for i in range(0, len(content), chunk_size):
                    chunk = content[i : i + chunk_size]
                    self.term.paste(chunk)

                    # Add delay between chunks (except after last chunk)
                    if i + chunk_size < len(content):
                        await asyncio.sleep(delay_ms / 1000.0)

                message = f"Pasted {len(content)} characters in {total_chunks} chunks"
            else:
                # Paste all at once (default behavior)
                self.term.paste(content)
                # message = "Pasted from clipboard"
                message = ""

            # Return warning if present, otherwise success message
            return True, warning if warning else message

        except Exception as e:
            return False, f"Failed to paste: {e}"
