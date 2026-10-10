"""Headless mode: the same interface as the window but on stdout."""

import sys

from script import STATUS_ERROR
from startup import startup

EXIT_OK = 0
EXIT_FAILURE = 1


class ConsoleUI:
    """Prints output lines to stdout and errors to stderr."""

    def emit(self, text, error=False):
        """Print a line of text."""
        if not text:
            return
        stream = sys.stderr if error else sys.stdout
        print(text, file=stream)
        stream.flush()

    def clear(self):
        """Clearing is meaningless for a stream, so just mark it."""
        print("[screen cleared]")


def run_headless(shell, config, problems=()):
    """Run the startup sequence once and return a process exit code."""
    status = startup(ConsoleUI(), shell, config, problems)
    return EXIT_FAILURE if status == STATUS_ERROR else EXIT_OK

