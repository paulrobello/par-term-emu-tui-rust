.PHONY: help run install setup-venv clean fmt lint test checkall themes \
        debug debug-verbose debug-trace debug-clear debug-tail debug-view debug-copy-logs \
        pre-commit-install pre-commit-uninstall pre-commit-run pre-commit-update keys borders colors

###############################################################################
# Common make values.
lib     := par-term-emu-tui-rust
run     := uv run
python  := $(run) python
ruff    := $(run) ruff
pyright := $(run) pyright
export PIPENV_VERBOSITY=-1

help:
	@echo "==================================================================="
	@echo "  par-term-emu-tui-rust Makefile"
	@echo "==================================================================="
	@echo ""
	@echo "  Python TUI terminal emulator using Textual"
	@echo ""
	@echo "==================================================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup-venv      - Create virtual environment and install dependencies"
	@echo "  install         - Install all dependencies (requires par-term-emu-core-rust)"
	@echo ""
	@echo "Running:"
	@echo "  run             - Run the interactive TUI"
	@echo "  themes          - List available color themes"
	@echo ""
	@echo "Debugging:"
	@echo "  debug           - Run TUI with DEBUG_LEVEL=2 (info)"
	@echo "  debug-verbose   - Run TUI with DEBUG_LEVEL=3 (debug)"
	@echo "  debug-trace     - Run TUI with DEBUG_LEVEL=4 (trace - WARNING: huge logs)"
	@echo "  debug-clear     - Clear the debug log files"
	@echo "  debug-tail      - Show debug logs in real-time (tail -f)"
	@echo "  debug-view      - View debug logs with less"
	@echo "  debug-copy-logs - Copy debug logs to ./logs directory"
	@echo ""
	@echo "Code Quality:"
	@echo "  fmt             - Format Python code with ruff"
	@echo "  lint            - Run Python linters (format + ruff + pyright, auto-fix)"
	@echo "  test            - Run Python tests with pytest"
	@echo "  checkall        - Run ALL checks: format, lint, typecheck, tests"
	@echo ""
	@echo "Pre-commit Hooks:"
	@echo "  pre-commit-install   - Install pre-commit hooks"
	@echo "  pre-commit-uninstall - Uninstall pre-commit hooks"
	@echo "  pre-commit-run       - Run pre-commit on all files"
	@echo "  pre-commit-update    - Update pre-commit hook versions"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean           - Clean build artifacts and cache"
	@echo ""
	@echo "==================================================================="

# ============================================================================
# Setup & Installation
# ============================================================================

setup-venv:
	@echo "Creating virtual environment and syncing dependencies..."
	uv venv .venv
	uv sync
	@echo ""
	@echo "======================================================================"
	@echo "  Virtual environment created and dependencies synced!"
	@echo "======================================================================"
	@echo ""
	@echo "Then run the TUI:"
	@echo "  make run"
	@echo ""

install:
	@echo "Syncing dependencies..."
	@if [ ! -d ".venv" ]; then \
		echo "Warning: .venv not found. Run 'make setup-venv' first."; \
		exit 1; \
	fi
	uv sync
	@echo ""
	@echo "Dependencies installed!"

# ============================================================================
# Running
# ============================================================================

run: install debug-clear
	@echo "======================================================================"
	@echo "  IMPORTANT WARNING"
	@echo "======================================================================"
	@echo ""
	@echo "Starting TUI..."
	@echo ""
	$(run) $(lib)

themes: install
	@echo "======================================================================"
	@echo "  Available Color Themes"
	@echo "======================================================================"
	@echo ""
	$(run) $(lib) --list-themes

# ============================================================================
# Debugging
# ============================================================================

debug: install debug-clear
	@echo "======================================================================"
	@echo "  Running TUI with DEBUG_LEVEL=2 (INFO)"
	@echo "======================================================================"
	@echo ""
	@echo "  Rust debug output: /tmp/par_term_emu_core_rust_debug_rust.log"
	@echo "  Python debug output: /tmp/par_term_emu_core_rust_debug_python.log"
	@echo "  Python TUI logs: debug_logs/terminal_debug_*.log"
	@echo "  View in another terminal: make debug-tail"
	@echo ""
	@echo "======================================================================"
	@echo ""
	@read -p "Press Enter to continue or Ctrl+C to cancel... " dummy
	@echo ""
	DEBUG_LEVEL=2 $(run) $(lib) --debug

debug-verbose: install debug-clear
	@echo "======================================================================"
	@echo "  Running TUI with DEBUG_LEVEL=3 (DEBUG)"
	@echo "======================================================================"
	@echo ""
	@echo "  Rust debug output: /tmp/par_term_emu_core_rust_debug_rust.log"
	@echo "  Python debug output: /tmp/par_term_emu_core_rust_debug_python.log"
	@echo "  Python TUI logs: debug_logs/terminal_debug_*.log"
	@echo "  View in another terminal: make debug-tail"
	@echo ""
	@echo "======================================================================"
	@echo ""
	@read -p "Press Enter to continue or Ctrl+C to cancel... " dummy
	@echo ""
	DEBUG_LEVEL=3 $(run) $(lib) --debug

debug-trace: install debug-clear
	@echo "======================================================================"
	@echo "  Running TUI with DEBUG_LEVEL=4 (TRACE)"
	@echo "======================================================================"
	@echo ""
	@echo "  Rust debug output: /tmp/par_term_emu_core_rust_debug_rust.log"
	@echo "  Python debug output: /tmp/par_term_emu_core_rust_debug_python.log"
	@echo "  Python TUI logs: debug_logs/terminal_debug_*.log"
	@echo "  View in another terminal: make debug-tail"
	@echo ""
	@echo "  WARNING: This will generate MASSIVE log output (50-100 MB/s)!"
	@echo "  Only use for short debugging sessions."
	@echo ""
	@echo "======================================================================"
	@echo ""
	@read -p "Press Enter to continue or Ctrl+C to cancel... " dummy
	@echo ""
	DEBUG_LEVEL=4 $(run) $(lib) --debug

debug-clear:
	@echo "Clearing debug logs..."
	@rm -f /tmp/par_term_emu_core_rust_debug_rust.log
	@rm -f /tmp/par_term_emu_core_rust_debug_python.log
	@echo "Debug logs cleared:"
	@echo "  - /tmp/par_term_emu_core_rust_debug_rust.log"
	@echo "  - /tmp/par_term_emu_core_rust_debug_python.log"

debug-tail:
	@echo "======================================================================"
	@echo "  Showing debug logs in real-time (Ctrl+C to exit)"
	@echo "======================================================================"
	@echo ""
	@if [ ! -f /tmp/par_term_emu_core_rust_debug_rust.log ] && [ ! -f /tmp/par_term_emu_core_rust_debug_python.log ]; then \
		echo "Debug logs not found. Run a debug target first:"; \
		echo "  make debug"; \
		echo "  make debug-verbose"; \
		echo "  make debug-trace"; \
		exit 1; \
	fi
	@echo "Tailing both Rust and Python logs..."
	@echo ""
	tail -f /tmp/par_term_emu_core_rust_debug_rust.log /tmp/par_term_emu_core_rust_debug_python.log 2>/dev/null || true

debug-view:
	@echo "======================================================================"
	@echo "  Debug Log Viewer"
	@echo "======================================================================"
	@echo ""
	@if [ -f /tmp/par_term_emu_core_rust_debug_rust.log ]; then \
		echo "--- Rust Debug Log ---"; \
		less /tmp/par_term_emu_core_rust_debug_rust.log; \
	fi
	@if [ -f /tmp/par_term_emu_core_rust_debug_python.log ]; then \
		echo "--- Python Debug Log ---"; \
		less /tmp/par_term_emu_core_rust_debug_python.log; \
	fi

# ============================================================================
# Code Quality
# ============================================================================

fmt:
	@echo "Formatting Python code..."
	$(ruff) format .

lint:
	@echo "Running Python linters and auto-fixing issues..."
	$(ruff) format .
	$(ruff) check --fix .
	$(pyright) .

test:
	@echo "Running Python tests with pytest..."
	$(run) pytest tests

checkall: lint test
	@echo ""
	@echo "======================================================================"
	@echo "  All code quality checks passed!"
	@echo "======================================================================"
	@echo ""
	@echo "Summary:"
	@echo "  ✓ Python format (auto-fixed)"
	@echo "  ✓ Python lint (ruff auto-fixed)"
	@echo "  ✓ Python type check (pyright)"
	@echo ""

# ============================================================================
# Pre-commit Hooks
# ============================================================================

pre-commit-install:
	@echo "Installing pre-commit hooks..."
	@if [ ! -d ".venv" ]; then \
		echo "Warning: .venv not found. Run 'make setup-venv' first."; \
		exit 1; \
	fi
	uv sync
	$(run) pre-commit install
	@echo ""
	@echo "======================================================================"
	@echo "  Pre-commit hooks installed successfully!"
	@echo "======================================================================"
	@echo ""
	@echo "Hooks will now run automatically on 'git commit'."
	@echo "To run hooks manually: make pre-commit-run"
	@echo "To skip hooks on commit: git commit --no-verify"
	@echo ""

pre-commit-uninstall:
	@echo "Uninstalling pre-commit hooks..."
	$(run) pre-commit uninstall
	@echo "Pre-commit hooks uninstalled."

pre-commit-run:
	@echo "Running pre-commit on all files..."
	$(run) pre-commit run --all-files

pre-commit-update:
	@echo "Updating pre-commit hook versions..."
	$(run) pre-commit autoupdate
	@echo ""
	@echo "Hook versions updated. Review changes in .pre-commit-config.yaml"

# ============================================================================
# Cleanup
# ============================================================================

clean:
	@echo "Cleaning build artifacts and cache..."
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"


# ============================================================================
# Textual
# ============================================================================

keys:
	$(run) textual keys

borders:
	$(run) textual borders

colors:
	$(run) textual colors
