"""Tests of the shell: errors, exit, conf-dump and basic commands."""

import unittest

from config import Config
from shell import Shell
from vfs import VFS, Directory, File


def make_shell():
    """Create a shell on a small in-memory VFS: /d/f.txt and /top.txt."""
    root = Directory({
        "d": Directory({"f.txt": File(b"data", 0o600)}),
        "top.txt": File(b"x"),
    })
    return Shell(VFS("t", root), Config(vfs="somewhere"))


class ErrorsTest(unittest.TestCase):
    """Parser level errors and exit."""

    def setUp(self):
        """Create a fresh shell."""
        self.shell = make_shell()

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

    def test_conf_dump(self):
        """conf-dump prints key=value lines."""
        output = self.shell.execute("conf-dump").output
        self.assertIn("vfs=somewhere", output.splitlines())
        self.assertTrue(self.shell.execute("conf-dump x").error)


class LsTest(unittest.TestCase):
    """The ls command."""

    def setUp(self):
        """Create a fresh shell."""
        self.shell = make_shell()

    def test_plain(self):
        """Directories get a slash, entries are sorted."""
        self.assertEqual(self.shell.execute("ls").output, "d/  top.txt")

    def test_path_argument(self):
        """ls lists the directory given by a path."""
        self.assertEqual(self.shell.execute("ls /d").output, "f.txt")

    def test_long_format(self):
        """ls -l shows permissions and size."""
        output = self.shell.execute("ls -l /d").output
        self.assertTrue(output.startswith("-rw-------"))
        self.assertTrue(output.endswith("4 f.txt"))
        self.assertTrue(self.shell.execute("ls -l").output.startswith("drwx"))

    def test_file_argument(self):
        """ls on a file shows that file."""
        self.assertEqual(self.shell.execute("ls top.txt").output, "top.txt")

    def test_errors(self):
        """Missing path, bad option and extra arguments are errors."""
        for line in ("ls /nope", "ls -z", "ls a b"):
            self.assertTrue(self.shell.execute(line).error, line)


class CdTest(unittest.TestCase):
    """The cd command and the prompt."""

    def setUp(self):
        """Create a fresh shell."""
        self.shell = make_shell()

    def test_cd_and_prompt(self):
        """cd changes the directory shown in the prompt."""
        self.assertEqual(self.shell.prompt(), "t:/$ ")
        self.assertFalse(self.shell.execute("cd d").error)
        self.assertEqual(self.shell.prompt(), "t:/d$ ")

    def test_dotdot_and_home(self):
        """.. goes up, plain cd goes to the root."""
        self.shell.execute("cd /d")
        self.shell.execute("cd ..")
        self.assertEqual(self.shell.vfs.cwd_path(), "/")
        self.shell.execute("cd d")
        self.shell.execute("cd")
        self.assertEqual(self.shell.vfs.cwd_path(), "/")

    def test_errors(self):
        """Missing directory, a file and extra arguments are errors."""
        for line in ("cd nope", "cd top.txt", "cd a b"):
            self.assertTrue(self.shell.execute(line).error, line)
        self.assertEqual(self.shell.vfs.cwd_path(), "/")

    def test_relative_ls_after_cd(self):
        """ls works relative to the new current directory."""
        self.shell.execute("cd d")
        self.assertEqual(self.shell.execute("ls").output, "f.txt")


class SimpleCommandsTest(unittest.TestCase):
    """echo, clear and who."""

    def setUp(self):
        """Create a fresh shell."""
        self.shell = make_shell()

    def test_echo(self):
        """echo prints its arguments, with variables expanded."""
        self.assertEqual(self.shell.execute("echo a   b").output, "a b")
        self.assertEqual(self.shell.execute("echo").output, "")

    def test_clear(self):
        """clear asks the interface to erase the screen."""
        self.assertTrue(self.shell.execute("clear").clear)
        self.assertTrue(self.shell.execute("clear x").error)

    def test_who(self):
        """who prints user, terminal and a start time."""
        parts = self.shell.execute("who").output.split("  ")
        self.assertEqual(parts[1], "console")
        self.assertEqual(len(parts), 3)
        self.assertTrue(self.shell.execute("who x").error)


if __name__ == "__main__":
    unittest.main()
