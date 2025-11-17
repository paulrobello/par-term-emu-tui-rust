# Repository Guidelines

## Project Overview & Structure
- Python Textual TUI that wraps the `par-term-emu-core-rust` backend (local Rust dependency in `../par-term-emu-core-rust`).
- `src/par_term_emu_tui_rust/`: main app (`app.py`), terminal widget and managers, dialogs, widgets, installer, utils.
- `tests/`: `pytest` suite (currently minimal; add new tests here).
- `docs/`: detailed design and usage (`ARCHITECTURE.md`, `CONFIG_REFERENCE.md`, `DEBUG.md`, and others).
- `debug_logs/` and `debug_scripts/`: debugging helpers and captured logs; safe to delete locally.

## Setup, Run & Development Commands
- `uv sync` or `make setup-venv`: create `.venv` and install dependencies (Python 3.14 for development).
- `make run` / `uv run par-term-emu-tui-rust` / `uv run ptr`: run the TUI (requires Rust core; humans only, see Agent notes).
- `make themes`: list available color themes.
- `make fmt`, `make lint`, `make checkall`: format, lint, and type-check; run `make checkall` before committing.
- `uv run pytest [...]`: run all tests or targeted tests.

## Coding Style & Naming
- Python 3.14 syntax, 4-space indentation, 120-column lines, Google-style docstrings.
- Full type hints on public functions and methods; use built-in generics (`list[str]`) and `str | None` unions.
- Use `snake_case` for functions/variables, `PascalCase` for classes, and `SCREAMING_SNAKE_CASE` for constants.
- Prefer `pathlib.Path` for filesystem work and always specify `encoding="utf-8"` for file I/O.

## Testing & Debugging
- Tests live under `tests/` as `test_*.py`; name tests for behavior (for example, `test_terminal_resizes_on_window_change`).
- Default test timeout is 10 seconds; keep tests fast and deterministic.
- Prefer fixing real bugs over weakening tests; understand what any failing test is asserting.
- Use `make debug`, `make debug-verbose`, or `make debug-trace` when diagnosing issues; inspect logs in `/tmp/par_term_emu_core_rust_debug_*.log` and `debug_logs/`.

## Commit & Pull Request Guidelines
- Use Conventional Commit-style messages (for example, `feat(ui): add theme picker`, `fix(build): avoid duplicate include`).
- Each pull request should focus on one logical change set, document rationale, link related issues, and update relevant docs.
- Include screenshots or terminal recordings when changing visual behavior, key bindings, or interaction flows.

## Agent-Specific Instructions
- Do not run interactive TUI commands yourself (for example, `make run`, `make debug*`, `uv run par-term-emu-tui-rust`, `uv run ptr`); ask the user to run them instead.
- For automated scenarios, suggest `--auto-quit` and `--screenshot` flags rather than opening long-running sessions, and let the user execute them.
- When in doubt, prefer describing steps and commands rather than directly exercising the UI.
