"""Entry point of the UNIX shell emulator (variant 30)."""

import tkinter as tk

from gui import EmulatorApp
from shell import Shell


def main():
    """Create the shell and the window and run the event loop."""
    root = tk.Tk()
    EmulatorApp(root, Shell())
    root.mainloop()


if __name__ == "__main__":
    main()
