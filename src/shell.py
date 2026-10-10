"""Command interpreter of the emulator."""

import datetime

from cmdparser import parse_line
from commands import COMMANDS
from result import Result, fail
from vfs import VFS


class Shell:
    """Interpreter that dispatches commands to handlers."""

    def __init__(self, vfs=None, config=None):
        """Create a shell working on the given VFS (default if None)."""
        self.vfs = vfs if vfs is not None else VFS.default()
        self.config = config
        self.started = datetime.datetime.now()

    @property
    def vfs_name(self):
        """Name of the loaded VFS."""
        return self.vfs.name

    def prompt(self):
        """Return the input prompt shown before each command."""
        return f"{self.vfs.name}:{self.vfs.cwd_path()}$ "

    def execute(self, line):
        """Execute one input line and return a Result."""
        name, args = parse_line(line)
        if not name:
            return Result()
        handler = COMMANDS.get(name)
        if handler is None:
            return fail(f"{name}: command not found")
        return handler(self, args)
