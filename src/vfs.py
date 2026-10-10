"""Virtual file system kept entirely in memory."""

import os
from dataclasses import dataclass, field

DEFAULT_NAME = "default"
MOTD_NAME = "motd"
FILE_MODE = 0o644
DIR_MODE = 0o755


class VFSError(Exception):
    """An operation on the virtual file system failed."""


@dataclass
class File:
    """A file: binary content and permission bits."""

    data: bytes = b""
    mode: int = FILE_MODE


@dataclass
class Directory:
    """A directory: named children and permission bits."""

    children: dict = field(default_factory=dict)
    mode: int = DIR_MODE


def read_tree(path):
    """Recursively read a real directory into a Directory in memory.

    Symbolic links are skipped. The disk is never modified.
    """
    node = Directory()
    try:
        entries = sorted(os.scandir(path), key=lambda entry: entry.name)
        for entry in entries:
            if entry.is_symlink():
                continue
            if entry.is_dir():
                node.children[entry.name] = read_tree(entry.path)
            elif entry.is_file():
                with open(entry.path, "rb") as handle:
                    node.children[entry.name] = File(handle.read())
    except OSError as error:
        raise VFSError(f"cannot read '{path}': {error.strerror}") from error
    return node


class VFS:
    """An in-memory tree of files and directories with a current dir."""

    def __init__(self, name=DEFAULT_NAME, root=None):
        """Create a VFS with the given name and root directory."""
        self.name = name
        self.root = root if root is not None else Directory()
        self.cwd = []

    @classmethod
    def from_directory(cls, path):
        """Load a VFS from a directory on the disk of the user."""
        if not os.path.exists(path):
            raise VFSError(f"'{path}': no such file or directory")
        if not os.path.isdir(path):
            raise VFSError(f"'{path}': invalid format, not a directory")
        name = os.path.basename(os.path.normpath(path)) or DEFAULT_NAME
        return cls(name, read_tree(path))

    @classmethod
    def default(cls):
        """Create the small VFS used when no path is given."""
        root = Directory()
        root.children["README.txt"] = File(b"Default in-memory VFS.\n")
        root.children["home"] = Directory()
        return cls(DEFAULT_NAME, root)

    def normalize(self, path):
        """Turn a path into a list of components starting from the root.

        Handles absolute and relative paths, '.' and '..'.
        """
        parts = [] if path.startswith("/") else list(self.cwd)
        for part in path.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part not in ("", "."):
                parts.append(part)
        return parts

    def node_at(self, parts):
        """Return the node for a list of components or raise VFSError."""
        node = self.root
        for part in parts:
            if not isinstance(node, Directory) or part not in node.children:
                raise VFSError("no such file or directory")
            node = node.children[part]
        return node

    def get(self, path):
        """Return the node for a path or raise VFSError."""
        return self.node_at(self.normalize(path))

    def chdir(self, path):
        """Make a directory the current one or raise VFSError."""
        parts = self.normalize(path)
        if not isinstance(self.node_at(parts), Directory):
            raise VFSError("not a directory")
        self.cwd = parts

    def cwd_path(self):
        """Return the current directory as an absolute path string."""
        return "/" + "/".join(self.cwd)

    def motd(self):
        """Return the text of the motd file in the root, or an empty str."""
        node = self.root.children.get(MOTD_NAME)
        if not isinstance(node, File):
            return ""
        return node.data.decode("utf-8", errors="replace").rstrip("\n")
