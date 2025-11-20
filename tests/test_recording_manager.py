"""Tests for RecordingManager directory selection and recording functionality."""

from __future__ import annotations

from pathlib import Path

from par_term_emu_tui_rust.config import TuiConfig
from par_term_emu_tui_rust.terminal_widget.recording import RecordingManager


class _DummyTermNoShellState:
    """Dummy terminal that does not provide shell integration state."""

    def __init__(self) -> None:
        self._recording = False
        self._session = None

    def shell_integration_state(self) -> None:
        """Raise to simulate lack of shell integration."""
        msg = "shell integration not available"
        raise RuntimeError(msg)

    def is_recording(self) -> bool:
        """Return recording state."""
        return self._recording

    def start_recording(self, title: str | None = None) -> None:
        """Start recording."""
        self._recording = True

    def stop_recording(self) -> object | None:
        """Stop recording and return session."""
        self._recording = False
        self._session = type("Session", (), {})()
        return self._session

    def export_asciicast(self, session: object | None = None) -> str:
        """Export as asciicast."""
        return '{"version": 2, "width": 80, "height": 24, "timestamp": 1234567890}'

    def export_json(self, session: object | None = None) -> str:
        """Export as JSON."""
        return '{"format": "json", "events": []}'


class _DummyTermWithShellState:
    """Dummy terminal that returns a shell integration state with a CWD."""

    def __init__(self, cwd: Path) -> None:
        self._cwd = cwd
        self._recording = False
        self._session = None

    def shell_integration_state(self) -> object:
        """Return an object with a cwd attribute."""
        return type("ShellState", (), {"cwd": str(self._cwd)})()

    def is_recording(self) -> bool:
        """Return recording state."""
        return self._recording

    def start_recording(self, title: str | None = None) -> None:
        """Start recording."""
        self._recording = True

    def stop_recording(self) -> object | None:
        """Stop recording and return session."""
        self._recording = False
        self._session = type("Session", (), {})()
        return self._session

    def export_asciicast(self, session: object | None = None) -> str:
        """Export as asciicast."""
        return '{"version": 2, "width": 80, "height": 24, "timestamp": 1234567890}'

    def export_json(self, session: object | None = None) -> str:
        """Export as JSON."""
        return '{"format": "json", "events": []}'


def _make_manager(term: object, cfg: TuiConfig) -> RecordingManager:
    """Helper to create a RecordingManager."""
    return RecordingManager(term=term, config=cfg)


def test_get_directory_uses_existing_config_directory(tmp_path: Path) -> None:
    """If recording_directory exists, get_directory should return it."""
    cfg = TuiConfig()
    recording_dir = tmp_path / "recordings"
    recording_dir.mkdir()
    cfg.recording_directory = str(recording_dir)

    mgr = _make_manager(_DummyTermNoShellState(), cfg)
    result = Path(mgr.get_directory())

    assert result == recording_dir
    assert recording_dir.is_dir()


def test_get_directory_creates_missing_config_directory(tmp_path: Path) -> None:
    """If recording_directory does not exist, get_directory should create it."""
    cfg = TuiConfig()
    recording_dir = tmp_path / "recordings-new"
    cfg.recording_directory = str(recording_dir)

    mgr = _make_manager(_DummyTermNoShellState(), cfg)
    result = Path(mgr.get_directory())

    assert result == recording_dir
    assert recording_dir.is_dir()


def test_get_directory_uses_shell_cwd_when_config_not_set(tmp_path: Path) -> None:
    """When no config directory is set, shell CWD from OSC 7 should be used."""
    cfg = TuiConfig()
    cfg.recording_directory = None

    shell_dir = tmp_path / "shell-cwd"
    shell_dir.mkdir()

    mgr = _make_manager(_DummyTermWithShellState(shell_dir), cfg)
    result = mgr.get_directory()

    assert result == str(shell_dir)


def test_format_path_for_display_relative(tmp_path: Path) -> None:
    """format_path_for_display should show relative path when in CWD."""
    import os

    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        file_path = tmp_path / "recording.cast"

        result = RecordingManager.format_path_for_display(str(file_path))

        assert result == "recording.cast"
    finally:
        os.chdir(original_cwd)


def test_format_path_for_display_absolute(tmp_path: Path) -> None:
    """format_path_for_display should show absolute path when not in CWD."""
    file_path = tmp_path / "recording.cast"

    result = RecordingManager.format_path_for_display(str(file_path))

    assert str(file_path) in result


def test_is_recording_initial_state() -> None:
    """is_recording should return False initially."""
    cfg = TuiConfig()
    mgr = _make_manager(_DummyTermNoShellState(), cfg)

    assert not mgr.is_recording()


def test_start_recording_success() -> None:
    """start should return success when recording starts."""
    cfg = TuiConfig()
    cfg.recording_title_template = "Test {timestamp}"
    mgr = _make_manager(_DummyTermNoShellState(), cfg)

    success, error = mgr.start()

    assert success
    assert error is None
    assert mgr.is_recording()


def test_start_recording_when_already_recording() -> None:
    """start should fail when already recording."""
    cfg = TuiConfig()
    term = _DummyTermNoShellState()
    mgr = _make_manager(term, cfg)

    # Start first time
    mgr.start()

    # Try to start again
    success, error = mgr.start()

    assert not success
    assert error == "Recording already in progress"


def test_stop_recording_success() -> None:
    """stop should return success when recording stops."""
    cfg = TuiConfig()
    term = _DummyTermNoShellState()
    mgr = _make_manager(term, cfg)

    # Start recording first
    mgr.start()

    # Stop recording
    success, error = mgr.stop()

    assert success
    assert error is None
    assert not mgr.is_recording()


def test_stop_recording_when_not_recording() -> None:
    """stop should fail when not recording."""
    cfg = TuiConfig()
    mgr = _make_manager(_DummyTermNoShellState(), cfg)

    success, error = mgr.stop()

    assert not success
    assert error == "No recording in progress"


def test_export_asciicast_format(tmp_path: Path) -> None:
    """export should create asciicast file with correct extension."""
    cfg = TuiConfig()
    cfg.recording_directory = str(tmp_path)
    cfg.recording_format = "asciicast"
    term = _DummyTermNoShellState()
    mgr = _make_manager(term, cfg)

    # Start and stop recording
    mgr.start()
    mgr.stop()

    # Export
    filepath, error = mgr.export()

    assert filepath is not None
    assert error is None
    assert filepath.endswith(".cast")
    assert Path(filepath).exists()


def test_export_json_format(tmp_path: Path) -> None:
    """export should create JSON file with correct extension."""
    cfg = TuiConfig()
    cfg.recording_directory = str(tmp_path)
    cfg.recording_format = "json"
    term = _DummyTermNoShellState()
    mgr = _make_manager(term, cfg)

    # Start and stop recording
    mgr.start()
    mgr.stop()

    # Export
    filepath, error = mgr.export()

    assert filepath is not None
    assert error is None
    assert filepath.endswith(".json")
    assert Path(filepath).exists()


def test_export_without_session() -> None:
    """export should fail when no session exists."""
    cfg = TuiConfig()
    mgr = _make_manager(_DummyTermNoShellState(), cfg)

    filepath, error = mgr.export()

    assert filepath is None
    assert error == "No recording session to export (recording was not stopped)"


def test_toggle_starts_recording() -> None:
    """toggle should start recording when not recording."""
    cfg = TuiConfig()
    mgr = _make_manager(_DummyTermNoShellState(), cfg)

    is_recording, message, filepath = mgr.toggle()

    assert is_recording
    assert message == "Recording started"
    assert filepath is None


def test_toggle_stops_and_exports_recording(tmp_path: Path) -> None:
    """toggle should stop and export recording when recording is active."""
    cfg = TuiConfig()
    cfg.recording_directory = str(tmp_path)
    cfg.recording_auto_export_on_stop = True
    cfg.recording_format = "asciicast"
    term = _DummyTermNoShellState()
    mgr = _make_manager(term, cfg)

    # Start recording
    mgr.toggle()

    # Stop recording (second toggle)
    is_recording, message, filepath = mgr.toggle()

    assert not is_recording
    assert message == "Recording stopped and saved"
    assert filepath is not None
    assert filepath.endswith(".cast")


def test_toggle_stops_without_export_when_disabled(tmp_path: Path) -> None:
    """toggle should stop but not export when auto_export_on_stop is False."""
    cfg = TuiConfig()
    cfg.recording_directory = str(tmp_path)
    cfg.recording_auto_export_on_stop = False
    term = _DummyTermNoShellState()
    mgr = _make_manager(term, cfg)

    # Start recording
    mgr.toggle()

    # Stop recording (second toggle)
    is_recording, message, filepath = mgr.toggle()

    assert not is_recording
    assert message == "Recording stopped (not exported)"
    assert filepath is None
