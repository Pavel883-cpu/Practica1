"""Graphical interface of the emulator built on tkinter."""

import tkinter as tk
from tkinter import scrolledtext

FONT = ("Courier", 11)
BACKGROUND = "#1e1e1e"
FOREGROUND = "#d4d4d4"
ERROR_COLOR = "#f48771"
OUTPUT_HEIGHT = 24
OUTPUT_WIDTH = 90


def window_title(vfs_name):
    """Return the window title containing the VFS name."""
    return f"Эмулятор - [{vfs_name}]"


class EmulatorApp:
    """Main window: output area and an input line with a prompt."""

    def __init__(self, root, shell):
        """Build the window for the given tk root and shell."""
        self.root = root
        self.shell = shell
        self.history = []
        self.history_pos = 0
        root.title(window_title(shell.vfs_name))
        self._build_widgets()
        self.entry.focus_set()

    def _build_widgets(self):
        """Create the output area, prompt label and input entry."""
        self.output = scrolledtext.ScrolledText(
            self.root, state="disabled", wrap="word", font=FONT,
            bg=BACKGROUND, fg=FOREGROUND, height=OUTPUT_HEIGHT,
            width=OUTPUT_WIDTH)
        self.output.tag_config("error", foreground=ERROR_COLOR)
        self.output.pack(fill="both", expand=True)
        bar = tk.Frame(self.root, bg=BACKGROUND)
        bar.pack(fill="x")
        self.prompt_var = tk.StringVar(value=self.shell.prompt())
        tk.Label(bar, textvariable=self.prompt_var, font=FONT,
                 bg=BACKGROUND, fg=FOREGROUND).pack(side="left")
        self.entry = tk.Entry(bar, font=FONT, bg=BACKGROUND,
                              fg=FOREGROUND, insertbackground=FOREGROUND,
                              relief="flat")
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Up>", self._on_up)
        self.entry.bind("<Down>", self._on_down)

    def emit(self, text, error=False):
        """Append a line of text to the output area."""
        if not text:
            return
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n", "error" if error else "")
        self.output.see("end")
        self.output.configure(state="disabled")

    def clear(self):
        """Erase everything from the output area."""
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def refresh_prompt(self):
        """Update the prompt label after the state of the shell changed."""
        self.prompt_var.set(self.shell.prompt())

    def submit(self, line):
        """Echo the line, execute it and show the result."""
        self.emit(self.shell.prompt() + line)
        result = self.shell.execute(line)
        if result.clear:
            self.clear()
        self.emit(result.output, result.error)
        self.refresh_prompt()
        if result.exit:
            self.root.destroy()

    def _on_enter(self, _event):
        """Handle the Enter key in the input entry."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        if line.strip():
            self.history.append(line)
        self.history_pos = len(self.history)
        self.submit(line)

    def _show_history(self):
        """Put the history item at the current position into the entry."""
        self.entry.delete(0, "end")
        if self.history_pos < len(self.history):
            self.entry.insert(0, self.history[self.history_pos])

    def _on_up(self, _event):
        """Show the previous command from the input history."""
        if self.history_pos > 0:
            self.history_pos -= 1
            self._show_history()

    def _on_down(self, _event):
        """Show the next command from the input history."""
        if self.history_pos < len(self.history):
            self.history_pos += 1
            self._show_history()
