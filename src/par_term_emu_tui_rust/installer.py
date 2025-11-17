"""
Installation utilities for par-term-emu-tui-rust.

This module provides Python wrappers around the installation scripts
bundled with the package.
"""

import subprocess
import sys
from pathlib import Path
from typing import NoReturn

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def get_scripts_dir() -> Path:
    """Get the path to the bundled installation scripts directory.

    Returns:
        Path to the install_scripts directory.
    """
    return Path(__file__).parent / "install_scripts"


def run_script(script_path: Path, args: list[str] | None = None) -> int:
    """Run a shell script with optional arguments.

    Args:
        script_path: Path to the shell script to execute.
        args: Optional list of arguments to pass to the script.

    Returns:
        Exit code from the script.
    """
    if not script_path.exists():
        console = Console(stderr=True)
        console.print(f"[red]Error: Script not found: {script_path}[/red]")
        return 1

    # Make sure script is executable
    script_path.chmod(0o755)

    # Build command
    cmd = [str(script_path)]
    if args:
        cmd.extend(args)

    # Run script
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        console = Console(stderr=True)
        console.print(f"[red]Error running script: {e}[/red]")
        return 1


def install_terminfo(system_wide: bool = False) -> int:
    """Install par-term terminfo definition.

    Args:
        system_wide: If True, install system-wide (requires sudo).
                    If False, install for current user only.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    console = Console()

    scripts_dir = get_scripts_dir()
    install_script = scripts_dir / "terminfo" / "install.sh"

    args = ["--system"] if system_wide else []

    console.print("\n[bold cyan]Installing par-term terminfo definition...[/bold cyan]\n")

    return run_script(install_script, args)


def install_shell_integration(shell: str | None = None, install_all: bool = False) -> int:
    """Install shell integration for par-term-emu-core-rust.

    Args:
        shell: Specific shell to install for (bash, zsh, fish).
               If None, auto-detects current shell.
        install_all: If True, install for all available shells.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    console = Console()

    scripts_dir = get_scripts_dir()
    install_script = scripts_dir / "shell_integration" / "install.sh"

    args = []
    if install_all:
        args.append("--all")
    elif shell:
        args.append(shell)

    console.print("\n[bold cyan]Installing shell integration...[/bold cyan]\n")

    return run_script(install_script, args)


def install_font() -> int:
    """Install Hack font for screenshot support.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    console = Console()

    scripts_dir = get_scripts_dir()
    install_script = scripts_dir / "font" / "install_font.sh"

    console.print("\n[bold cyan]Installing Hack font for screenshots...[/bold cyan]\n")

    return run_script(install_script, [])


def install_all() -> int:
    """Run all installation steps.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    console = Console()

    console.print(
        Panel.fit(
            "[bold cyan]Running all installation steps for par-term-emu-tui-rust[/bold cyan]",
            border_style="cyan",
        )
    )

    # Install terminfo (user-level)
    console.print("\n[bold]Step 1/3: Installing terminfo[/bold]")
    result = install_terminfo(system_wide=False)
    if result != 0:
        console.print("[red]✗ Terminfo installation failed[/red]")
        return result

    # Install shell integration (auto-detect)
    console.print("\n[bold]Step 2/3: Installing shell integration[/bold]")
    result = install_shell_integration()
    if result != 0:
        console.print("[red]✗ Shell integration installation failed[/red]")
        return result

    # Install font
    console.print("\n[bold]Step 3/3: Installing font[/bold]")
    result = install_font()
    if result != 0:
        console.print("[red]✗ Font installation failed[/red]")
        return result

    console.print(
        Panel.fit(
            "[bold green]✓ All installation steps completed successfully![/bold green]",
            border_style="green",
        )
    )

    return 0


def show_install_help() -> NoReturn:
    """Display help for the install subcommand."""
    console = Console()

    help_text = Text()
    help_text.append("Installation utilities for par-term-emu-tui-rust\n\n", style="bold cyan")
    help_text.append("Usage:\n", style="bold")
    help_text.append("  par-term-emu-tui-rust install <component> [options]\n\n")

    help_text.append("Components:\n", style="bold")
    help_text.append("  all                  Install all components (terminfo, shell-integration, font)\n")
    help_text.append("  terminfo             Install par-term terminfo definition\n")
    help_text.append("  shell-integration    Install shell integration for bash/zsh/fish\n")
    help_text.append("  font                 Install Hack font for screenshot support\n\n")

    help_text.append("Terminfo Options:\n", style="bold")
    help_text.append("  --system             Install system-wide (requires sudo)\n\n")

    help_text.append("Shell Integration Options:\n", style="bold")
    help_text.append("  --all                Install for all available shells\n")
    help_text.append("  bash                 Install for bash only\n")
    help_text.append("  zsh                  Install for zsh only\n")
    help_text.append("  fish                 Install for fish only\n\n")

    help_text.append("Examples:\n", style="bold")
    help_text.append("  # Install everything\n", style="dim")
    help_text.append("  par-term-emu-tui-rust install all\n\n", style="green")

    help_text.append("  # Install terminfo for current user\n", style="dim")
    help_text.append("  par-term-emu-tui-rust install terminfo\n\n", style="green")

    help_text.append("  # Install terminfo system-wide\n", style="dim")
    help_text.append("  sudo par-term-emu-tui-rust install terminfo --system\n\n", style="green")

    help_text.append("  # Install shell integration for current shell\n", style="dim")
    help_text.append("  par-term-emu-tui-rust install shell-integration\n\n", style="green")

    help_text.append("  # Install shell integration for all shells\n", style="dim")
    help_text.append("  par-term-emu-tui-rust install shell-integration --all\n\n", style="green")

    help_text.append("  # Install shell integration for specific shell\n", style="dim")
    help_text.append("  par-term-emu-tui-rust install shell-integration zsh\n\n", style="green")

    help_text.append("  # Install font\n", style="dim")
    help_text.append("  par-term-emu-tui-rust install font\n", style="green")

    console.print(Panel(help_text, border_style="cyan", padding=(1, 2)))
    sys.exit(0)


def handle_install_command(args: list[str]) -> int:
    """Handle the install subcommand.

    Args:
        args: Command-line arguments after 'install'.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    if not args or args[0] in ("--help", "-h"):
        show_install_help()

    component = args[0]
    extra_args = args[1:] if len(args) > 1 else []

    if component == "all":
        return install_all()
    if component == "terminfo":
        system_wide = "--system" in extra_args
        return install_terminfo(system_wide=system_wide)
    if component == "shell-integration":
        install_all_shells = "--all" in extra_args
        shell = None
        if extra_args and extra_args[0] not in ("--all", "--help", "-h"):
            shell = extra_args[0]
        return install_shell_integration(shell=shell, install_all=install_all_shells)
    if component == "font":
        return install_font()
    console = Console(stderr=True)
    console.print(f"[red]Error: Unknown component '{component}'[/red]")
    console.print("Run 'par-term-emu-tui-rust install --help' for usage information.")
    return 1
