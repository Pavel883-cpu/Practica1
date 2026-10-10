"""Tests of command line configuration."""

import unittest

from config import Config, format_debug, parse_args


class ConfigTest(unittest.TestCase):
    """Parameters, names and debug output."""

    def test_parse_all(self):
        """All parameters are read from the command line."""
        config = parse_args(["--vfs", "a/b", "--script", "s.emu"])
        self.assertEqual((config.vfs, config.script), ("a/b", "s.emu"))
        self.assertFalse(config.headless)

    def test_debug_lists_every_parameter(self):
        """Debug output has one line for each parameter."""
        lines = format_debug(Config(vfs="x"))
        self.assertEqual(len(lines), len(Config().as_dict()))
        self.assertIn("[debug] vfs = x", lines)


if __name__ == "__main__":
    unittest.main()
