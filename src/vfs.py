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

    def parent_and_name(self, parts):
        """Return the parent directory and the last name of a path."""
        if not parts:
            raise VFSError("operation not permitted on the root directory")
        parent = self.node_at(parts[:-1])
        if not isinstance(parent, Directory):
            raise VFSError("not a directory")
        return parent, parts[-1]

    def lookup_entry(self, parts):
        """Return (parent, name, node) for an existing path."""
        parent, name = self.parent_and_name(parts)
        node = parent.children.get(name)
        if node is None:
            raise VFSError("no such file or directory")
        return parent, name, node

    def contains_cwd(self, parts):
        """Return True if the current directory is at or below the path."""
        return self.cwd[:len(parts)] == parts

    def remove(self, path, recursive=False):
        """Remove a file, or a directory when recursive is True."""
        parts = self.normalize(path)
        parent, name, node = self.lookup_entry(parts)
        if isinstance(node, Directory) and not recursive:
            raise VFSError("is a directory")
        if self.contains_cwd(parts):
            raise VFSError("is the current directory or contains it")
        del parent.children[name]

    def resolve_target(self, source_name, dest_parts):
        """Find where a moved entry goes: (parent, new name, full path).

        An existing directory as destination receives the entry inside.
        """
        try:
            existing = self.node_at(dest_parts)
        except VFSError:
            existing = None
        if isinstance(existing, Directory):
            return existing, source_name, dest_parts + [source_name]
        parent, name = self.parent_and_name(dest_parts)
        return parent, name, dest_parts

    def move(self, source, destination):
        """Move or rename a file or a directory inside the VFS."""
        src_parts = self.normalize(source)
        src_parent, src_name, node = self.lookup_entry(src_parts)
        if self.contains_cwd(src_parts):
            raise VFSError("is the current directory or contains it")
        parent, name, full = self.resolve_target(
            src_name, self.normalize(destination))
        if full == src_parts:
            return
        if full[:len(src_parts)] == src_parts:
            raise VFSError("cannot move a directory into itself")
        existing = parent.children.get(name)
        if existing is not None and Directory in (type(existing), type(node)):
            raise VFSError(f"cannot overwrite '{name}'")
        del src_parent.children[src_name]
        parent.children[name] = node

    def cwd_path(self):
        """Return the current directory as an absolute path string."""
        return "/" + "/".join(self.cwd)

    def motd(self):
        """Return the text of the motd file in the root, or an empty str."""
        node = self.root.children.get(MOTD_NAME)
        if not isinstance(node, File):
            return ""
        return node.data.decode("utf-8", errors="replace").rstrip("\n")
