"""Entry point of the UNIX shell emulator (variant 30)."""

import sys

from config import parse_args
from console import run_headless
from shell import Shell

START_DELAY_MS = 50


def run_gui(shell, config, problems):
    """Open the window and run the startup sequence inside the event loop."""
    import tkinter as tk

    from gui import EmulatorApp

    root = tk.Tk()
    app = EmulatorApp(root, shell)
    root.after(START_DELAY_MS, lambda: app.start(config, problems))
    root.mainloop()
    return 0


def main(argv=None):
    """Parse parameters, create the shell and run the chosen mode."""
    config = parse_args(argv)
    shell = Shell(config.vfs_name(), config)
    problems = []
    if config.headless:
        return run_headless(shell, config, problems)
    return run_gui(shell, config, problems)


if __name__ == "__main__":
    sys.exit(main())
