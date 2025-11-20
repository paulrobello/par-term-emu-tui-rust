"""Terminal session recording and management."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from par_term_emu_core_rust.debug import debug_log

if TYPE_CHECKING:
    from par_term_emu_core_rust import PtyTerminal

    from par_term_emu_tui_rust.config import TuiConfig


class RecordingManager:
    """Manages terminal session recording and export."""

    def __init__(self, term: PtyTerminal, config: TuiConfig) -> None:
        """Initialize recording manager.

        Args:
            term: Terminal instance
            config: TUI configuration
        """
        self.term = term
        self.config = config
        self.current_session = None  # Stores session data after stop_recording()

    def is_recording(self) -> bool:
        """Check if terminal is currently recording.

        Returns:
            True if recording is active, False otherwise
        """
        return self.term.is_recording()

    def start(self) -> tuple[bool, str | None]:
        """Start recording terminal session.

        Uses recording_title_template from config, replacing {timestamp} with current time.

        Returns:
            Tuple of (success, error_message). If successful, success is True and
            error_message is None. If failed, success is False and error_message is set.
        """
        try:
            if self.is_recording():
                return False, "Recording already in progress"

            # Generate title from template
            timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
            title = self.config.recording_title_template.replace("{timestamp}", timestamp)

            debug_log("RECORDING", f"Starting recording with title: {title}")
            self.term.start_recording(title=title)
            return True, None

        except Exception as e:
            error_msg = f"Failed to start recording: {e}"
            debug_log("RECORDING", f"Start error: {e}")
            return False, error_msg

    def stop(self) -> tuple[bool, str | None]:
        """Stop recording terminal session.

        Stores session data for later export.

        Returns:
            Tuple of (success, error_message). If successful, success is True and
            error_message is None. If failed, success is False and error_message is set.
        """
        try:
            if not self.is_recording():
                return False, "No recording in progress"

            debug_log("RECORDING", "Stopping recording")
            self.current_session = self.term.stop_recording()

            if self.current_session is None:
                return False, "Failed to stop recording (no session data)"

            return True, None

        except Exception as e:
            error_msg = f"Failed to stop recording: {e}"
            debug_log("RECORDING", f"Stop error: {e}")
            return False, error_msg

    def get_directory(self) -> str:
        """Determine the best directory to save recordings.

        Priority order:
        1. Config recording_directory (if set)
        2. Shell's current working directory (from OSC 7)
        3. XDG_VIDEOS_DIR/Recordings or ~/Videos/Recordings
        4. Home directory

        Returns:
            Path to directory where recording should be saved
        """
        # 1. Check if user configured a specific directory
        if self.config and self.config.recording_directory:
            config_dir = Path(self.config.recording_directory).expanduser()
            if config_dir.is_dir():
                return str(config_dir)
            # Create it if it doesn't exist
            try:
                config_dir.mkdir(parents=True, exist_ok=True)
                return str(config_dir)
            except OSError:
                pass  # Fall through to next option

        # 2. Try to get shell's current working directory from OSC 7
        try:
            shell_state = self.term.shell_integration_state()
            if shell_state.cwd and Path(shell_state.cwd).is_dir():
                debug_log("RECORDING", f"Using shell CWD from OSC 7: {shell_state.cwd}")
                return shell_state.cwd
        except Exception:
            pass  # Fall through to next option

        # 3. Try XDG Videos/Recordings or ~/Videos/Recordings
        # Check XDG_VIDEOS_DIR environment variable first
        xdg_videos = os.environ.get("XDG_VIDEOS_DIR")
        if xdg_videos:
            # XDG_VIDEOS_DIR is set - use it even if directory doesn't exist yet
            recordings_dir = Path(xdg_videos).expanduser() / "Recordings"
            try:
                # Create both XDG_VIDEOS_DIR and Recordings subdirectory if needed
                recordings_dir.mkdir(parents=True, exist_ok=True)
                debug_log("RECORDING", f"Using XDG recordings directory: {recordings_dir}")
                return str(recordings_dir)
            except OSError as e:
                # If we can't create it, log and fall through
                debug_log("RECORDING", f"Failed to create XDG directory {recordings_dir}: {e}")

        # Fall back to ~/Videos/Recordings if XDG not set or failed
        recordings_dir = Path.home() / "Videos" / "Recordings"
        try:
            recordings_dir.mkdir(parents=True, exist_ok=True)
            debug_log("RECORDING", f"Using default recordings directory: {recordings_dir}")
            return str(recordings_dir)
        except OSError as e:
            # Log the error and fall through to final fallback
            debug_log("RECORDING", f"Failed to create default directory {recordings_dir}: {e}")

        # 4. Final fallback: home directory
        home_dir = Path.home()
        debug_log("RECORDING", f"Falling back to home directory: {home_dir}")
        return str(home_dir)

    def export(self) -> tuple[str | None, str | None]:
        """Export the last stopped recording to file.

        Uses configured recording_format (asciicast or json) with timestamp-based filename.

        Returns:
            Tuple of (filepath, error_message). If successful, filepath is set and
            error_message is None. If failed, filepath is None and error_message is set.
        """
        try:
            if self.current_session is None:
                return None, "No recording session to export (recording was not stopped)"

            # Get recording format from config
            recording_format = self.config.recording_format if self.config else "asciicast"

            # Generate filename with timestamp
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            if recording_format == "asciicast":
                extension = "cast"
            elif recording_format == "json":
                extension = "json"
            else:
                return None, f"Unsupported recording format: {recording_format}"

            filename = f"terminal_recording_{timestamp}.{extension}"

            # Determine save directory
            save_dir = self.get_directory()
            filepath = Path(save_dir) / filename

            # Export recording based on format
            if recording_format == "asciicast":
                content = self.term.export_asciicast(session=self.current_session)
            elif recording_format == "json":
                content = self.term.export_json(session=self.current_session)
            else:
                return None, f"Unsupported recording format: {recording_format}"

            # Write to file
            with filepath.open("w", encoding="utf-8") as f:
                f.write(content)

            debug_log("RECORDING", f"Exported recording to {filepath}")
            return str(filepath), None

        except Exception as e:
            error_msg = f"Failed to export recording: {e}"
            debug_log("RECORDING", f"Export error: {e}")
            return None, error_msg

    def toggle(self) -> tuple[bool, str, str | None]:
        """Toggle recording state (start if stopped, stop if started).

        Auto-exports if configured to do so.

        Returns:
            Tuple of (is_now_recording, message, filepath). If recording was started,
            is_now_recording is True and message describes the action. If recording was
            stopped and exported, filepath contains the export path.
        """
        if self.is_recording():
            # Stop recording
            success, error = self.stop()
            if not success:
                return False, f"Error: {error}", None

            # Auto-export if configured
            if self.config.recording_auto_export_on_stop:
                filepath, export_error = self.export()
                if export_error:
                    return False, f"Recording stopped, but export failed: {export_error}", None
                return False, "Recording stopped and saved", filepath
            return False, "Recording stopped (not exported)", None
        # Start recording
        success, error = self.start()
        if not success:
            return True, f"Error: {error}", None
        return True, "Recording started", None

    @staticmethod
    def format_path_for_display(filepath: str) -> str:
        """Format filepath for display, showing relative path if in current directory.

        Args:
            filepath: Absolute path to file

        Returns:
            Relative path if in current directory, otherwise absolute path
        """
        try:
            cwd = Path.cwd()
            file_path = Path(filepath)
            if file_path.is_relative_to(cwd):
                return str(file_path.relative_to(cwd))
            return filepath
        except (ValueError, OSError):
            # Different drives on Windows or other path issues
            return filepath
