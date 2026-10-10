"""Tests of startup script execution."""

import os
import tempfile
import unittest

from script import (STATUS_ERROR, STATUS_EXIT, STATUS_OK, ScriptError,
                    read_script, run_script)
from shell import Shell


class FakeUI:
    """Collects emitted lines instead of drawing them."""

    def __init__(self):
        """Start with empty history."""
        self.lines = []
        self.cleared = 0

    def emit(self, text, error=False):
        """Remember a line."""
        if text:
            self.lines.append((text, error))

    def clear(self):
        """Count clear requests."""
        self.cleared += 1


class RunScriptTest(unittest.TestCase):
    """Dialog imitation, comments and stopping on errors."""

    def setUp(self):
        """Create shell and fake ui."""
        self.shell = Shell()
        self.ui = FakeUI()

    def texts(self):
        """Return only the text of emitted lines."""
        return [text for text, _ in self.ui.lines]

    def test_input_and_output_are_shown(self):
        """Each command is echoed with the prompt followed by output."""
        status = run_script(self.shell, ["echo a"], self.ui)
        self.assertEqual(status, STATUS_OK)
        self.assertEqual(self.texts(), ["default:/$ echo a", "a"])

    def test_comments_and_blank_lines_skipped(self):
        """Comments and blank lines produce no output."""
        run_script(self.shell, ["# note", "", "  ", "echo x"], self.ui)
        self.assertEqual(len(self.ui.lines), 2)

    def test_stops_at_first_error(self):
        """Lines after the failed command are not executed."""
        lines = ["ls", "bad", "echo x"]
        self.assertEqual(run_script(self.shell, lines, self.ui),
                         STATUS_ERROR)
        self.assertNotIn("default:/$ echo x", self.texts())
        self.assertIn("script stopped: error in line 2", self.texts())

    def test_exit(self):
        """exit in a script ends it with STATUS_EXIT."""
        self.assertEqual(run_script(self.shell, ["exit", "ls"], self.ui),
                         STATUS_EXIT)

    def test_read_missing_file(self):
        """A missing script file raises ScriptError."""
        with self.assertRaises(ScriptError):
            read_script(os.path.join(tempfile.gettempdir(), "no-such.emu"))


if __name__ == "__main__":
    unittest.main()
