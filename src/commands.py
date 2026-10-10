"""Implementation of shell commands (stage 4: basic commands)."""

import getpass
import stat

from result import Result, fail
from vfs import Directory, VFSError

SESSION_TERMINAL = "console"
START_FORMAT = "%Y-%m-%d %H:%M"
LONG_FLAG = "-l"


def cmd_exit(_shell, args):
    """Finish the emulator."""
    if args:
        return fail("exit: too many arguments")
    return Result(exit=True)


def cmd_conf_dump(shell, args):
    """Print emulator parameters as key=value lines."""
    if args:
        return fail("conf-dump: too many arguments")
    if shell.config is None:
        return Result()
    lines = [f"{key}={value}" for key, value in shell.config.as_dict().items()]
    return Result("\n".join(lines))


def cmd_clear(_shell, args):
    """Ask the interface to erase the screen."""
    if args:
        return fail("clear: too many arguments")
    return Result(clear=True)


def cmd_echo(_shell, args):
    """Print the arguments separated by single spaces."""
    return Result(" ".join(args))


def current_user():
    """Return the name of the real user, or 'user' if it is unknown."""
    try:
        return getpass.getuser()
    except (KeyError, OSError, ImportError):
        return "user"


def cmd_who(shell, args):
    """Print the user, the terminal and the session start time."""
    if args:
        return fail("who: too many arguments")
    started = shell.started.strftime(START_FORMAT)
    return Result(f"{current_user()}  {SESSION_TERMINAL}  {started}")


def describe(name, node, long_format):
    """Format one entry for ls: plain name or a line with permissions."""
    is_dir = isinstance(node, Directory)
    if not long_format:
        return name + "/" if is_dir else name
    kind = stat.S_IFDIR if is_dir else stat.S_IFREG
    mode = stat.filemode(kind | node.mode)
    size = 0 if is_dir else len(node.data)
    return f"{mode} {size:>8} {name}"


def parse_ls_args(args):
    """Split ls arguments into the long flag and a list of paths.

    Returns (long_format, paths, error_message).
    """
    long_format = False
    paths = []
    for arg in args:
        if arg == LONG_FLAG:
            long_format = True
        elif arg.startswith("-") and len(arg) > 1:
            return False, [], f"ls: invalid option '{arg}'"
        else:
            paths.append(arg)
    if len(paths) > 1:
        return False, [], "ls: too many arguments"
    return long_format, paths, ""


def cmd_ls(shell, args):
    """List a directory (or show a file) of the VFS: ls [-l] [path]."""
    long_format, paths, message = parse_ls_args(args)
    if message:
        return fail(message)
    target = paths[0] if paths else "."
    try:
        node = shell.vfs.get(target)
    except VFSError as error:
        return fail(f"ls: {target}: {error}")
    if not isinstance(node, Directory):
        return Result(describe(target, node, long_format))
    items = [describe(name, child, long_format)
             for name, child in sorted(node.children.items())]
    separator = "\n" if long_format else "  "
    return Result(separator.join(items))


def cmd_cd(shell, args):
    """Change the current directory: cd [path]; plain cd goes to '/'."""
    if len(args) > 1:
        return fail("cd: too many arguments")
    target = args[0] if args else "/"
    try:
        shell.vfs.chdir(target)
    except VFSError as error:
        return fail(f"cd: {target}: {error}")
    return Result()


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
    "conf-dump": cmd_conf_dump,
    "clear": cmd_clear,
    "echo": cmd_echo,
    "who": cmd_who,
}
