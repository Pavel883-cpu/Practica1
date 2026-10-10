"""Tests of the input line parser."""

import unittest

from cmdparser import expand_env, parse_line


class ExpandEnvTest(unittest.TestCase):
    """Environment variable expansion."""

    def test_plain_and_braces(self):
        """Both $VAR and ${VAR} forms are expanded."""
        env = {"HOME": "/home/u"}
        self.assertEqual(expand_env("$HOME/a", env), "/home/u/a")
        self.assertEqual(expand_env("${HOME}x", env), "/home/ux")

    def test_unknown_variable_is_empty(self):
        """An unknown variable is replaced by an empty string."""
        self.assertEqual(expand_env("a$NOPE_VAR", {}), "a")


class ParseLineTest(unittest.TestCase):
    """Splitting into command and arguments."""

    def test_split(self):
        """The line is split by whitespace."""
        self.assertEqual(parse_line("ls  -l   /a"), ("ls", ["-l", "/a"]))

    def test_empty_line(self):
        """An empty line gives an empty command."""
        self.assertEqual(parse_line("   "), ("", []))

    def test_expansion_in_arguments(self):
        """Variables in arguments are expanded."""
        self.assertEqual(parse_line("cd $D", {"D": "/x"}), ("cd", ["/x"]))

    def test_empty_expansion_dropped(self):
        """A token that expands to nothing disappears."""
        self.assertEqual(parse_line("ls $NOPE_VAR a", {}), ("ls", ["a"]))


if __name__ == "__main__":
    unittest.main()
