"""Smoke tests of the window logic with tkinter replaced by mocks."""

import sys
import unittest
from unittest import mock


class GuiTest(unittest.TestCase):
    """EmulatorApp is checked without a display."""

    def setUp(self):
        """Import gui.py with fake tkinter modules."""
        fake = mock.MagicMock()
        patcher = mock.patch.dict(sys.modules, {
            "tkinter": fake, "tkinter.scrolledtext": fake.scrolledtext})
        patcher.start()
        self.addCleanup(patcher.stop)
        sys.modules.pop("gui", None)
        self.addCleanup(sys.modules.pop, "gui", None)
        import gui
        from shell import Shell
        self.gui = gui
        self.root = mock.MagicMock()
        self.app = gui.EmulatorApp(self.root, Shell())

    def test_title_contains_vfs_name(self):
        """The window title shows the VFS name."""
        self.root.title.assert_called_with("Эмулятор - [default]")
        self.assertEqual(self.gui.window_title("x"), "Эмулятор - [x]")

    def test_submit_echoes_and_executes(self):
        """A submitted line is echoed with the prompt and executed."""
        self.app.emit = mock.MagicMock()
        self.app.submit("echo hi")
        calls = [call.args for call in self.app.emit.call_args_list]
        self.assertEqual(calls[0], ("default:/$ echo hi",))
        self.assertEqual(calls[1], ("hi", False))

    def test_exit_closes_window(self):
        """The exit command destroys the window."""
        self.app.submit("exit")
        self.root.destroy.assert_called_once()

    def test_history_navigation(self):
        """Up and Down walk through the entered lines."""
        self.app.entry.get.return_value = "ls"
        self.app._on_enter(None)
        self.app._on_up(None)
        self.app.entry.insert.assert_called_with(0, "ls")


if __name__ == "__main__":
    unittest.main()
