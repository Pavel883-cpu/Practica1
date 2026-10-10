"""Command interpreter of the emulator (stage 3: VFS)."""

from dataclasses import dataclass

from cmdparser import parse_line
from vfs import VFS


@dataclass
class Result:
    """Result of executing one command."""

    output: str = ""
    error: bool = False
    exit: bool = False
    clear: bool = False


class Shell:
    """Interpreter that dispatches commands to handlers."""

    def __init__(self, vfs=None, config=None):
        """Create a shell working on the given VFS (default if None)."""
        self.vfs = vfs if vfs is not None else VFS.default()
        self.config = config
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
            "conf-dump": self.cmd_conf_dump,
        }

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
        handler = self.commands.get(name)
        if handler is None:
            return Result(f"{name}: command not found", error=True)
        return handler(args)

    def cmd_ls(self, args):
        """Stub of ls: prints its name and arguments."""
        return Result(f"ls: args={args}")

    def cmd_cd(self, args):
        """Stub of cd: prints its name and arguments."""
        return Result(f"cd: args={args}")

    def cmd_exit(self, args):
        """Finish the emulator."""
        if args:
            return Result("exit: too many arguments", error=True)
        return Result(exit=True)

    def cmd_conf_dump(self, args):
        """Print emulator parameters as key=value lines."""
        if args:
            return Result("conf-dump: too many arguments", error=True)
        if self.config is None:
            return Result()
        lines = [f"{key}={value}"
                 for key, value in self.config.as_dict().items()]
        return Result("\n".join(lines))
