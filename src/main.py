"""Entry point of the UNIX shell emulator (variant 30)."""

import sys

from config import parse_args
from console import run_headless
from shell import Shell
from vfs import VFS, VFSError

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


def load_vfs(config):
    """Load the VFS named in the config.

    Returns (vfs, problems). On a load error the default in-memory VFS
    is used and the error message is returned in problems.
    """
    if not config.vfs:
        return VFS.default(), []
    try:
        return VFS.from_directory(config.vfs), []
    except VFSError as error:
        return VFS.default(), [f"VFS load error: {error}"]


def main(argv=None):
    """Parse parameters, create the shell and run the chosen mode."""
    config = parse_args(argv)
    vfs, problems = load_vfs(config)
    shell = Shell(vfs, config)
    if config.headless:
        return run_headless(shell, config, problems)
    return run_gui(shell, config, problems)


if __name__ == "__main__":
    sys.exit(main())
