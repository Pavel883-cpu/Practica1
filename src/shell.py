"""Command interpreter of the emulator (stage 1: prototype with stubs)."""

from dataclasses import dataclass

from cmdparser import parse_line


@dataclass
class Result:
    """Result of executing one command."""

    output: str = ""
    error: bool = False
    exit: bool = False
    clear: bool = False


class Shell:
    """Interpreter that dispatches commands to handlers."""

    def __init__(self, vfs_name="default"):
        """Create a shell for the VFS with the given name."""
        self.vfs_name = vfs_name
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }

    def prompt(self):
        """Return the input prompt shown before each command."""
        return f"{self.vfs_name}:/$ "

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
