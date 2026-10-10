"""Tests of the shell (stage 1: stubs, errors, exit)."""

import unittest

from shell import Shell


class ShellStubsTest(unittest.TestCase):
    """Stub commands and error handling."""

    def setUp(self):
        """Create a fresh shell."""
        self.shell = Shell()

    def test_stub_prints_name_and_args(self):
        """ls and cd print their name and arguments."""
        self.assertEqual(self.shell.execute("ls a b").output,
                         "ls: args=['a', 'b']")
        self.assertEqual(self.shell.execute("cd x").output,
                         "cd: args=['x']")

    def test_unknown_command(self):
        """An unknown command is an error."""
        result = self.shell.execute("foo")
        self.assertTrue(result.error)
        self.assertIn("command not found", result.output)

    def test_exit(self):
        """exit finishes the emulator, exit with arguments is an error."""
        self.assertTrue(self.shell.execute("exit").exit)
        self.assertTrue(self.shell.execute("exit 1").error)

    def test_empty_line(self):
        """An empty line does nothing."""
        result = self.shell.execute("  ")
        self.assertEqual((result.output, result.error), ("", False))


if __name__ == "__main__":
    unittest.main()
