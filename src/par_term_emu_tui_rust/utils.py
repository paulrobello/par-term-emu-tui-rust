"""Utility functions for par-term-emu-tui-rust TUI."""

from __future__ import annotations

import logging
import platform
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def open_with_default_app(file_path: Path | str) -> bool:
    """Open a file with the system's default application.

    Uses the appropriate OS-specific command:
    - macOS: open
    - Linux: xdg-open
    - Windows: start

    Args:
        file_path: Path to the file to open.

    Returns:
        True if the file was successfully opened, False otherwise.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error("Cannot open file: %s does not exist", file_path)
        return False

    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", str(file_path)], check=True, capture_output=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", str(file_path)], check=True, capture_output=True)
        elif system == "Windows":
            subprocess.run(
                ["start", "", str(file_path)],
                shell=True,
                check=True,
                capture_output=True,
            )
        else:
            logger.error("Unsupported platform: %s", system)
            return False

        logger.debug("Opened %s with default application", file_path)
        return True
    except subprocess.CalledProcessError:
        logger.exception("Failed to open %s", file_path)
        return False
    except FileNotFoundError:
        logger.exception("Command not found when trying to open %s", file_path)
        return False
    except Exception:
        logger.exception("Unexpected error opening %s", file_path)
        return False
